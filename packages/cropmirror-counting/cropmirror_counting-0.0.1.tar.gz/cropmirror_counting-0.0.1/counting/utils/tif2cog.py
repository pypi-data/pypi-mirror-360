'''
2025-06-30 优化测试



'''
import os
from osgeo import gdal,osr
import multiprocessing
from multiprocessing.pool import ThreadPool
from datetime import datetime

# 导入高精度坐标系统转换工具
try:
    from .wmct2wgs84 import (
        get_recommended_projection, 
        convert_point, 
        COORDINATE_SYSTEMS
    )
except ImportError:
    # 如果在单独测试时导入失败，提供基本功能
    def get_recommended_projection(longitude):
        return 'EPSG:4490'  # 默认CGCS2000地理坐标系
    
    def convert_point(from_epsg, to_epsg, src_point):
        return src_point  # 简单返回原坐标
    
    COORDINATE_SYSTEMS = {'EPSG:4490': 'CGCS2000 地理坐标系'}


# def translateToCOG_Optimized(in_ds, out_path, compression="JPEG", overview_levels=[2, 4, 8, 16], num_threads=None):
def translateToCOG_Optimized(in_ds, out_path, compression="JPEG", num_threads=None):
    """
    优化后的dataset转cog文件函数
    
    :param in_ds: 输入dataset
    :param out_path: 输出路径
    :param compression: 压缩算法 (LZW, DEFLATE, JPEG, ZSTD等)
    :param overview_levels: 金字塔层级
    :param num_threads: 线程数，默认使用所有核心
    :return:
    """
    # 设置GDAL配置优化
    # gdal.SetConfigOption('GDAL_NUM_THREADS', str(num_threads or multiprocessing.cpu_count()))
    # gdal.SetConfigOption('GDAL_TIFF_OVR_BLOCKSIZE', '256')
    # 设置 GDAL 多线程配置
    trans_start = datetime.now()
    print(f"Optimized trans_start: {trans_start}")
    gdal.SetConfigOption('GDAL_NUM_THREADS', 'ALL_CPUS')  # 使用所有CPU核心
    gdal.SetConfigOption('GDAL_TIFF_OVR_BLOCKSIZE', '256')  # 优化金字塔块大小
    
    # 创建输出目录
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    
    im_bands = in_ds.RasterCount
    # 串行处理波段统计和nodata值， Old method
    band_start = datetime.now()
    for i in range(im_bands):
        # 获取nodata和波段统计值
        nodataVal = in_ds.GetRasterBand(i + 1).GetNoDataValue()
        maxBandValue = in_ds.GetRasterBand(i + 1).GetMaximum()
        # 缺啥设置啥
        if maxBandValue is None:
            in_ds.GetRasterBand(i + 1).ComputeStatistics(0)
        if nodataVal is None:
            in_ds.GetRasterBand(i + 1).SetNoDataValue(0.0)
    band_end = datetime.now()
    print(f"Optimized band_start: {band_start}, band_end: {band_end}, band_cost: {band_end - band_start}")

    # 构建金字塔
    # in_ds.BuildOverviews("NEAREST", overview_levels, gdal.TermProgress)
    build_overviews_start = datetime.now()
    in_ds.BuildOverviews("NEAREST", [2, 4, 8, 16])
    build_overviews_end = datetime.now()
    print(f"Optimized build_overviews_start: {build_overviews_start}, build_overviews_end: {build_overviews_end}, build_overviews_cost: {build_overviews_end - build_overviews_start}")
    
    # 创建COG文件
    create_cog_start = datetime.now()
    driver = gdal.GetDriverByName('GTiff')
    creation_options = [
        "COPY_SRC_OVERVIEWS=YES",
        "TILED=YES",
        f"COMPRESS={compression}",
        "INTERLEAVE=BAND",
        "BIGTIFF=IF_SAFER",
        "NUM_THREADS=ALL_CPUS"
    ]
    
    # 根据压缩类型添加额外选项
    if compression in ["LZW", "DEFLATE", "ZSTD"]:
        creation_options.append("PREDICTOR=2")
    if compression == "DEFLATE":
        creation_options.append("ZLEVEL=9")
    if compression == "ZSTD":
        creation_options.append("ZSTD_LEVEL=9")
    
    driver.CreateCopy(out_path, in_ds, options=creation_options)
    create_cog_end = datetime.now()
    print(f"Optimized createCopy_cog_start: {create_cog_start}, createCopy_cog_end: {create_cog_end}, createCopy_cog_cost: {create_cog_end - create_cog_start}")
    
    # 显式清理资源
    in_ds.FlushCache()
    trans_end = datetime.now()
    print(f"Optimized translateToCOG_Optimized cost: {trans_end - trans_start}")

def translateToCOGOptimize(in_ds, out_path):
    """
    将 dataset 转为 COG 文件（优化版）
    :param in_ds: 输入 dataset
    :param out_path: 输出路径
    :return:
    """
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # 使用 gdal.Translate 生成 COG，内部会自动处理统计、overviews、分块等
    in_ds.BuildOverviews("NEAREST", [2, 4, 8, 16])
    translate_options = gdal.TranslateOptions(
        format='COG',
        creationOptions=[
            # 'TILED=YES',
            'COMPRESS=JPEG',  # 或者 'DEFLATE' 如果需要更高压缩比且支持透明
            'BLOCKXSIZE=256',
            'BLOCKYSIZE=256',
            'PREDICTOR=2',  # 对 DEFLATE 有效，JPEG 会忽略
            'OVERVIEWS=SKIP',  # 或者指定级别如 '2,4,8,16'
            'BIGTIFF=IF_SAFER'
        ]
    )

    # 直接从 in_ds 翻译成 COG
    gdal.Translate(out_path, in_ds, options=translate_options)

