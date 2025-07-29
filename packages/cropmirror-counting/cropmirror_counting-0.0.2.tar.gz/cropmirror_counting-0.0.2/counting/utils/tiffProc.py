'''
2025-07-01 创建文件，用于处理GeoTIFF文件

2025-07-01 JPEG压缩的限制是65535像素，如果图像尺寸超过这个限制，使用DEFLATE压缩
'''
import os
from osgeo import gdal, osr, gdalconst
# import gdal
import fiona
from shapely.geometry import shape, Point, mapping
from collections import defaultdict
import json
from datetime import datetime
from rtree import index  # 用于空间索引加速查询
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import chardet
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

# 导入高精度坐标系统转换工具
from .wmct2wgs84 import (
    get_recommended_projection, 
    convert_point, 
    convert_polygon,
    WGS84_to_CGCS2000_3degree,
    CGCS2000_3degree_to_WGS84,
    COORDINATE_SYSTEMS
)

def detect_encoding(shp_path):
    if not os.path.exists(shp_path.replace('.shp', '.dbf')):
        return 'utf-8'  # 默认编码
    with open(shp_path.replace('.shp', '.dbf'), 'rb') as f:
        rawdata = f.read(1000)  # 读取dbf文件头部
    return chardet.detect(rawdata)['encoding']

def run_yolo_detection(image_path, model_path, results_dir, detection_jpg_name):
    """运行YOLO检测并返回结果列表"""
    
    detection_model = AutoDetectionModel.from_pretrained(
        model_type='ultralytics',
        model_path=model_path,
        confidence_threshold=0.3,
        device='cuda:0',
    )
    
    slice_result = get_sliced_prediction(
        image_path,
        detection_model,
        slice_height=1280,
        slice_width=1280,
        overlap_height_ratio=0.05,
        overlap_width_ratio=0.05,
        verbose=2
    )
    
    slice_result.export_visuals(export_dir=results_dir, hide_labels=True, hide_conf=True, file_name=detection_jpg_name, text_size=1.0, rect_th=2, export_format="jpg")
    return slice_result.to_coco_predictions()

def build_spatial_index(shp_path):
    """空间索引构建函数"""
    # 创建RTree索引
    idx = index.Index()
    parcel_shapes = []
    parcel_properties = []
    
    encoding = detect_encoding(shp_path)
    with fiona.open(shp_path, encoding=encoding) as parcels:
        for i, parcel in enumerate(parcels):
            geom = shape(parcel['geometry'])
            parcel_shapes.append(geom)
            parcel_properties.append(parcel['properties'])
            
            # 插入索引，i是记录ID，geom.bounds是边界框
            idx.insert(i, geom.bounds)
    
    return idx, parcel_shapes, parcel_properties

def process_detections_without_plots(detection_list, geotiff_path, results_dir):
    """
    处理没有地块文件的情况
    """
    print("没有找到地块文件，跳过地块关联处理...")
    start_time = datetime.now()
    
    # 1. 加载GeoTIFF地理信息
    ds = gdal.Open(geotiff_path)
    transform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    ds = None
    
    # 2. 初始化统计和Shapefile写入
    base_name = os.path.splitext(os.path.basename(geotiff_path))[0]
    detected_objs_shp_path = os.path.join(results_dir, f"{base_name}_pts.shp")
    total_count = len(detection_list)
    
    # 准备Shapefile写入
    schema = {
        'geometry': 'Point',
        'properties': {
            'id': 'int',
            'category': 'str',
            'score': 'float'
        }
    }
    
    # 3. 主处理循环
    with fiona.open(
        detected_objs_shp_path, 'w',
        driver='ESRI Shapefile',
        schema=schema,
        crs=projection,
        encoding='utf-8'
    ) as output_shp:
        
        for det_idx, item in enumerate(detection_list):
            # 4.1 计算地理坐标
            bbox = item['bbox']
            x_center = bbox[0] + bbox[2]/2
            y_center = bbox[1] + bbox[3]/2
            geo_x, geo_y = pixel_to_geo(x_center, y_center, transform)
            item['WGS84_EPSG_4326'] = [geo_x, geo_y]
            
            # 4.1.1 转换到高精度CGCS2000坐标系统
            try:
                cgcs2000_coords, used_epsg = WGS84_to_CGCS2000_3degree([geo_x, geo_y])
                item['CGCS2000_coords'] = cgcs2000_coords
                item['CGCS2000_epsg'] = used_epsg
                item['coordinate_system'] = COORDINATE_SYSTEMS.get(used_epsg, used_epsg)
            except Exception as e:
                print(f"坐标转换失败: {e}")
                item['CGCS2000_coords'] = None
                item['CGCS2000_epsg'] = None
            
            # 4.3 写入Shapefile
            output_shp.write({
                'geometry': mapping(Point(geo_x, geo_y)),
                'properties': {
                    'id': det_idx,
                    'category': item['category_name'],
                    'score': item['score']
                }
            })
    
    end_time = datetime.now()
    print(f"处理完成，耗时: {end_time - start_time}")
    
    return detection_list, {'total': len(detection_list)}

