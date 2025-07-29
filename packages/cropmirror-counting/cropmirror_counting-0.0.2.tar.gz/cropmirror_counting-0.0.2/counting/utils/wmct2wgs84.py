#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复版坐标转换模块 - 使用proj4字符串
解决云南地区坐标定位错误问题
"""

try:
    from osgeo import ogr, osr
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False
    print("警告: GDAL/OGR 未安装，坐标转换功能不可用")

# CGCS2000 3度带坐标系统定义 (使用proj4字符串)
COORDINATE_SYSTEMS_PROJ4 = {
    'EPSG:4534': '+proj=tmerc +lat_0=0 +lon_0=75 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4535': '+proj=tmerc +lat_0=0 +lon_0=78 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4536': '+proj=tmerc +lat_0=0 +lon_0=81 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4537': '+proj=tmerc +lat_0=0 +lon_0=84 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4538': '+proj=tmerc +lat_0=0 +lon_0=87 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4539': '+proj=tmerc +lat_0=0 +lon_0=90 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4540': '+proj=tmerc +lat_0=0 +lon_0=93 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4541': '+proj=tmerc +lat_0=0 +lon_0=96 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4542': '+proj=tmerc +lat_0=0 +lon_0=99 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4543': '+proj=tmerc +lat_0=0 +lon_0=102 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4544': '+proj=tmerc +lat_0=0 +lon_0=105 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4545': '+proj=tmerc +lat_0=0 +lon_0=108 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4546': '+proj=tmerc +lat_0=0 +lon_0=111 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4547': '+proj=tmerc +lat_0=0 +lon_0=114 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4548': '+proj=tmerc +lat_0=0 +lon_0=117 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4549': '+proj=tmerc +lat_0=0 +lon_0=120 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4550': '+proj=tmerc +lat_0=0 +lon_0=123 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4551': '+proj=tmerc +lat_0=0 +lon_0=126 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4552': '+proj=tmerc +lat_0=0 +lon_0=129 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4553': '+proj=tmerc +lat_0=0 +lon_0=132 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4554': '+proj=tmerc +lat_0=0 +lon_0=135 +k=1 +x_0=500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
    'EPSG:4326': '+proj=longlat +datum=WGS84 +no_defs',
    'EPSG:3857': '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs',
    'EPSG:4490': '+proj=longlat +ellps=GRS80 +no_defs'
}

# 坐标系统描述
COORDINATE_SYSTEMS = {
    'EPSG:4534': 'CGCS2000 / 3度带 CM 75E (新疆西部)',
    'EPSG:4535': 'CGCS2000 / 3度带 CM 78E (新疆中西部)',
    'EPSG:4536': 'CGCS2000 / 3度带 CM 81E (新疆中部)',
    'EPSG:4537': 'CGCS2000 / 3度带 CM 84E (新疆东部)',
    'EPSG:4538': 'CGCS2000 / 3度带 CM 87E (新疆东南部)',
    'EPSG:4539': 'CGCS2000 / 3度带 CM 90E (西藏西部)',
    'EPSG:4540': 'CGCS2000 / 3度带 CM 93E (西藏中部)',
    'EPSG:4541': 'CGCS2000 / 3度带 CM 96E (西藏东部)',
    'EPSG:4542': 'CGCS2000 / 3度带 CM 99E (云南西部)',
    'EPSG:4543': 'CGCS2000 / 3度带 CM 102E (云南中部)',
    'EPSG:4544': 'CGCS2000 / 3度带 CM 105E (云南东部)',
    'EPSG:4545': 'CGCS2000 / 3度带 CM 108E (重庆、贵州西部)',
    'EPSG:4546': 'CGCS2000 / 3度带 CM 111E (湖南西部)',
    'EPSG:4547': 'CGCS2000 / 3度带 CM 114E (湖南东部)',
    'EPSG:4548': 'CGCS2000 / 3度带 CM 117E (河南东部)',
    'EPSG:4549': 'CGCS2000 / 3度带 CM 120E (山东东部)',
    'EPSG:4550': 'CGCS2000 / 3度带 CM 123E (江苏东部)',
    'EPSG:4551': 'CGCS2000 / 3度带 CM 126E (东北南部)',
    'EPSG:4552': 'CGCS2000 / 3度带 CM 129E (东北中部)',
    'EPSG:4553': 'CGCS2000 / 3度带 CM 132E (东北北部)',
    'EPSG:4554': 'CGCS2000 / 3度带 CM 135E (东北东部)'
}

def get_recommended_projection(longitude):
    """
    根据经度自动推荐最适合的CGCS2000 3度带坐标系统
    
    Args:
        longitude (float): 经度值
        
    Returns:
        str: 推荐的EPSG代码
    """
    # CGCS2000 3度带高精度坐标系统推荐 (覆盖全中国)
    if longitude >= 73.5 and longitude <= 76.5: return 'EPSG:4534'  # 新疆西部 (CM 75E)
    if longitude >= 76.5 and longitude <= 79.5: return 'EPSG:4535'  # 新疆中西部 (CM 78E)
    if longitude >= 79.5 and longitude <= 82.5: return 'EPSG:4536'  # 新疆中部 (CM 81E)
    if longitude >= 82.5 and longitude <= 85.5: return 'EPSG:4537'  # 新疆东部 (CM 84E)
    if longitude >= 85.5 and longitude <= 88.5: return 'EPSG:4538'  # 新疆东南部 (CM 87E)
    if longitude >= 88.5 and longitude <= 91.5: return 'EPSG:4539'  # 西藏西部 (CM 90E)
    if longitude >= 91.5 and longitude <= 94.5: return 'EPSG:4540'  # 西藏中部 (CM 93E)
    if longitude >= 94.5 and longitude <= 97.5: return 'EPSG:4541'  # 西藏东部 (CM 96E)
    if longitude >= 97.5 and longitude <= 100.5: return 'EPSG:4542' # 云南西部、青海南部 (CM 99E)
    if longitude >= 100.5 and longitude <= 103.5: return 'EPSG:4543' # 云南中部、四川西部 (CM 102E)
    if longitude >= 103.5 and longitude <= 106.5: return 'EPSG:4544' # 云南东部、四川中部 (CM 105E)
    if longitude >= 106.5 and longitude <= 109.5: return 'EPSG:4545' # 重庆、贵州西部 (CM 108E)
    if longitude >= 109.5 and longitude <= 112.5: return 'EPSG:4546' # 湖南西部、贵州东部 (CM 111E)
    if longitude >= 112.5 and longitude <= 115.5: return 'EPSG:4547' # 湖南东部、湖北南部 (CM 114E)
    if longitude >= 115.5 and longitude <= 118.5: return 'EPSG:4548' # 河南东部、安徽西部 (CM 117E)
    if longitude >= 118.5 and longitude <= 121.5: return 'EPSG:4549' # 山东东部、江苏北部 (CM 120E)
    if longitude >= 121.5 and longitude <= 124.5: return 'EPSG:4550' # 江苏东部、上海 (CM 123E)
    if longitude >= 124.5 and longitude <= 127.5: return 'EPSG:4551' # 辽宁、吉林南部 (CM 126E)
    if longitude >= 127.5 and longitude <= 130.5: return 'EPSG:4552' # 吉林北部、黑龙江南部 (CM 129E)
    if longitude >= 130.5 and longitude <= 133.5: return 'EPSG:4553' # 黑龙江北部 (CM 132E)
    if longitude >= 133.5 and longitude <= 136.5: return 'EPSG:4554' # 黑龙江东部 (CM 135E)
    
    # 中国境内使用CGCS2000地理坐标系
    if longitude >= 70 and longitude <= 140: return 'EPSG:4490'
    
    # 默认使用Web Mercator
    return 'EPSG:3857'

def convert_point_proj4(from_proj4, to_proj4, src_point):
    """
    使用proj4字符串进行坐标点转换
    
    Args:
        from_proj4 (str): 源坐标系统proj4字符串
        to_proj4 (str): 目标坐标系统proj4字符串
        src_point (list): 源坐标点 [lng, lat] 或 [x, y]
        
    Returns:
        list: 转换后的坐标点 [x, y] 或 [lng, lat]
    """
    if not GDAL_AVAILABLE:
        print("错误: GDAL/OGR 未安装，无法进行坐标转换")
        return src_point
    
    try:
        # 创建坐标系统
        cs_from = osr.SpatialReference()
        cs_from.ImportFromProj4(from_proj4)
        
        cs_to = osr.SpatialReference()
        cs_to.ImportFromProj4(to_proj4)
        
        # 创建坐标转换
        transform = osr.CoordinateTransformation(cs_from, cs_to)
        
        # 执行转换
        pwkt = "POINT (%s %s)" % (src_point[0], src_point[1])
        point = ogr.CreateGeometryFromWkt(pwkt)
        
        if point is None:
            print(f"错误: 无法创建几何点 {src_point}")
            return src_point
            
        point.Transform(transform)
        
        # 解析结果
        wkt_result = point.ExportToWkt()
        if wkt_result is None:
            print(f"错误: 坐标转换失败 {src_point}")
            return src_point
            
        tmp = wkt_result.replace('POINT (', '').replace(')', '').split()
        return [float(tmp[0]), float(tmp[1])]
        
    except Exception as e:
        print(f"坐标转换错误: {e}")
        return src_point

def convert_point(from_epsg, to_epsg, src_point):
    """
    通用坐标点转换函数 (使用proj4字符串)
    
    Args:
        from_epsg (str or int): 源坐标系统EPSG代码
        to_epsg (str or int): 目标坐标系统EPSG代码
        src_point (list): 源坐标点 [lng, lat] 或 [x, y]
        
    Returns:
        list: 转换后的坐标点 [x, y] 或 [lng, lat]
    """
    # 处理EPSG代码格式
    if isinstance(from_epsg, int):
        from_epsg = f'EPSG:{from_epsg}'
    if isinstance(to_epsg, int):
        to_epsg = f'EPSG:{to_epsg}'
    
    # 获取proj4字符串
    from_proj4 = COORDINATE_SYSTEMS_PROJ4.get(from_epsg)
    to_proj4 = COORDINATE_SYSTEMS_PROJ4.get(to_epsg)
    
    if from_proj4 is None:
        print(f"错误: 不支持的源坐标系统 {from_epsg}")
        return src_point
        
    if to_proj4 is None:
        print(f"错误: 不支持的目标坐标系统 {to_epsg}")
        return src_point
    
    return convert_point_proj4(from_proj4, to_proj4, src_point)

def convert_polygon(from_epsg, to_epsg, polygon_coords):
    """
    多边形坐标转换函数
    
    Args:
        from_epsg (str or int): 源坐标系统EPSG代码
        to_epsg (str or int): 目标坐标系统EPSG代码
        polygon_coords (list): 多边形坐标列表 [[lng1, lat1], [lng2, lat2], ...]
        
    Returns:
        list: 转换后的多边形坐标列表
    """
    converted_coords = []
    for coord in polygon_coords:
        converted_coord = convert_point(from_epsg, to_epsg, coord)
        converted_coords.append(converted_coord)
    return converted_coords

def WGS84_to_CGCS2000_3degree(src_point, target_epsg=None):
    """
    WGS84 转 CGCS2000 3度带高精度坐标系统
    
    Args:
        src_point (list): [lng, lat] WGS84坐标点
        target_epsg (str, optional): 目标EPSG代码，如果不指定则自动推荐
        
    Returns:
        tuple: (转换后坐标点 [x, y], 使用的EPSG代码)
    """
    if target_epsg is None:
        target_epsg = get_recommended_projection(src_point[0])
    
    converted_point = convert_point('EPSG:4326', target_epsg, src_point)
    return converted_point, target_epsg

def CGCS2000_3degree_to_WGS84(src_point, source_epsg):
    """
    CGCS2000 3度带坐标系统 转 WGS84
    
    Args:
        src_point (list): [x, y] CGCS2000坐标点
        source_epsg (str): 源EPSG代码
        
    Returns:
        list: [lng, lat] WGS84坐标点
    """
    return convert_point(source_epsg, 'EPSG:4326', src_point)

# 向后兼容的函数
def webMercator_to_WGS84(src_point):
    """Web Mercator 转 WGS84 (向后兼容)"""
    return convert_point('EPSG:3857', 'EPSG:4326', [src_point[1], src_point[0]])

def WGS84_to_webMercator(src_point):
    """WGS84 转 Web Mercator (向后兼容)"""
    result = convert_point('EPSG:4326', 'EPSG:3857', [src_point[1], src_point[0]])
    return [result[1], result[0]]

if __name__ == '__main__':
    # 测试用例
    print("=== 修复版坐标转换测试 ===")
    
    # 测试云南昆明坐标
    kunming_wgs84 = [102.7, 25.0]  # [lng, lat]
    print(f"昆明 WGS84: {kunming_wgs84}")
    
    # 自动推荐坐标系统
    recommended_epsg = get_recommended_projection(kunming_wgs84[0])
    print(f"推荐坐标系统: {recommended_epsg} - {COORDINATE_SYSTEMS[recommended_epsg]}")
    
    # 转换到高精度坐标系统
    kunming_cgcs2000, used_epsg = WGS84_to_CGCS2000_3degree(kunming_wgs84)
    print(f"昆明 {used_epsg}: {kunming_cgcs2000}")
    
    # 转换回WGS84验证
    kunming_wgs84_back = CGCS2000_3degree_to_WGS84(kunming_cgcs2000, used_epsg)
    print(f"验证转换回WGS84: {kunming_wgs84_back}")
    
    # 计算转换精度
    lng_diff = abs(kunming_wgs84[0] - kunming_wgs84_back[0])
    lat_diff = abs(kunming_wgs84[1] - kunming_wgs84_back[1])
    print(f"转换精度: 经度差 {lng_diff:.8f}°, 纬度差 {lat_diff:.8f}°")
    
    if lng_diff < 0.000001 and lat_diff < 0.000001:
        print("✅ 坐标转换成功，精度良好")
    else:
        print("❌ 坐标转换精度不足") 