def translateToCOG(in_ds, out_path):
    """
    将dataset转为cog文件
    :param in_ds: 输入dataset
    :param out_path: 输出路径
    :return:
    """
    trans_start = datetime.now()
    print(f"Old trans_start: {trans_start}")
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir,exist_ok=True)
    band_start = datetime.now()
    im_bands = in_ds.RasterCount
    for i in range(im_bands):
        # 获取nodata和波段统计值
        nodataVal = in_ds.GetRasterBand(i + 1).GetNoDataValue()
        maxBandValue = in_ds.GetRasterBand(i + 1).GetMaximum()
        # 缺啥设置啥
        if maxBandValue is None:
            in_ds.GetRasterBand(i + 1).ComputeStatistics(0)
        if nodataVal is None:
            in_ds.GetRasterBand(i + 1).SetNoDataValue(0.0)
    band_end = datetime.now()
    print(f"Old band_start: {band_start}, band_end: {band_end}, band_cost: {band_end - band_start}")
    build_overviews_start = datetime.now()
    in_ds.BuildOverviews("NEAREST", [2, 4, 8, 16])
    build_overviews_end = datetime.now()
    print(f"Old build_overviews_start: {build_overviews_start}, build_overviews_end: {build_overviews_end}, build_overviews_cost: {build_overviews_end - build_overviews_start}")
    create_cog_start = datetime.now()
    driver = gdal.GetDriverByName('GTiff')
    driver.CreateCopy(out_path, in_ds,
                      options=["COPY_SRC_OVERVIEWS=YES",
                               "TILED=YES",
                               "COMPRESS=JPEG",
                            #    "QUALITY=100", not support
                               "INTERLEAVE=BAND"])
    create_cog_end = datetime.now()
    print(f"Old createCopy_cog_start: {create_cog_start}, createCopy_cog_end: {create_cog_end}, createCopy_cog_cost: {create_cog_end - create_cog_start}")

    trans_end = datetime.now()
    print(f"Old translateToCOG cost: {trans_end - trans_start}")


def warpDataset(in_ds, proj, resampling=1):
    """
    转换空间参考
    :param in_ds:输入dataset
    :param proj: 目标空间参考wkt
    :param resampling: 重采样方法
    :return: 转换后的dataset
    """
    RESAMPLING_MODEL = ['', gdal.GRA_NearestNeighbour,
                        gdal.GRA_Bilinear, gdal.GRA_Cubic]

    resampleAlg = RESAMPLING_MODEL[resampling]

    return gdal.AutoCreateWarpedVRT(in_ds, None, proj, resampleAlg)


def getTifDataset(dataset, srid=None, auto_recommend_cgcs2000=False):
    """
    返回tif文件dataset，支持CGCS2000高精度坐标系统
    :param dataset: 输入dataset
    :param srid: epsg_srid，若指定且不同于dataset，就将dataset转为该空间参考
    :param auto_recommend_cgcs2000: 是否自动推荐CGCS2000坐标系统
    :return: dataset
    """
    if dataset is None:
        print("Invalid result image file!")
        return
    
    fileSrs = osr.SpatialReference()
    fileSrs.ImportFromWkt(dataset.GetProjection())

    if srid is None and not auto_recommend_cgcs2000:
        return dataset
    
    # 自动推荐CGCS2000坐标系统
    if auto_recommend_cgcs2000 and srid is None:
        try:
            # 获取数据集的地理范围
            transform = dataset.GetGeoTransform()
            width = dataset.RasterXSize
            height = dataset.RasterYSize
            
            # 计算中心点经度
            center_x = transform[0] + (width / 2) * transform[1]
            center_y = transform[3] + (height / 2) * transform[5]
            
            # 如果当前是地理坐标系，直接使用经度
            if fileSrs.IsGeographic():
                longitude = center_x
            else:
                # 如果是投影坐标系，先转换到WGS84获取经度
                from osgeo import ogr
                wgs84_srs = osr.SpatialReference()
                wgs84_srs.ImportFromEPSG(4326)
                transform_to_wgs84 = osr.CoordinateTransformation(fileSrs, wgs84_srs)
                
                # 创建点几何
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(center_x, center_y)
                point.Transform(transform_to_wgs84)
                longitude = point.GetX()
            
            # 推荐最适合的CGCS2000坐标系统
            recommended_epsg = get_recommended_projection(longitude)
            srid = int(recommended_epsg.split(':')[1])
            print(f"自动推荐坐标系统: {recommended_epsg} - {COORDINATE_SYSTEMS.get(recommended_epsg, recommended_epsg)}")
            
        except Exception as e:
            print(f"自动推荐坐标系统失败: {e}")
            srid = 4490  # 默认使用CGCS2000地理坐标系
    
    if srid is not None:
        outSrs = osr.SpatialReference()
        outSrs.ImportFromEPSG(srid)

        if fileSrs.IsSame(outSrs):
            return dataset
        else:
            print(f"转换坐标系统: {fileSrs.GetAuthorityCode(None)} -> EPSG:{srid}")
            return warpDataset(dataset, outSrs.ExportToWkt())
    
    return dataset


'''
if __name__ == '__main__':
    import time
    start = time.process_time()
    inPath = "tobacco_result.tif"
    outputPath = "tobacco_result_cog.tif"

    originDataset = getTifDataset(inPath, 4326)
    translateToCOG(originDataset, outputPath)
    originDataset = None
    end = time.process_time()
    print('Running time: %s Seconds' % (end - start))
'''