def process_detections_optimized(detection_list, geotiff_path, plots_shp_path, results_dir):
    """
    优化版处理流程：
    1. 计算地理坐标
    2. 使用空间索引确定所属地块
    3. 统计地块计数
    4. 创建检测点Shapefile
    """
    print("开始处理检测结果...")
    start_time = datetime.now()
    
    # 1. 加载GeoTIFF地理信息
    ds = gdal.Open(geotiff_path)
    transform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    ds = None
    
    # 2. 构建空间索引
    print("构建地块空间索引...")
    rtree_idx, parcel_shapes, parcel_properties = build_spatial_index(plots_shp_path)
    
    # 3. 初始化统计和Shapefile写入
    base_name = os.path.splitext(os.path.basename(geotiff_path))[0]
    detected_objs_shp_path = os.path.join(results_dir, f"{base_name}_pts.shp")
    
    parcel_counts = defaultdict(int)
    processed_count = 0
    total_count = len(detection_list)
    
    # 准备Shapefile写入 (增强版schema支持CGCS2000坐标)
    schema = {
        'geometry': 'Point',
        'properties': {
            'id': 'int',
            'category': 'str',
            'score': 'float',
            'parcel_id': 'str',
            'cgcs2000_x': 'float',
            'cgcs2000_y': 'float',
            'epsg_code': 'str',
            'coord_sys': 'str'
        }
    }
    
    # 4. 主处理循环
    with fiona.open(
        detected_objs_shp_path, 'w',
        driver='ESRI Shapefile',
        schema=schema,
        crs=projection,
        encoding='utf-8'
    ) as output_shp:
        
        for det_idx, item in enumerate(detection_list):
            # 进度报告
            processed_count += 1
            if processed_count % 1000 == 0:
                print(f"已处理 {processed_count}/{total_count} 个检测目标...")
            
            # 4.1 计算地理坐标
            bbox = item['bbox']
            x_center = bbox[0] + bbox[2]/2
            y_center = bbox[1] + bbox[3]/2
            geo_x, geo_y = pixel_to_geo(x_center, y_center, transform)
            item['WGS84_EPSG_4326'] = [geo_x, geo_y]
            
            # 4.1.1 转换到高精度CGCS2000坐标系统
            try:
                cgcs2000_coords, used_epsg = WGS84_to_CGCS2000_3degree([geo_x, geo_y])
                item['CGCS2000_coords'] = cgcs2000_coords
                item['CGCS2000_epsg'] = used_epsg
                item['coordinate_system'] = COORDINATE_SYSTEMS.get(used_epsg, used_epsg)
            except Exception as e:
                print(f"坐标转换失败: {e}")
                item['CGCS2000_coords'] = None
                item['CGCS2000_epsg'] = None
            
            # 4.2 使用空间索引确定所属地块
            point = Point(geo_x, geo_y)
            parcel_id = None
            
            # 先查询可能包含此点的地块
            possible_parcels = list(rtree_idx.intersection((geo_x, geo_y, geo_x, geo_y)))
            
            # 精确检查这些地块
            for i in possible_parcels:
                if point.within(parcel_shapes[i]):
                    parcel_id = parcel_properties[i].get('name', f"parcel_{i}")
                    item['parcel_id'] = parcel_id
                    parcel_counts[parcel_id] += 1
                    break
            
            # 4.3 写入Shapefile (包含CGCS2000坐标信息)
            properties = {
                    'id': det_idx,
                    'category': item['category_name'],
                    'score': item['score'],
                    'parcel_id': parcel_id if parcel_id else ''
                }
            
            # 添加CGCS2000坐标信息
            if item.get('CGCS2000_coords'):
                properties['cgcs2000_x'] = item['CGCS2000_coords'][0]
                properties['cgcs2000_y'] = item['CGCS2000_coords'][1]
                properties['epsg_code'] = item.get('CGCS2000_epsg', '')
                properties['coord_sys'] = item.get('coordinate_system', '')
            else:
                properties['cgcs2000_x'] = None
                properties['cgcs2000_y'] = None
                properties['epsg_code'] = ''
                properties['coord_sys'] = ''
            
            output_shp.write({
                'geometry': mapping(point),
                'properties': properties
            })
    
    end_time = datetime.now()
    print(f"处理完成，耗时: {end_time - start_time}")
    
    return detection_list, dict(parcel_counts)

def pixel_to_geo(pixel_x, pixel_y, geotransform):
    """将像素坐标转换为地理坐标"""
    geo_x = geotransform[0] + pixel_x * geotransform[1] + pixel_y * geotransform[2]
    geo_y = geotransform[3] + pixel_x * geotransform[4] + pixel_y * geotransform[5]
    return geo_x, geo_y

def create_detection_geotiff(geotiff_path, output_path):
    """创建带有蓝色标记点的GeoTIFF并保持地理信息"""
    
    try:
        # 打开原始GeoTIFF获取地理信息
        ds = gdal.Open(geotiff_path)
        transform = ds.GetGeoTransform()
        projection = ds.GetProjection()
        # import logging
        # logging.info(projection)

        arr1 = ds.GetRasterBand(1).ReadAsArray()
        arr2 = ds.GetRasterBand(2).ReadAsArray()
        arr3 = ds.GetRasterBand(3).ReadAsArray()

        ds = None
        
        # 创建3通道RGB数组
        rgb = np.zeros((arr1.shape[0], arr1.shape[1], 3), dtype=np.uint8)
        rgb[:,:,0] = arr1  # Red channel
        rgb[:,:,1] = arr2  # Green channel
        rgb[:,:,2] = arr3  # Blue channel
        
        # 检查图像尺寸，如果太大则使用DEFLATE压缩而不是JPEG
        height, width = rgb.shape[:2]
        max_dimension = max(height, width)
        
        # 如果图像尺寸超过JPEG限制（通常是65535像素），使用DEFLATE压缩
        if max_dimension > 65000:
            print(f"⚠️ 图像尺寸较大 ({width}x{height})，使用DEFLATE压缩替代JPEG")
            compression_options = [
                'COMPRESS=DEFLATE',
                'PREDICTOR=2',
                'TILED=YES',
                'BLOCKXSIZE=512',
                'BLOCKYSIZE=512'
            ]
        else:
            print(f"✅ 图像尺寸适中 ({width}x{height})，使用JPEG压缩")
            compression_options = [
                'COMPRESS=JPEG',
                'JPEG_QUALITY=85',
                'TILED=YES',
                'BLOCKXSIZE=512',
                'BLOCKYSIZE=512'
            ]
        
        # 保存新的GeoTIFF
        driver = gdal.GetDriverByName('GTiff')
        out_ds = driver.Create(output_path, rgb.shape[1], rgb.shape[0], 3, gdal.GDT_Byte, options=compression_options)
        out_ds.SetGeoTransform(transform)
        out_ds.SetProjection(projection)
        
        out_ds.GetRasterBand(1).WriteArray(rgb[:,:,0])
        out_ds.GetRasterBand(2).WriteArray(rgb[:,:,1])
        out_ds.GetRasterBand(3).WriteArray(rgb[:,:,2])
        
        out_ds = None
        return True
    except Exception as e:
        print(f"创建标记点GeoTIFF失败: {str(e)}")
        # 如果仍然失败，尝试使用无压缩
        try:
            print("🔄 尝试使用无压缩模式...")
            driver = gdal.GetDriverByName('GTiff')
            out_ds = driver.Create(output_path, rgb.shape[1], rgb.shape[0], 3, gdal.GDT_Byte, options=['COMPRESS=NONE'])
            out_ds.SetGeoTransform(transform)
            out_ds.SetProjection(projection)
            
            out_ds.GetRasterBand(1).WriteArray(rgb[:,:,0])
            out_ds.GetRasterBand(2).WriteArray(rgb[:,:,1])
            out_ds.GetRasterBand(3).WriteArray(rgb[:,:,2])
            
            out_ds = None
            print("✅ 使用无压缩模式成功")
            return True
        except Exception as e2:
            print(f"❌ 无压缩模式也失败: {str(e2)}")
            return False

def convert_to_cog(input_path, output_path, compress="JPEG", quality=85, block_size=512, target_srs='EPSG:4326'):
    """将GeoTIFF转换为WGS84坐标系的Cloud Optimized GeoTIFF"""
    print(f"🔄 开始转换COG并重投影到 {target_srs}: {input_path} -> {output_path}")
    
    # 检查输入文件
    if not os.path.exists(input_path):
        print(f"❌ 输入文件不存在: {input_path}")
        return False
    
    # 创建输出目录
    out_dir = os.path.dirname(output_path)
    if not os.path.exists(out_dir):
        try:
            os.makedirs(out_dir, exist_ok=True)
            print(f"✅ 创建输出目录: {out_dir}")
        except Exception as e:
            print(f"❌ 无法创建输出目录: {e}")
            return False
    
    try:
        # 打开输入文件
        in_ds = gdal.Open(input_path)
        if in_ds is None:
            print(f"❌ 无法打开输入文件: {input_path}")
            return False
        
        # 获取原始投影信息
        original_srs = in_ds.GetProjection()
        print(f"📊 原始坐标系: {original_srs[:100]}...")
        print(f"📊 输入文件信息: {in_ds.RasterXSize}x{in_ds.RasterYSize}, {in_ds.RasterCount}波段")
        
        # 检查是否需要重投影
        from osgeo import osr
        source_srs = osr.SpatialReference()
        source_srs.ImportFromWkt(original_srs)
        
        target_srs_obj = osr.SpatialReference()
        target_srs_obj.ImportFromEPSG(int(target_srs.split(':')[1]))
        
        needs_reprojection = not source_srs.IsSame(target_srs_obj)
        
        if needs_reprojection:
            print(f"🔄 需要重投影: {source_srs.GetAttrValue('AUTHORITY', 1)} -> {target_srs}")
            
            # 使用gdalwarp进行重投影和COG转换
            creation_options = [
                'TILED=YES',
                f'COMPRESS={compress}',
                'COPY_SRC_OVERVIEWS=YES',
                f'BLOCKXSIZE={block_size}',
                f'BLOCKYSIZE={block_size}',
                'BIGTIFF=IF_SAFER',
                'INTERLEAVE=BAND'
            ]
            
            # 检查图像尺寸，如果太大则自动切换到DEFLATE压缩
            if compress.upper() == 'JPEG':
                # 获取图像尺寸
                width = in_ds.RasterXSize
                height = in_ds.RasterYSize
                max_dimension = max(width, height)
                
                if max_dimension > 65000:
                    print(f"⚠️ 图像尺寸较大 ({width}x{height})，自动切换到DEFLATE压缩")
                    creation_options = [
                        'TILED=YES',
                        'COMPRESS=DEFLATE',
                        'COPY_SRC_OVERVIEWS=YES',
                        f'BLOCKXSIZE={block_size}',
                        f'BLOCKYSIZE={block_size}',
                        'BIGTIFF=IF_SAFER',
                        'INTERLEAVE=BAND',
                        'PREDICTOR=2'
                    ]
                else:
                    creation_options.append(f'JPEG_QUALITY={quality}')
            elif compress.upper() == 'DEFLATE':
                creation_options.append('PREDICTOR=2')
            elif compress.upper() == 'LZW':
                creation_options.append('PREDICTOR=3')
            
            warp_options = gdal.WarpOptions(
                dstSRS=target_srs,  # 目标坐标系
                format='GTiff',
                multithread=True,  # 多线程加速
                creationOptions=creation_options
            )
            
            # 执行重投影转换
            print(f"🔧 执行重投影转换...")
            out_ds = gdal.Warp(output_path, in_ds, options=warp_options)
            
            if out_ds is not None:
                # 构建金字塔
                print(f"🏗️ 构建金字塔...")
                out_ds.BuildOverviews("NEAREST", [2, 4, 8, 16, 32])
                out_ds.FlushCache()
                out_ds = None
                
                print(f"✅ COG重投影转换成功: {output_path}")
                print(f"📍 目标坐标系: {target_srs}")
            else:
                print(f"❌ COG重投影转换失败")
                return False
        else:
            print(f"✅ 坐标系统已经是 {target_srs}，使用常规COG转换")
            
            # 常规COG转换 (不需要重投影)
            in_bands = in_ds.RasterCount
            
            # 设置nodata和统计值
            for i in range(in_bands):
                band = in_ds.GetRasterBand(i + 1)
                nodataVal = band.GetNoDataValue()
                maxBandValue = band.GetMaximum()
                
                if maxBandValue is None:
                    print(f"🔢 计算波段{i+1}统计值...")
                    in_ds.GetRasterBand(i + 1).ComputeStatistics(0)
                if nodataVal is None:
                    band.SetNoDataValue(0.0)
            
            # 构建金字塔
            print(f"🏗️ 构建金字塔...")
            overview_result = in_ds.BuildOverviews("NEAREST", [2, 4, 8, 16, 32])
            if overview_result != 0:
                print(f"⚠️ 金字塔构建警告，但继续处理...")
            
            # 设置压缩选项
            options = [
                "COPY_SRC_OVERVIEWS=YES",
                "TILED=YES",
                f"BLOCKXSIZE={block_size}",
                f"BLOCKYSIZE={block_size}",
                "INTERLEAVE=BAND",
                "BIGTIFF=IF_SAFER"
            ]
            
            # 检查图像尺寸，如果太大则自动切换到DEFLATE压缩
            if compress.upper() == "JPEG":
                # 获取图像尺寸
                width = in_ds.RasterXSize
                height = in_ds.RasterYSize
                max_dimension = max(width, height)
                
                if max_dimension > 65000:
                    print(f"⚠️ 图像尺寸较大 ({width}x{height})，自动切换到DEFLATE压缩")
                    options.extend(["COMPRESS=DEFLATE", "PREDICTOR=2"])
                    print(f"🗜️ 使用DEFLATE压缩")
                else:
                    options.extend(["COMPRESS=JPEG", f"JPEG_QUALITY={quality}"])
                    print(f"🗜️ 使用JPEG压缩，质量: {quality}")
            elif compress.upper() == "DEFLATE":
                options.extend(["COMPRESS=DEFLATE", "PREDICTOR=2"])
                print(f"🗜️ 使用DEFLATE压缩")
            elif compress.upper() == "LZW":
                options.extend(["COMPRESS=LZW", "PREDICTOR=3"])
                print(f"🗜️ 使用LZW压缩")
            
            # 创建COG
            print(f"🔧 创建COG文件...")
            driver = gdal.GetDriverByName('GTiff')
            if driver is None:
                print(f"❌ 无法获取GTiff驱动")
                return False
            
            out_ds = driver.CreateCopy(output_path, in_ds, options=options)
            if out_ds is None:
                print(f"❌ COG文件创建失败")
                return False
            
            # 确保文件写入完成
            out_ds.FlushCache()
            out_ds = None
        
        in_ds = None
        
        # 验证输出文件
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ COG文件生成成功: {output_path}")
            print(f"📁 文件大小: {file_size / (1024*1024):.2f} MB")
            
            # 验证COG文件有效性和坐标系统
            test_ds = gdal.Open(output_path)
            if test_ds is not None:
                test_projection = test_ds.GetProjection()
                print(f"✅ COG文件验证通过")
                print(f"📍 输出坐标系: {test_projection[:100]}...")
                test_ds = None
                return True
            else:
                print(f"❌ COG文件验证失败")
                return False
        else:
            print(f"❌ COG文件生成失败: 文件不存在")
            return False

    except Exception as e:
        print(f"❌ COG转换错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def convert_to_jpg(input_path, output_path):
    """将图像转换为JPG格式"""
    
    try:
        img = Image.open(input_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output_path, quality=70)
        return True
    except Exception as e:
        print(f"转换为JPG格式失败: {str(e)}")
        return False

def create_detection_json(detection_list, geotiff_path, output_path):
    """创建包含检测点坐标的JSON文件 - 使用高精度坐标转换"""
    
    try:
        # 获取图像中心坐标
        ds = gdal.Open(geotiff_path)
        transform = ds.GetGeoTransform()
        projection = ds.GetProjection()
        width = ds.RasterXSize
        height = ds.RasterYSize
        
        # 获取原始地理坐标
        center_geo_x, center_geo_y = pixel_to_geo(width/2, height/2, transform)
        
        # 检查坐标系统并转换到WGS84
        print(f"原始投影: {projection}")
        
        # 如果原始坐标系统不是WGS84，需要转换
        if 'CGCS2000' in projection or 'EPSG:45' in projection:
            # 智能检测和推荐坐标系统
            if 'CGCS2000' in projection:
                # 从投影信息中提取中央经线信息
                if 'central_meridian",102' in projection or 'CM 102E' in projection:
                    source_epsg = 'EPSG:4543'
                elif 'central_meridian",99' in projection or 'CM 99E' in projection:
                    source_epsg = 'EPSG:4542'
                elif 'central_meridian",105' in projection or 'CM 105E' in projection:
                    source_epsg = 'EPSG:4544'
                elif 'central_meridian",108' in projection or 'CM 108E' in projection:
                    source_epsg = 'EPSG:4545'
                else:
                    # 如果无法从投影信息中提取，根据坐标范围估算
                    # CGCS2000投影坐标的X值可以用来估算中央经线
                    if 400000 <= center_geo_x <= 600000:  # 接近中央经线的范围
                        if center_geo_x < 500000:
                            # 西侧，可能是CM 99E
                            source_epsg = 'EPSG:4542'
                        else:
                            # 东侧，可能是CM 102E或105E
                            # 根据Y坐标(纬度)进一步判断
                            if center_geo_y > 2500000:  # 北纬25度以上，可能是云南
                                source_epsg = 'EPSG:4543'  # CM 102E
                            else:
                                source_epsg = 'EPSG:4544'  # CM 105E
                    else:
                        # 默认使用CM 102E
                        source_epsg = 'EPSG:4543'
                
                print(f"检测到CGCS2000坐标系统，使用: {source_epsg}")
            else:
                # 根据经度自动推荐
                source_epsg = get_recommended_projection(center_geo_x)
            
            print(f"检测到CGCS2000坐标系统，从 {source_epsg} 转换到 WGS84")
            
            # 转换中心点到WGS84
            center_wgs84 = CGCS2000_3degree_to_WGS84([center_geo_x, center_geo_y], source_epsg)
            center_x, center_y = center_wgs84[0], center_wgs84[1]
            
            # 收集所有检测点坐标并转换到WGS84
            coordinates = []
            for item in detection_list:
                bbox = item['bbox']
                x_center = bbox[0] + bbox[2]/2
                y_center = bbox[1] + bbox[3]/2
                geo_x, geo_y = pixel_to_geo(x_center, y_center, transform)
                
                # 转换到WGS84
                wgs84_coords = CGCS2000_3degree_to_WGS84([geo_x, geo_y], source_epsg)
                coordinates.append({
                    'lat': wgs84_coords[1],
                    'lng': wgs84_coords[0]
                })
        else:
            # 已经是WGS84或其他地理坐标系统
            center_x, center_y = center_geo_x, center_geo_y
            
            coordinates = []
            for item in detection_list:
                bbox = item['bbox']
                x_center = bbox[0] + bbox[2]/2
                y_center = bbox[1] + bbox[3]/2
                geo_x, geo_y = pixel_to_geo(x_center, y_center, transform)
                coordinates.append({
                    'lat': geo_y,
                    'lng': geo_x
                })
        
        ds = None
        
        # 构建JSON结构
        result = {
            'count': len(coordinates),
            'coordinates': coordinates,
            'latlng': {
                'lat': center_y,
                'lng': center_x
            },
            'coordinate_info': {
                'original_projection': projection,
                'output_crs': 'WGS84 (EPSG:4326)',
                'conversion_applied': 'CGCS2000' in projection
            }
        }
        
        # 保存JSON文件
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ 坐标JSON已生成: {len(coordinates)} 个检测点")
        print(f"   中心坐标: [{center_x:.6f}, {center_y:.6f}] (WGS84)")
        
        return True
    except Exception as e:
        print(f"创建坐标JSON文件失败: {str(e)}")
        return False

def create_composite_image_without_plots(geotiff_path, detection_jpg_path, output_jpg_path):
    """没有地块文件时的合成图像生成"""
    print("开始生成合成图像(无地块信息)...")
    try:
        base_img = Image.open(detection_jpg_path)
        base_img.save(output_jpg_path, quality=85)
        print("直接保存检测结果图像")
    except FileNotFoundError:
        print(f"警告：检测结果图片不存在 {detection_jpg_path}")

def create_composite_image_optimized(geotiff_path, plots_shp_path, detected_shp_path, detection_jpg_path, parcel_counts, output_jpg_path):
    """增强版合成图像生成（在地块检测图上绘制醒目边界和标签）"""
    print("开始生成合成图像...")
    start_time = datetime.now()
    
    # 1. 先加载检测结果图像作为底图
    try:
        base_img = Image.open(detection_jpg_path)
        draw = ImageDraw.Draw(base_img)
    except FileNotFoundError:
        print(f"警告：检测结果图片不存在 {detection_jpg_path}，将使用空白画布")
        base_img = Image.new("RGB", (8000, 6000), (0, 0, 0))
        draw = ImageDraw.Draw(base_img)
    
    # 2. 加载GDAL获取坐标转换参数
    ds = gdal.Open(geotiff_path)
    transform = ds.GetGeoTransform()
    ds = None
    
    # 3. 设置绘图样式
    BORDER_COLOR = (255, 165, 0)
    BORDER_WIDTH = 14
    FONT_COLOR = (255, 0, 0)
    
    # 4. 加载字体
    try:
        default_size = 100
        font = ImageFont.truetype("arial.ttf", default_size)
    except:
        try:
            font = ImageFont.truetype("simhei.ttf", default_size)
        except:
            font = ImageFont.load_default()
            font.size = default_size
    
    # 5. 绘制地块边界和名称
    print("绘制地块边界和名称...")

    encoding = detect_encoding(plots_shp_path)
    with fiona.open(plots_shp_path, encoding=encoding) as parcels:
        for i, parcel in enumerate(parcels):
            if i >= 50:  # 限制绘制数量
                break
            
            geom = shape(parcel['geometry'])
            if geom.geom_type == 'Polygon':
                # 转换坐标到像素
                coords = []
                for x, y in geom.exterior.coords:
                    px = int((x - transform[0]) / transform[1])
                    py = int((y - transform[3]) / transform[5])
                    coords.append((px, py))
                
                if len(coords) > 2:
                    # 绘制加粗橘黄色边界
                    draw.polygon(coords, outline=BORDER_COLOR, width=BORDER_WIDTH)
                    
                    # 计算中心点并绘制红色标签
                    centroid = geom.centroid
                    cx = int((centroid.x - transform[0]) / transform[1])
                    cy = int((centroid.y - transform[3]) / transform[5])
                    parcel_name = parcel['properties'].get('name', f"地块{i+1}")
                    parcel_text = f"{parcel_name}: \n{parcel_counts[parcel_name]} 株玉米苗"
                    draw.text((cx, cy), parcel_text, fill=FONT_COLOR, font=font)
    
    # 6. 保存结果
    base_img.save(output_jpg_path, quality=85)
    end_time = datetime.now()
    print(f"合成图像生成完成，耗时: {end_time - start_time}")

def main():
    # 文件路径配置
    results_dir = "results-" + datetime.now().strftime('%Y-%m-%d_%H%M%S')
    os.makedirs(results_dir, exist_ok=True)
    # geotiff_path = '/home/ubuntu/project/corn_sxxz/code/result-30M-sxxz-corn.tif'
    geotiff_path = '/home/ubuntu/project/corn_sxxz/code/corn_cnt.tif'
    plots_shp_path = 'demo_fields/demo_small_fields.shp'                                 ## 包含各地块的 shp 文件

    base_name = os.path.splitext(os.path.basename(geotiff_path))[0]         ## 不带扩展名的 原始图像的名字
    yolo_model_path = '/home/ubuntu/project/corn_sxxz/code/runs/detect/train3/weights/best.pt'  ## 模型
    detected_objs_shp_path = os.path.join(results_dir, f"{base_name}_pts.shp")          ## 包含所有检测结果的shp
    detection_jpg_path = os.path.join(results_dir, f"{base_name}_sahi_export.jpg")      ## sahi 导出的结果图。
    detection_jpg_name = f"{base_name}_sahi_export"                                     ## sahi 导出的结果图。
    output_jpg_path = os.path.join(results_dir, f"{base_name}_composite_result.jpg")    ##  合成图像，包含检测框，地块，地块计数的 JPG
    detected_objs_json_path = os.path.join(results_dir, f"{base_name}_all_results.json")           ## 包含所有检测结果的json
    count_by_field_path = os.path.join(results_dir, f"{base_name}_cnt_by_plot.json")    ## 包含按地块统计数量的json
    
    # 检查地块文件是否存在
    plots_shp_exists = os.path.exists(plots_shp_path)
    
    # 1. 运行YOLO检测
    print("运行YOLO目标检测...")
    detection_list = run_yolo_detection(geotiff_path, yolo_model_path, results_dir, detection_jpg_name)
    
    # 2. 处理检测结果
    if plots_shp_exists:
        updated_detections, parcel_counts = process_detections_optimized(
            detection_list, geotiff_path, plots_shp_path, results_dir
        )
    else:
        updated_detections, parcel_counts = process_detections_without_plots(
            detection_list, geotiff_path, results_dir
        )
    
    # 保存统计结果
    with open(count_by_field_path, 'w', encoding='utf-8') as f:
        json.dump(parcel_counts, f, ensure_ascii=False, indent=2)
    
    # 保存最终检测结果
    final_results = {
        'timestamp': datetime.now().isoformat(),
        'count': len(updated_detections),
        'parcel_counts': parcel_counts,
        'detections': updated_detections
    }
    
    with open(detected_objs_json_path, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print("目标统计:")
    if plots_shp_exists:
        for parcel_id, count in parcel_counts.items():
            print(f"{parcel_id}: {count}")
    else:
        print(f"总检测数量: {parcel_counts.get('total', 0)}")
    
    # 3. 创建合成图像
    if plots_shp_exists:
        create_composite_image_optimized(
            geotiff_path, plots_shp_path, detected_objs_shp_path, 
            detection_jpg_path, parcel_counts, output_jpg_path
        )
    else:
        create_composite_image_without_plots(
            geotiff_path, detection_jpg_path, output_jpg_path
        )

    # 4. 创建新增的输出文件
    
    # 生成标记点GeoTIFF
    raw_tif_path = os.path.join(results_dir, f"{base_name}_raw.tif")
    create_detection_geotiff(geotiff_path, raw_tif_path)

    # 生成COG GeoTIFF
    cog_tif_path = os.path.join(results_dir, f"{base_name}_cog.tif")
    convert_to_cog(geotiff_path, cog_tif_path, compress="JPEG", quality=75, block_size=512)

        
    # 生成JPG图像
    jpg_path = os.path.join(results_dir, f"{base_name}.jpg")
    convert_to_jpg(raw_tif_path, jpg_path)
    
    # 生成坐标JSON
    json_path = os.path.join(results_dir, f"{base_name}_pts.json")
    create_detection_json(detection_list, geotiff_path, json_path)
    
    print(f"生成的文件:")
    print(f"- 标记点GeoTIFF: {raw_tif_path}")
    print(f"- COG GeoTIFF: {cog_tif_path}")
    print(f"- JPG图像: {jpg_path}")
    print(f"- 坐标JSON: {json_path}")

if __name__ == '__main__':
    main()