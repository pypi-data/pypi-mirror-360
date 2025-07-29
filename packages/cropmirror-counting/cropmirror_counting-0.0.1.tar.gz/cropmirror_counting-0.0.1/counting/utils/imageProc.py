#!/usr/bin/env python
# -*- coding: utf-8 -*-
# time: 2024/5/12 16:49

import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
import glob
import cv2
from osgeo import gdal, osr, ogr
import numpy as np
import json
from loguru import logger
gdal.UseExceptions()

from .tif2cog import getTifDataset, translateToCOG             # 在MirrorCrop项目中，使用此行 --- imageProc.py 放在utils文件夹中
# from tif2cog import getTifDataset, translateToCOG             # 在单独测试imageProc时，使用此行

# 导入高精度坐标系统转换工具
from .wmct2wgs84 import (
    get_recommended_projection, 
    convert_point, 
    convert_polygon,
    WGS84_to_CGCS2000_3degree,
    CGCS2000_3degree_to_WGS84,
    COORDINATE_SYSTEMS
)

# 地球半径
# _EARTH_R = 6371000 # meter

# 每纬度的物理距离
# _DISTANCE_PER_LAT = 2*np.pi*_EARTH_R*np.cos(camera_lat*np.pi/180)/360 #85.563km
# _DISTANCE_PER_LAT = 85563

# 每经度的物理距离
# _DISTANCE_PER_LNG = 2*np.pi*_EARTH_R/360 #111.194 km
# _DISTANCE_PER_LNG = 111194.92664455873


_MODEL = {
    # 无人机各个型号的传感器尺寸
    "DJI": {
        "M3M": {                        # 4/3 CMOS
            "h_sensor_size": 18.0,      # mm
            "v_sensor_size": 13.5,      # mm
            "d_sensor_size": 22.5,      # mm
            "pixel_size": 3.3  # um
        },
        "M3E": {                        # 4/3 CMOS
            "h_sensor_size": 18.0,      # mm
            "v_sensor_size": 13.5,      # mm
            "d_sensor_size": 22.5,      # mm
            "pixel_size": 3.3           # um
        },
        "Phantom 4 Pro": {                        # 4/3 CMOS
            "h_sensor_size": 13.2,      # mm
            "v_sensor_size": 8.8,      # mm
            "d_sensor_size": 15.8,      # mm
            "pixel_size": 3.3           # um
        },
        "M4E": {                        # 4/3 CMOS
            "h_sensor_size": 18.0,      # mm
            "v_sensor_size": 13.5,      # mm
            "d_sensor_size": 22.5,      # mm
            "pixel_size": 3.3           # um
        },
        "ZenmuseP1": {
            "h_sensor_size": 36.0,      # mm
            "v_sensor_size": 24.0,      # mm
            "d_sensor_size": 43.2,      # mm
            "pixel_size": 4.4           # um

        }
    }
}
# logger.info(_MODEL)



class imgProc():
    def __init__(self, img, out_folder, loglevel="info"):
        self.img_all_info = {}
        self.img = img
        self.log_level = loglevel
        self.out_folder = out_folder


        self.tmp_folder = out_folder + '/tmp/'
        if not os.path.exists(self.tmp_folder):
            os.mkdir(self.tmp_folder)

        basename = os.path.splitext(os.path.basename(self.img))[0]

        self.img_cropped_tmp = os.path.join(self.tmp_folder, basename + '_cropped.JPG')             # 用于方向矫正的临时文件
        self.img_tmp = os.path.join(self.tmp_folder, basename + '_orient_corrected.JPG')             # 用于方向矫正的临时文件
        self.img_tran = os.path.join(self.tmp_folder, basename + '_tran.JPG')             # 透视变换后的JPG
        self.img_tag_tran = os.path.join(self.tmp_folder, basename + '_tag_tran.JPG')             # 透视变换后的JPG
        self.compress_jpg_path = os.path.join(self.out_folder, basename + '.JPG')
        self.tag_jpg_path = os.path.join(self.tmp_folder, basename + '_tag.JPG')
        self.img_tran_ndarray = np.array([])             # 透视变换后的JPG
        self.tag_img_tran_ndarray = np.array([])             # 透视变换后的JPG
        # self.img_tran_R_bin = os.path.join(self.out_folder, basename + '_tran_R_Bin.JPG')             # 透视变换后的JPG
        self.img_tran_R_bin = np.array([])
        self.raw_geotiff_path = os.path.join(self.tmp_folder,  basename + '_nonrotate_raw.tif')          # 未做Yaw角矫正前的 原始 tiff照片
        self.rotate_raw_geotiff_path = os.path.join(self.out_folder, basename + '_raw.tif')       # Yaw角矫正后的原始 tiff照片
        self.tag_geotiff_path = os.path.join(self.tmp_folder,  basename + '_tag_geo.tif')          # 未做Yaw角矫正前的 原始 tiff照片
        self.rotate_tag_geotiff_path = os.path.join(self.tmp_folder, basename + '_rotated_tag_geo.tif')       # Yaw角矫正后的原始 tiff照片
        self.raw_cog_tiff_path = os.path.join(self.tmp_folder, basename + '_cog_raw.tif')        # 未做Yaw 角矫正的cog tiff
        self.rotate_cog_tiff_path = os.path.join(self.out_folder, basename + '_cog.tif')         # 最后的cog tiff, 完成透视变换和Yaw角矫正
        self.key_points = os.path.join(self.tmp_folder, basename + '_key_pts.csv')             # 记录在处理图像过程中的几个关键点 的坐标, 用于在QGIS里测试
        self.sheep_points = os.path.join(self.tmp_folder, basename + '_sheep_pts.csv')             # 记录在处理图像过程中的几个关键点 的坐标, 用于在QGIS里测试
        self.RzMat = np.array([])
        self.proj_matrix = np.array([])
        self.rotation_matrix = np.array([])
        # self.img_all_info["fovWidth"] = 84.0    # M3M 对角FOV 度, DJ 官网 https://ag.dji.com/cn/mavic-3-m/specs?startPoint=0
        self.img_all_info["fovHeight"] = 0.0     # 先设置为0, 后面会在读取得到照片分辨率后计算
        self.camera_center_distance = 0
        self.camera_tran_center_distance = 0
        self.exif_data = {}
        self.geotransform = []

        self.exif_data = self.get_exif()
        self.get_img_all_info()


        # self.pre_process()
        self.calculate_image_fov()              # 计算fov
        self.img_correct_orientation()          # 矫正照片 Orientation 旋转

        self.img_all_info |= self.get_gsd()

        if self.log_level == "debug":
            logger.debug('Finished Getting Necessary Information of the image')
            logger.debug(f'GPS: {self.img_all_info["camera_lat"]}, {self.img_all_info["camera_lng"]}')
            logger.debug(f'Size: {self.img_all_info["width"]}, {self.img_all_info["height"]}')
            logger.debug(f'Focal Len: {self.img_all_info["focal_len"]}')
            logger.debug(f'GSD: {self.img_all_info["gsd"]}')
            logger.debug(f'FOV: {self.img_all_info["hfov"]}, {self.img_all_info["vfov"]}, {self.img_all_info["dfov"]}')


    def collect_info(self):

        file = self.out_folder + '/imginfocollection.csv'
        jpgname = os.path.basename(self.img)
        gpsstatus = self.img_all_info["GpsStatus"]
        surveyingmode = self.img_all_info["SurveyingMode"]
        gimbalroll = self.img_all_info["GimbalRollDegree"]
        gimbalpitch = self.img_all_info["GimbalPitchDegree"]
        gimbalyaw = self.img_all_info["GimbalYawDegree"]
        flightroll = self.img_all_info["FlightRollDegree"]
        flightpitch = self.img_all_info["FlightPitchDegree"]
        flightyaw = self.img_all_info["FlightYawDegree"]
        relativealtitude = self.img_all_info["RelativeAltitude"]
        digitalzoomratio = self.img_all_info["DigitalZoomRatio"]
        dronemodel = self.img_all_info["DroneModel"]
        dronemaker = self.img_all_info["DroneMake"]
        width = self.img_all_info["width"]
        height = self.img_all_info["height"]
        LOG = self.img_all_info["LOG"]
        gsd = self.img_all_info["gsd"]


        with open(file, "a") as file:
            if gpsstatus == "RTK":
                rtkflag = self.img_all_info["RtkFlag"]
                rtkstdlon = self.img_all_info["RtkStdLon"]
                rtkstdlat = self.img_all_info["RtkStdLat"]
                rtkstdhgt = self.img_all_info["RtkStdHgt"]
                file.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,,,,,,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                    jpgname, gimbalpitch, flightpitch, gimbalyaw, flightyaw, gimbalroll, flightroll, width, height, dronemaker, dronemodel, relativealtitude, LOG, digitalzoomratio, gpsstatus, surveyingmode,
                    rtkflag, rtkstdlat, rtkstdlon, rtkstdhgt, gsd))
            elif gpsstatus == "Normal":
                file.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,,,,,,%s,%s,%s,%s,%s,%s,%s,,,,,%s\n" % (
                    jpgname, gimbalpitch, flightpitch, gimbalyaw, flightyaw, gimbalroll, flightroll, width, height, dronemaker, dronemodel, relativealtitude, LOG, digitalzoomratio, gpsstatus, surveyingmode,
                    gsd))

    def pre_process(self):
        """
        预处理
        """
        self.calculate_image_fov()              # 计算fov
        self.img_correct_orientation()          # 矫正照片 Orientation 旋转
        # self.img_crop()                         # 矫正照片 Orientation 旋转

    def img_crop(self):
        """
        处理 pitch 角太小，拍照太倾斜的照片。
        pitch >= -30, 裁剪 30%
        -30 > pitch >= -40, 裁剪 25%
        -40 > pitch >= -50, 裁剪 15%
        """
        pitch = self.img_all_info["GimbalPitchDegree"]
        # logger.info(pitch)
        if abs(pitch) - 50.0 > 0.01:
            return
        else:
            image = cv2.imdecode(np.fromfile(self.img, dtype=np.uint8), -1)      #
            # logger.info(image.shape)
            height = image.shape[0]


            rate = 0.0
            if 50.0 - abs(pitch) >= 0.01 and abs(pitch) - 40.0 > 0.01:
                rate = 0.15
            elif 40.0 - abs(pitch) >= 0.01 and abs(pitch) - 30.0 > 0.01:
                rate = 0.20
            if 30.0 - abs(pitch) >= 0.01:
                rate = 0.30

            if self.log_level == "debug":
                logger.debug("Pitch: %s. The image is Oblique. Crop %s percent of it for better presentation" % (pitch, rate))

            h = int(height * rate)

            image[0:h,:,:] = 0                      # 0 - h 部分全部设置为0，黑色，这样在 地图上显示的时候，就不会显示这部分了。
            cv2.imwrite(self.img_cropped_tmp, image)                                   #

            self.img = self.img_cropped_tmp



    def img_correct_orientation(self):
        """
        照片Orientation 矫正
        EXIF Orientation 参数意义 与 矫正方法
        旋转角度	    参数      矫正方法
        0°	        1        不需要矫正
        顺时针90°	6        顺时针转270°
        逆时针90°	8        顺时针转90°
        180°	    3        顺时针转180°
        """
        orientation = self.exif_data["Orientation"]
        # logger.info(orientation)
        if orientation == 1:
            return
        else:
            image = Image.open(self.img)
            exif_data = image.getexif()  # 获取图片的EXIF标签
            angle = 0
            if orientation == 3:
                angle = 180

            elif orientation == 6:
                angle = 270

            elif orientation == 8:
                angle = 90

            if self.log_level == "debug":
                logger.debug("EXIF Oritation: %s (3: 180; 6: 90; 8: -90;). The image is rotated. Need to correct, rotate back %s degree" % (orientation, angle))
            exif_data[274] = 1
            image.info["exif"] = exif_data
            image.save(self.img_tmp, exif=exif_data)
            image.close()
            self.img = self.img_tmp



    def get_img_all_info(self):
        """
        1, 收集所有关于照片的参数，如：
        焦距，GPS，照片分辨率，相机的像元尺寸，云台(Roll, Pitch, Yaw)，相机高度，相机内参矩阵+畸变参数，GSD, pixel size像元尺寸, 等等
        """
        if self.log_level == "debug":
            logger.debug("Getting Necessary Information of the image, GPS, FOV, Size, Focal Len, GSD, ect.")

        self.get_coord_transform_matrix()       # GWS84 4326 与 Web Mercator 3857 坐标系之间的变换矩阵
        self.img_all_info |= self.get_image_size() | self.get_gps_info() | self.get_len_info() | self.get_xmp_info()
        self.img_all_info |= self.get_center_lat_lng()

        dronemaker = self.img_all_info["DroneMake"]
        dronemodel = self.img_all_info["DroneModel"]
        self.pixel_size = _MODEL[dronemaker][dronemodel]["pixel_size"]

        if self.log_level == "debug":
            logger.debug("Finish Getting Necessary Information of the image")


    def cleanup(self, media=False):
        if not self.log_level == "debug":
            # 非 debug mode, 直接删除整个tmp folder
            # if os.path.exists(self.img_tran):
            #     os.remove(self.img_tran)
            # if os.path.exists(self.sheep_points):
            #     os.remove(self.sheep_points)
            # if os.path.exists(self.key_points):
            #     os.remove(self.key_points)

            shutil.rmtree(self.tmp_folder)

            # 在上传完JPG后调用的话，删除 rotate_raw_geotiff_path 以及对应 的.ovr, .aux.xml文件
            if media:
                if os.path.exists(self.rotate_raw_geotiff_path):
                    os.remove(self.rotate_raw_geotiff_path)
                if os.path.exists(self.rotate_raw_geotiff_path + '.ovr'):
                    os.remove(self.rotate_raw_geotiff_path + '.ovr')
                if os.path.exists(self.rotate_raw_geotiff_path + '.aux.xml'):
                    os.remove(self.rotate_raw_geotiff_path + '.aux.xml')

        else:
            # debug mode, 删除tmp folder中的部分文件
            if os.path.exists(self.img_tmp):
                os.remove(self.img_tmp)

            # if os.path.exists(self.raw_geotiff_path):
            #     os.remove(self.raw_geotiff_path)

            if os.path.exists(self.raw_geotiff_path + '.ovr'):
                os.remove(self.raw_geotiff_path + '.ovr')

            if os.path.exists(self.raw_cog_tiff_path):
                os.remove(self.raw_cog_tiff_path)


    def get_coord_transform_matrix(self):
        """
        获取 坐标系 间变换的矩阵
        CoordinateTransformation from GWS84 4326 to Web Mercator: 3857
        CoordinateTransformation from Web Mercator: 3857 to GWS84 4326
        支持CGCS2000 3度带高精度坐标系统
        """

        cs1 = osr.SpatialReference()
        cs1.ImportFromEPSG(4326)
        # print(cs1.ExportToPrettyWkt())

        cs2 = osr.SpatialReference()
        cs2.ImportFromEPSG(3857)
        # print(cs2.ExportToPrettyWkt())
        self.img_all_info["4326_to_3857"] = osr.CoordinateTransformation(cs1, cs2)
        self.img_all_info["3857_to_4326"] = osr.CoordinateTransformation(cs2, cs1)
        
        # 添加CGCS2000坐标系统支持
        try:
            # 根据GPS坐标推荐最适合的CGCS2000坐标系统
            if hasattr(self, 'img_all_info') and 'camera_lng' in self.img_all_info:
                recommended_epsg = get_recommended_projection(self.img_all_info['camera_lng'])
                self.img_all_info['recommended_cgcs2000_epsg'] = recommended_epsg
                self.img_all_info['recommended_coord_system'] = COORDINATE_SYSTEMS.get(recommended_epsg, recommended_epsg)
                
                # 创建CGCS2000坐标转换矩阵
                epsg_code = int(recommended_epsg.split(':')[1])
                cs_cgcs2000 = osr.SpatialReference()
                cs_cgcs2000.ImportFromEPSG(epsg_code)
                
                self.img_all_info["4326_to_cgcs2000"] = osr.CoordinateTransformation(cs1, cs_cgcs2000)
                self.img_all_info["cgcs2000_to_4326"] = osr.CoordinateTransformation(cs_cgcs2000, cs1)
        except Exception as e:
            logger.warning(f"CGCS2000坐标系统初始化失败: {e}")
            self.img_all_info['recommended_cgcs2000_epsg'] = 'EPSG:4490'  # 默认使用CGCS2000地理坐标系

    def webMercator_to_WGS84(self,src_point):
        """
        src_point: [x,y]
        return: [lat,lng]
        """
        pwkt = "POINT (%s %s)" % (src_point[1], src_point[0])       # lng, lat
        point = ogr.CreateGeometryFromWkt(pwkt)
        point.Transform(self.img_all_info["3857_to_4326"])
        tmp = point.ExportToWkt().replace('(','').replace(')','').split()   # 'POINT (47.3488070138318 -122.598149943144)'
        return [float(tmp[1]),float(tmp[2])]

    def WGS84_to_webMercator(self, src_point):
        """
        src_point: [lat,lng]
        return: [x,y]
        """
        pwkt = "POINT (%s %s)" % (src_point[0],src_point[1])
        point = ogr.CreateGeometryFromWkt(pwkt)
        point.Transform(self.img_all_info["4326_to_3857"])
        tmp = point.ExportToWkt().replace('(','').replace(')','').split()
        return [float(tmp[2]),float(tmp[1])]

    def WGS84_to_CGCS2000(self, src_point):
        """
        WGS84 转 CGCS2000 高精度坐标系统
        src_point: [lng, lat] WGS84坐标点
        return: ([x, y], epsg_code) CGCS2000坐标点和使用的EPSG代码
        """
        try:
            # 使用通用转换函数
            cgcs2000_coords, used_epsg = WGS84_to_CGCS2000_3degree(src_point)
            return cgcs2000_coords, used_epsg
        except Exception as e:
            logger.error(f"WGS84转CGCS2000失败: {e}")
            # 降级使用内置转换矩阵
            if "4326_to_cgcs2000" in self.img_all_info:
                pwkt = "POINT (%s %s)" % (src_point[0], src_point[1])
                point = ogr.CreateGeometryFromWkt(pwkt)
                point.Transform(self.img_all_info["4326_to_cgcs2000"])
                tmp = point.ExportToWkt().replace('(','').replace(')','').split()
                return [float(tmp[1]), float(tmp[2])], self.img_all_info.get('recommended_cgcs2000_epsg', 'EPSG:4490')
            else:
                return src_point, 'EPSG:4326'  # 转换失败，返回原坐标

    def CGCS2000_to_WGS84(self, src_point, source_epsg=None):
        """
        CGCS2000 转 WGS84
        src_point: [x, y] CGCS2000坐标点
        source_epsg: 源EPSG代码，如果不指定则使用推荐的坐标系统
        return: [lng, lat] WGS84坐标点
        """
        try:
            if source_epsg is None:
                source_epsg = self.img_all_info.get('recommended_cgcs2000_epsg', 'EPSG:4490')
            
            # 使用通用转换函数
            return CGCS2000_3degree_to_WGS84(src_point, source_epsg)
        except Exception as e:
            logger.error(f"CGCS2000转WGS84失败: {e}")
            # 降级使用内置转换矩阵
            if "cgcs2000_to_4326" in self.img_all_info:
                pwkt = "POINT (%s %s)" % (src_point[0], src_point[1])
                point = ogr.CreateGeometryFromWkt(pwkt)
                point.Transform(self.img_all_info["cgcs2000_to_4326"])
                tmp = point.ExportToWkt().replace('(','').replace(')','').split()
                return [float(tmp[1]), float(tmp[2])]
            else:
                return src_point  # 转换失败，返回原坐标

    def get_gsd(self):
        """
        计算照片GSD
        """
        gsd = {}
        ## GSD: Meter per pixel
        # LOG = self.img_all_info["LOG"]  # 1: LOG G(Ground) 地面中心离光心距离, 即相机坐标系的Zc轴值; 即线段 OC
        # h_sensor_size = self.img_all_info["h_sensor_size"]
        # width =  self.img_all_info["width"]

        H = self.img_all_info["RelativeAltitude"]       # 无人机飞行高度，离地面高度
        pitch = abs(self.img_all_info["GimbalPitchDegree"])     # 相机 pitch 角 的绝对值, 仰角
        pitchArc = pitch * np.pi / 180
        LOG = H / np.sin(pitchArc)         # 1: LOG G(Ground) 地面中心离光心距离, 即相机坐标系的Zc轴值; 即线段 OC

        gsd["gsd"] = (self.img_all_info["h_sensor_size"] * LOG) / (self.img_all_info["focal_len"] * self.img_all_info["width"])

        return gsd

    def get_exif(self):
        """
        从图片中返回EXIF元数据
        """
        exif_data = {}
        if not self.exif_data:
            try:
                i = Image.open(self.img)  # 使用PIL库打开图片
                tags = i._getexif()  # 获取图片的EXIF标签

                for tag, value in tags.items():
                    decoded = TAGS.get(tag, tag)  # 尝试从预定义的TAGS字典中获取标签的中文描述，否则使用标签ID
                    exif_data[decoded] = value  # 将标签及其值存储到exif_data字典中
                    # print("EXIF:",decoded,value)

                i.close()
                return exif_data

            except Exception as e:
                logger.error("Can NOT get the exif data for the image!")
                logger.error(e)  # 捕获所有异常并忽略，这通常不是一个好的做法，应该明确指定要捕获的异常


    def get_image_size(self):
        """
        获取照片分辨率
        """
        i = Image.open(self.img)

        return {"width": i.width, "height":i.height}

        # return {"width": self.exif_data["ExifImageWidth"], "height": self.exif_data["ExifImageHeight"]}

    def get_xmp_info(self):
        """
        获取照片参数
        """

        b = b"\x3c\x2f\x72\x64\x66\x3a\x44\x65\x73\x63\x72\x69\x70\x74\x69\x6f\x6e\x3e"
        a = b"\x3c\x72\x64\x66\x3a\x44\x65\x73\x63\x72\x69\x70\x74\x69\x6f\x6e\x20"
        with open(self.img, 'rb') as img:
            data = bytearray()
            dj_data_dict = {}
            flag = False
            for line in img.readlines():
                if a in line:
                    flag = True
                if flag:
                    data += line
                if b in line:
                    break

            if len(data) > 0:
                data = str(data.decode('ascii'))
                # print("Data:")
                # print(data)
                # print("=====================================================================================")
                lines = list(filter(lambda x: 'drone-dji:' in x, data.replace('\" ', '\"\n').split("\n")))
                for d in lines:
                    # print(d)
                    d = d.strip()[10:]
                    key, value = d.split("=")
                    dj_data_dict[key] = value
                    # print(key, value)

            roll = float(dj_data_dict["GimbalRollDegree"][1:-1])
            gimbalyaw = float(dj_data_dict["GimbalYawDegree"][1:-1])
            pitch = float(dj_data_dict["GimbalPitchDegree"][1:-1])
            flightroll = float(dj_data_dict["FlightRollDegree"][1:-1])
            flightyaw = float(dj_data_dict["FlightYawDegree"][1:-1])
            flightpitch = float(dj_data_dict["FlightPitchDegree"][1:-1])
            relativealtitude = float(dj_data_dict["RelativeAltitude"][1:-1])
            gpsstatus = dj_data_dict["GpsStatus"][1:-1]
            surveyingmode = dj_data_dict["SurveyingMode"][1:-1]
            digitalzoomratio = float(self.exif_data["DigitalZoomRatio"])
            dronemodel = self.exif_data["Model"]
            dronemaker = self.exif_data["Make"]

            # print("GpsStatus", gpsstatus)
            # print("SurveyingMode", surveyingmode)
            # RtkFlag RtkStdLon	RtkStdLat	RtkStdHgt

            if gpsstatus == "RTK":
                rtkflag = dj_data_dict["RtkFlag"][1:-1]
                rtkstdlon = float(dj_data_dict["RtkStdLon"][1:-1])
                rtkstdlat = float(dj_data_dict["RtkStdLat"][1:-1])
                rtkstdhgt = float(dj_data_dict["RtkStdHgt"][1:-1])
                dj_data_dict["RtkFlag"] = rtkflag
                dj_data_dict["RtkStdLon"] = rtkstdlon
                dj_data_dict["RtkStdLat"] = rtkstdlat
                dj_data_dict["RtkStdHgt"] = rtkstdhgt
                # rtkfile = self.out_folder + '/01rtk.txt'
                # with open(rtkfile, "a") as file:
                #     file.write("%s,%s,%s,%s,%s,%s,%s\n" % (self.img, surveyingmode, gpsstatus, rtkflag, rtkstdlat, rtkstdlon, rtkstdhgt))
            # elif gpsstatus == "Normal":
            #     print("%s,%s,%s" % (self.img, gpsstatus, surveyingmode))
            #     rtkfile = self.out_folder + '/01rtk.txt'
            #     with open(rtkfile, "a") as file:
            #         file.write("%s,%s,%s\n" % (self.img, surveyingmode, gpsstatus))

            if "DewarpData" in dj_data_dict.keys():
                dewarpdata = dj_data_dict["DewarpData"][1:-1].split(";")[1].split(",")
                dj_data_dict["DewarpData"] = dewarpdata

            dj_data_dict["GimbalRollDegree"] = roll
            dj_data_dict["GimbalPitchDegree"] = pitch
            dj_data_dict["GimbalYawDegree"] = gimbalyaw
            dj_data_dict["FlightRollDegree"] = flightroll
            dj_data_dict["FlightPitchDegree"] = flightpitch
            dj_data_dict["FlightYawDegree"] = flightyaw
            dj_data_dict["RelativeAltitude"] = relativealtitude
            dj_data_dict["GpsStatus"] = gpsstatus
            dj_data_dict["SurveyingMode"] = surveyingmode
            dj_data_dict["DigitalZoomRatio"] = digitalzoomratio  # 数码变焦倍率
            dj_data_dict["DroneModel"] = dronemodel
            dj_data_dict["DroneMake"] = dronemaker

            #dzrfile = self.out_folder + '/01dzr.csv'
            #with open(dzrfile, "a") as file:
            #    file.write("%s,%s\n" % (self.img, digitalzoomratio))

            if abs(abs(pitch) - 90.0) <  0.001:
                yaw = flightyaw
                rotateyaw = flightyaw

            else:
                yaw = gimbalyaw
                rotateyaw = gimbalyaw

            dj_data_dict["Yaw"] = yaw
            dj_data_dict["RotateYaw"] = rotateyaw

            return dj_data_dict

    def get_len_info(self):
        """
        获取相机镜头焦距
        """
        if self.exif_data.get('FocalLength'):       # 'FocalLength'
            focal_len = self.exif_data['FocalLength']
            return {"focal_len": focal_len}
        else:
            logger.error("Can Not Get focal len in image EXIF data")

    def dms_2dd(self, d, m, s, i):
        """
        将角度的 度/分/秒 转换为十进制度
        """
        sec = float((m * 60) + s)  # 将分和秒转换为秒
        dec = float(sec / 3600)  # 将秒转换为小数度
        deg = float(d + dec)  # 将度和小数度相加

        if i.upper() == 'W':  # 如果方向是西
            deg = deg * -1  # 将度数变为负数

        elif i.upper() == 'S':  # 如果方向是南
            deg = deg * -1  # 将度数变为负数

        return float(deg)

    def get_gps_info(self):
        """
        从EXIF元数据中提取GPS信息
        """
        lat = None  # 纬度
        lng = None  # 经度
        if self.exif_data.get('GPSInfo'):  # 如果EXIF中包含GPS信息
            # 纬度
            coords = self.exif_data['GPSInfo']
            i = coords[1]  # 纬度方向（N/S）
            d = coords[2][0]  # 纬度度数
            m = coords[2][1]  # 纬度分钟
            s = coords[2][2]  # 纬度秒
            lat = self.dms_2dd(d, m, s, i)  # 将纬度转换为十进制度

            # 经度
            i = coords[3]  # 经度方向（E/W）
            d = coords[4][0]  # 经度度数
            m = coords[4][1]  # 经度分钟
            s = coords[4][2]  # 经度秒
            lng = self.dms_2dd(d, m, s, i)  # 将经度转换为十进制度

            wmct = self.WGS84_to_webMercator([lat,lng])

            # MC: Mercator, 墨卡托
            logger.debug(f"camera_lat: {lat}, camera_lng: {lng}, camera_MC_lat: {wmct[0]}, camera_MC_lng: {wmct[1]}")
            return {"camera_lat": lat, "camera_lng": lng, "camera_MC_lat": wmct[0], "camera_MC_lng": wmct[1]}
        else:
            logger.error("Can Not Get GPS from image EXIF data")
            logger.debug("Can Not Get GPS from image EXIF data")


    def get_center_lat_lng(self):
        """
        计算照片中心的经纬度, 并放到 self.img_all_info中
        """
        self.camera_center_distance = self.img_all_info["RelativeAltitude"] / np.tan(abs(self.img_all_info["GimbalPitchDegree"]) * np.pi/180)
        if self.camera_center_distance < 0.01:
            self.camera_center_distance = 0.0

        yaw = self.img_all_info["Yaw"]

        # Web Mercator 投影的坐标
        center_MC_lat = self.img_all_info["camera_MC_lat"] + self.camera_center_distance * np.cos(yaw * np.pi / 180)
        center_MC_lng = self.img_all_info["camera_MC_lng"] + self.camera_center_distance * np.sin(yaw * np.pi / 180)

        # print("Camera to GC:" , self.camera_center_distance)

        cen_lat_lng = {}
        cen_lat_lng["center_MC"] = [center_MC_lat, center_MC_lng]

        return cen_lat_lng

    def calculate_image_fov(self):
        """
        计算相机的 FOV 值
        33.87mm×25.4mm
        """
        dronemodel = self.img_all_info["DroneModel"]
        dronemaker = self.img_all_info["DroneMake"]

        h_sensor_size = _MODEL[dronemaker][dronemodel]["h_sensor_size"]
        v_sensor_size = _MODEL[dronemaker][dronemodel]["v_sensor_size"]
        d_sensor_size = _MODEL[dronemaker][dronemodel]["d_sensor_size"]

        if self.log_level == "debug":
            logger.debug("Drone Info: %s, %s, %s, %s, %s" % (dronemaker, dronemodel, h_sensor_size, v_sensor_size, d_sensor_size))
        # 不考虑 数码变焦
        # 4/3 CMOS: horizon =  18.0 mm, vertical = 13.5 mm, diagonal = 22.5 mm
        # h_sensor_size = 18.0       # mm Horizon Sensor Size, 水平方向
        # v_sensor_size = 13.5       # mm Vertical Sensor Size, 垂直方向
        # d_sensor_size = 22.5       # mm Diagonal Sensor Size, 对角线

        # 考虑 数码变焦
        # h_sensor_size = 18.0 * 1.231 / self.img_all_info["DigitalZoomRatio"]      # mm Horizon Sensor Size, 水平方向
        # v_sensor_size = 13.5 * 1.231 / self.img_all_info["DigitalZoomRatio"]       # mm Vertical Sensor Size, 垂直方向
        # d_sensor_size = 22.5 * 1.231 / self.img_all_info["DigitalZoomRatio"]     # mm Diagonal Sensor Size, 对角线
        h_sensor_size = h_sensor_size / self.img_all_info["DigitalZoomRatio"]      # mm Horizon Sensor Size, 水平方向
        v_sensor_size = v_sensor_size / self.img_all_info["DigitalZoomRatio"]       # mm Vertical Sensor Size, 垂直方向
        d_sensor_size = d_sensor_size / self.img_all_info["DigitalZoomRatio"]     # mm Diagonal Sensor Size, 对角线
        focal_len = self.img_all_info["focal_len"]  # mm
        self.img_all_info["h_sensor_size"] = h_sensor_size  # mm
        self.img_all_info["v_sensor_size"] = v_sensor_size  # mm
        self.img_all_info["d_sensor_size"] = d_sensor_size  # mm

        # hfovArc =  2 * np.arctan( 0.5 * self.pixel_size * self.img_all_info["width"] / self.img_all_info["focal_len"] / 1000)        # np.arctan 返回的是弧度
        # vfovArc =  2 * np.arctan( 0.5 * self.img_all_info["width"] / 3713.29 )        # np.arctan 返回的是弧度
        # dfovArc =  2 * np.arctan( 0.5 * w_sensor_size / self.img_all_info["focal_len"] )        # np.arctan 返回的是弧度

        # 使用 照相机传感器尺寸和焦距计算 FOV
        hfovArc =  2 * np.arctan( 0.5 * h_sensor_size / focal_len )        # np.arctan 返回的是弧度
        vfovArc =  2 * np.arctan( 0.5 * v_sensor_size / focal_len )        # np.arctan 返回的是弧度
        dfovArc =  2 * np.arctan( 0.5 * d_sensor_size / focal_len )        # np.arctan 返回的是弧度

        hfov = hfovArc * 180 / np.pi       # 水平 FOV
        vfov = vfovArc * 180 / np.pi       # 垂直 FOV
        dfov = dfovArc * 180 / np.pi       # 对角 FOV

        self.img_all_info["hfov"] = hfov    # FOV 度, Horizon FOV, 水平方向 FOV
        self.img_all_info["vfov"] = vfov    # FOV 度, Vertical FOV, 垂直方向 FOV
        self.img_all_info["dfov"] = dfov    # FOV 度, Diagonal FOV, 对角线 FOV

        if self.log_level == "debug":
            logger.debug("FOV: {Horizon: %s; Vertical: %s; Diagonal: %s}" % (hfov, vfov, dfov))


    def calculate_image_positions(self, media=False):
        """
        media: 当在上传照片到媒体库时调用，media=True
        使用几何方法，计算无人机照片在Web Mercator坐标下几个点的位置:
        原始照片中的：LT, RT, LB, RB
        经过透视变换后的：LT, RT, LB, RB
        经过偏航角矫正后的：LT, RT, LB, RB
        """

        if self.log_level == "debug":
            logger.debug("Start to calculate the positions of the image %s" % os.path.basename(self.img))
        self.img_all_info["fovHeight"] = self.img_all_info["vfov"]
        H = self.img_all_info["RelativeAltitude"]       # 无人机飞行高度，离地面高度
        H = H + 8.0

        # 角度换算成弧度：1度 = pi/180 弧度
        pitch = abs(self.img_all_info["GimbalPitchDegree"])     # 相机 pitch 角 的绝对值, 仰角
        pitchArc = pitch * np.pi / 180

        # yaw = self.img_all_info["GimbalYawDegree"]              # 相机 Yaw 角, 偏航角
        yaw = self.img_all_info["Yaw"]              # 相机 Yaw 角, 偏航角
        rotateyaw = self.img_all_info["RotateYaw"]              # 相机 Yaw 角, 偏航角
        yawArc = yaw * np.pi/180 # 弧度
        rotateyawArc = rotateyaw * np.pi/180 # 弧度

        # fovH = self.img_all_info["fovHeight"]                   # fovH: 照片高度方向的FOV(视角)
        fovH = self.img_all_info["vfov"]                   # fovH: 照片高度方向的FOV(视角); FOV 度, Vertical FOV, 垂直方向 FOV
        # fovW = self.img_all_info["fovWidth"]                    # fovW: 照片宽度方向的FOV(视角)
        # fovH = fovW
        fovHArc = fovH * np.pi / 180

        angleT = fovH/2 - (90 - pitch)                          # 角 DOA, DO 与 OA 夹角
        angleTArc = angleT * np.pi / 180

        height = self.img_all_info["height"]
        width = self.img_all_info["width"]

        cameraInsideImage = False
        if pitch > 90 - fovH/2:
            cameraInsideImage = True

        # logger.info(self.img_all_info["width"], self.img_all_info["height"])
        # logger.info("Yaw:",yaw, "Pitch:",pitch, "Fov Width:", fovW, "Fov Height:", fovH)

        # O 点: 飞机观察点，即无人机相机所在的点
        LOG = H / np.sin(pitchArc)         # 1: LOG G(Ground) 地面中心离光心距离, 即相机坐标系的Zc轴值; 即线段 OC
        # logger.info("LOG =",H, "/", self.img_all_info["GimbalPitchDegree"], "=", self.img_all_info["LOG"])

        self.img_all_info["LOG"] = LOG                          # 1: LOG G(Ground) 地面中心离光心距离, 即相机坐标系的Zc轴值; 即线段 OC
        AC = H / np.tan(pitchArc)                               # 2: AC
        AD = H * np.tan(angleTArc)                              # 4: AD
        if cameraInsideImage:
            CD = AC + AD                                        # 4: CD
        else:
            CD = AC - AD                                        # 4: CD
        OD = H / np.cos(angleTArc)                              # 5: OD
        LOA = OD * np.cos(fovHArc/2)                            # 6: LOA A面中心离光心距离, 即相机坐标系的Zc轴值, 线段 OE
        self.img_all_info["LOA"] = LOA                          # 6: LOA A面中心离光心距离, 即相机坐标系的Zc轴值, 线段 OE
        DE = OD * np.sin(fovHArc/2)                             # 7: DE
        CE = DE / np.tan(pitchArc)                              # 8: CE
        LOB = LOG / (1 - CE/LOA)                                # 9: LOB B面中心离光心距离, 即相机坐标系的Zc轴值, 线段 OF

        if self.log_level == "debug":
            logger.debug("CE: %s, LOA: %s, LOG: %s, LOB: %s" % (CE, LOA, LOG, LOB))

        self.img_all_info["LOB"] = LOB                          # 9: LOB B面中心离光心距离, 即相机坐标系的Zc轴值, 线段 OF
        CF = LOB - LOG                                          # 10: CF
        NF = CF * DE / CE                                       # 11: NF
        LHB = 2 * NF                                            # 12: LHB B面 高度 H(Height), 也是线段 NI
        LHA = 2 * DE                                            # 13: LHA A面 高度 H(Height), 也是线段 DM
        dh = LHA / height
        LWA = width * LHA / height                              # 14: LWA A面 宽度 W(Width), 照片近端边的地理长度, LB ---> RB 的距离
        if abs(LOA - LOG) < 0.01:                                          # LOA == LOG, 此时相机垂直向下, pitch 角 = -90 度
            LWB = LWA                                           # 15: LWB B面 宽度 W(Width), 照片远端边的地理长度, LT ---> RT 的距离
            LHG = LHA                                           # 16: LHG Grond面 高度 H(Height), 照片近端边 与 远端边的 距离, LT,RT ---> LB,RB 的距离. 即线段DI
        else:
            LWB = width * LHB / height                          # 15: LWB B面 宽度 W(Width), 照片远端边的地理长度, LT ---> RT 的距离
            LHG = (CE + CF) / np.cos(pitchArc)                  # 16: LHG Grond面 高度 H(Height), 照片近端边 与 远端边的 距离, LT,RT ---> LB,RB 的距离. 即线段DI
        self.img_all_info["LHA"] = LHA
        self.img_all_info["LHB"] = LHB
        self.img_all_info["LWA"] = LWA
        self.img_all_info["LWB"] = LWB
        self.img_all_info["LHG"] = LHG

        if self.log_level == "debug":
            logger.debug("LHA: %s, LHB: %s, LWA: %s, LWB: %s, LHG: %s" % (LHA,LHB,LWA,LWB,LHG))
        LGA = LHG - LHG / (1 + LWA / LWB)                       # 17: 地面中点离与A面距离, C点 ---> DM, 即线段CE
        LGB = LHG / (1 + LWA / LWB)                             # 18: 地面中点离与B面距离, C点 ---> NI, 即线段CF
        self.img_all_info["LGA"] = LHG - LHG / (1 + LWA / LWB)  # 17: 地面中点离与A面距离, 即线段 GA
        self.img_all_info["LGB"] = LHG / (1 + LWA / LWB)        # 18: 地面中点离与B面距离, 即线段 GB
        # print("Camera to GC: %s; LHG: %s; LGA: %s; LGB: %s" % (self.camera_center_distance, LHG, LGA, LGB))
        self.camera_tran_center_distance = self.camera_center_distance + LHG/2 - LGA            # 完成透视变换后，照片的中心点与相机定位点的距离
        if self.camera_tran_center_distance < 0.01:
            self.camera_tran_center_distance = 0.0
        # logger.info("Camera to Tran GC: %s" % self.camera_tran_center_distance)

        # logger.info("LWA:", LWA, "LHG:", LHG, "LWB:", LWB, "DIAG:", np.sqrt(LHG ** 2 + LWB ** 2))

        LTG = np.sqrt((LWB/2)**2 + LGB**2)                      # 19: 图中心到 B 面对角线距离, Left Top --> Ground Center
        self.img_all_info["LTG"] = LTG                          # 19: 图中心到 B 面对角线距离, Left Top --> Ground Center
        LBG = np.sqrt((LWA/2)**2 + LGA**2)                      # 20: 图中心到 A 面对角线距离, Left Bottom --> Ground Center
        self.img_all_info["LBG"] = LBG                          # 20: 图中心到 A 面对角线距离, Left Bottom --> Ground Center
        self.img_all_info["RTG"] = self.img_all_info["LTG"]     # 21: 图中心到 B 面对角线距离, Right Top --> Ground Center
        self.img_all_info["RBG"] = self.img_all_info["LBG"]     # 22: 图中心到 A 面对角线距离, Right Bottom --> Ground Center


        GCMClat = self.img_all_info["center_MC"][0]                    # Web Mercator 3857 地面中心点纬度 坐标轴为N, Ground Center latitude
        GCMClng = self.img_all_info["center_MC"][1]                    # WGS Mercator 3857 地面中心点经度 坐标轴为E, Ground Center longitude

        # Yaw sin(), cos()
        sinYaw = np.sin(yawArc)
        cosYaw = np.cos(yawArc)
        # sinrotateYaw = np.sin(rotateyawArc)
        # cosrotateYaw = np.cos(rotateyawArc)

        # 绕 Z 轴旋转, Yaw角 旋转矩阵, 计算偏航用的矩阵
        self.RzMat = np.array([[cosYaw,  -sinYaw],
                               [sinYaw, cosYaw]])
        # 绕 Z 轴旋转, Yaw角 旋转矩阵, 计算偏航用的矩阵
        # self.RzMat = np.array([[cosrotateYaw,  -sinrotateYaw],
        #                   [sinrotateYaw, cosrotateYaw]])

        # 在没有做透视变换之前, LT, LB, RT, RB 四个点旋转之前，相对于地面中心 GC 的的XY, X,Y 值 单位：米; X:N 北; Y:E 东
        LTx, LTy = self.img_all_info["LGB"], -1 * self.img_all_info["LWB"] / 2
        RTx, RTy = self.img_all_info["LGB"], self.img_all_info["LWB"] / 2
        LBx, LBy = -1 * self.img_all_info["LGA"], -1 * self.img_all_info["LWA"] / 2
        RBx, RBy = -1 * self.img_all_info["LGA"], self.img_all_info["LWA"] / 2

        # 在没有做透视变换之前, 四个角点在没有旋转 Yaw 前，在Web Mercator 3857 坐标系下 平移, 单位：米
        # ltoMCLat, ltoMCLng = GCMClat + LTx, GCMClng + LTy       # Original LT, lt original before 透视变换
        # rtoMCLat, rtoMCLng = GCMClat + RTx, GCMClng + RTy       # Original LB, lb original before 透视变换
        # lboMCLat, lboMCLng = GCMClat + LBx, GCMClng + LBy       # Original RT, rt original before 透视变换
        # rboMCLat, rboMCLng = GCMClat + RBx, GCMClng + RBy       # Original RB, rb original before 透视变换

        # 在没有做透视变换之前, 旋转 单位还是 米
        [LTxr, LTyr] = np.dot(self.RzMat, [LTx,LTy])     # LTxy: LTx 旋转 yaw 度后; LTyy: LTy 旋转 yaw 度后
        [LBxr, LByr] = np.dot(self.RzMat, [LBx,LBy])
        [RTxr, RTyr] = np.dot(self.RzMat, [RTx,RTy])
        [RBxr, RByr] = np.dot(self.RzMat, [RBx,RBy])

        # 在没有做透视变换之前, 角点在旋转 Yaw 后，在Web Mercator 3857 坐标系下 平移, 单位：米
        self.img_all_info["LT_lat_lng_MC"] = [GCMClat + LTxr, GCMClng + LTyr]
        self.img_all_info["LB_lat_lng_MC"] = [GCMClat + LBxr, GCMClng + LByr]
        self.img_all_info["RT_lat_lng_MC"] = [GCMClat + RTxr, GCMClng + RTyr]
        self.img_all_info["RB_lat_lng_MC"] = [GCMClat + RBxr, GCMClng + RByr]

        if self.log_level == "debug":
            logger.debug("LT Mercator: %s" % self.img_all_info["LT_lat_lng_MC"])
            logger.debug("RT Mercator: %s" % self.img_all_info["RT_lat_lng_MC"])
            logger.debug("LB Mercator: %s" % self.img_all_info["LB_lat_lng_MC"])
            logger.debug("RB Mercator: %s" % self.img_all_info["RB_lat_lng_MC"])
        # logger.info("")
        # logger.info("四个角在旋转之前, 相对于透视变换前的地面中心的 X, Y值:")
        # logger.info("LT: %s,%s" % (LTx,LTy))
        # logger.info("LB: %s,%s" % (LBx,LBy))
        # logger.info("RT: %s,%s" % (RTx,RTy))
        # logger.info("RB: %s,%s" % (RBx,RBy))

        # logger.info("")
        # logger.info("四个角在 旋转 Yaw %s 度后，相对于透视变换前地面中心的 X,Y 值:" % yaw)
        # logger.info("LT: %s,%s" % (LTxr,LTyr))
        # logger.info("LB: %s,%s" % (LBxr,LByr))
        # logger.info("RT: %s,%s" % (RTxr,RTyr))
        # logger.info("RB: %s,%s" % (RBxr,RByr))
        # logger.info("")

        gimbalyaw = self.img_all_info["GimbalYawDegree"]
        flightyaw = self.img_all_info["FlightYawDegree"]
        Yaw = self.img_all_info["Yaw"]
        rotateyaw = self.img_all_info["RotateYaw"]

        if self.log_level == "debug":
            logger.debug("飞行高度: %s; 近端宽度: %s; 照片高度: %s; 远端宽度: %s; 相机到照片中心距离(未做透视变换前): %s; 原始照片中心到透视变换照片中心: %s" % (H, LWA, LHG, LWB, LOG, self.camera_tran_center_distance))
        # logger.info("Pitch:", pitch,"Gimbal Yaw:", gimbalyaw, "Flight Yaw:", flightyaw, "Yaw:", Yaw, "Rotate Yaw:", rotateyaw)
        # logger.info("Pitch:", pitch,"Gimbal Yaw:", gimbalyaw, "Flight Yaw:", flightyaw, "Yaw:", yaw)

        # *********************************************************************** #
        # 做透视变换, 完成后，得到一张90度向下的仰视图, 正射影像
        # *********************************************************************** #

        far_width = width                                          # 远端的保持不变，近端和高度按地理长度的比例计算
        near_width  = int(far_width * LWA / LWB)
        tran_width = far_width
        tran_height = int(far_width * LHG / LWB)
        tran_width = far_width
        tran_height = int(far_width * LHG / LWB)

        self.img_all_info["tran_width"] = tran_width
        self.img_all_info["tran_height"] = tran_height

        # 记录照片地理长宽高等关键信息
        # geor = self.out_folder + '/01geor.txt'
        # logger.info("名字,飞行高度,近端宽度,照片高度,远端宽度,相机到照片中心距离(未做透视变换前),相机到透视变换照片中心")
        # with open(geor, "a") as file:
        #     # print("飞行高度: %s; 近端宽度: %s; 照片高度: %s; 远端宽度: %s; 相机到照片中心距离(未做透视变换前): %s; 相机到透视变换照片中心: %s" % (H, LWA, LHG, LWB, LOG, self.camera_tran_center_distance))
        #     file.write("%s,%s,%s,%s,%s,%s,%s\n" % (imgname, H, LWA, LHG, LWB, LOG, self.camera_tran_center_distance))

        # 记录 Pitch 角
        # pyr= self.out_folder + '/01pitchyaw.txt'
        # logger.info("Name,GPitch,FPitch,GYaw,FYaw,GRoll,FRoll,Width,Height,TWidth,THeight")
        # with open(pyr, "a") as file:
        #     file.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (imgname, gimbalpitch, flightpitch, gimbalyaw, flightyaw, gimbalroll, flightroll, width, height, tran_width, tran_height))
        # # 记录 Flight Yaw 和 Gimbal Yaw 相差较大的照片
        # gap = abs(abs(flightyaw) - abs(gimbalyaw))
        # if gap > 15:
        #     # yawgap = 'D:/ChenQiu/DrLong/sheep_crowd_counting/GIS/test/yawgap.txt'
        #     yawgap = self.out_folder + '/01yawgap.txt'
        #     with open(yawgap, "a") as file:
        #         file.write("%s; Gimbal Yaw: %s; Flight Yaw: %s; GAP: %s\n" % (os.path.basename(self.img), gimbalyaw, flightyaw, gap))


        FW = LWB
        NW = LWA
        H = LHG
        w = width
        h = height

        x = int(width * LWA / LWB)
        h_new = int(width * LHG / LWB)

        pts1 = np.float32([[(w-x)/2,0],[(w+x)/2,0],[0,height],     [width,height]])                  # 原照片四个角的坐标
        pts2 = np.float32([[(w-x)/2,0],[(w+x)/2,0],[(w-x)/2,h_new],[(w+x)/2,h_new]])                  # 原照片四个角的坐标

        # self.img_crop()                         # 对于拍照角度比较倾斜的照片，剪切一部分

        im1 = cv2.imread(self.img)

        self.proj_matrix = cv2.getPerspectiveTransform(pts1, pts2)                      # 透视矩阵
        self.img_tran_ndarray = cv2.warpPerspective(im1, self.proj_matrix, (tran_width, tran_height))     # 做透视变换，得到计算透视后的照片, 不写入磁盘。
        im2 = cv2.warpPerspective(im1, self.proj_matrix, (tran_width, tran_height), cv2.INTER_AREA)     # 做透视变换，得到计算透视后的照片, 保存到磁盘. cv2.INTER_NEAREST、cv2.INTER_LINEAR、cv2.INTER_CUBIC或cv2.INTER_LANCZOS4
        cv2.imwrite(self.img_tran, im2)

        if not media:
            im1_tag = cv2.imread(self.tag_jpg_path)
            self.tag_img_tran_ndarray = cv2.warpPerspective(im1_tag, self.proj_matrix, (tran_width, tran_height))     # 做透视变换，得到计算透视后的照片, 不写入磁盘。
            im2_tag = cv2.warpPerspective(im1_tag, self.proj_matrix, (tran_width, tran_height), cv2.INTER_AREA)     # 做透视变换，得到计算透视后的照片, 保存到磁盘. cv2.INTER_NEAREST、cv2.INTER_LINEAR、cv2.INTER_CUBIC或cv2.INTER_LANCZOS4
            cv2.imwrite(self.img_tag_tran, im2_tag)

        # 取 R 波段, 为后面二值化做准备
        im_bin = cv2.imdecode(np.fromfile(self.img, dtype=np.uint8),-1)[:,:,0]          # 对原始照片, 取 R 波段, 二值化, 然后做透视变换
        im_bin[im_bin < 30] = 100                                                       # 把所有小于30 的像素都变成100, 用于后面的二传值化
        self.img_tran_R_bin = cv2.warpPerspective(im_bin, self.proj_matrix, (tran_width, tran_height))     # 做透视变换，得到计算透视后的照片

        # im_bin_tran = cv2.warpPerspective(im_bin, self.proj_matrix, (tran_width, tran_height))     # 做透视变换，得到计算透视后的照片
        # print("Type im_bin_tran:", type(im_bin_tran))
        # cv2.imwrite(self.img_tran_R_bin, im_bin_tran)                                   #


        # 透视变换后，照片中心的坐标, 也是地面中心的坐标。 90度 俯视照片
        # logger.info("Camera to Tran GC:" , self.camera_tran_center_distance)
        center_Tran_MC_lat = self.img_all_info["camera_MC_lat"] + self.camera_tran_center_distance * np.cos(yaw * np.pi / 180)
        center_Tran_MC_lng = self.img_all_info["camera_MC_lng"] + self.camera_tran_center_distance * np.sin(yaw * np.pi / 180)
        self.img_all_info["Center_Tran_MC"] = [center_Tran_MC_lat, center_Tran_MC_lng]

        #################################################################################################################
        # LT, LB, RT, RB 四个点旋转之前, 相对于透视变换后的地面中心的XY, X,Y 值 单位：米; X:N 北; Y:E 东
        LTx_tran, LTy_tran = LHG/2, -1 * LWB / 2
        RTx_tran, RTy_tran = LHG/2, LWB/2
        LBx_tran, LBy_tran = -1 * LHG/2, -1 * LWB / 2
        RBx_tran, RBy_tran = -1 * LHG/2, LWB / 2

        # logger.info("LT_tran: %s; LTy_tran: %s;" % (LTx_tran, LTy_tran))
        # logger.info("LB_tran: %s; LBy_tran: %s;" % (LBx_tran, LBy_tran))
        # logger.info("RT_tran: %s; RTy_tran: %s;" % (RTx_tran, RTy_tran))
        # logger.info("RB_tran: %s; RBy_tran: %s;" % (RBx_tran, RBy_tran))
        # logger.info()

        # 计算透视变换后, 并旋转 Yaw 后四角坐标
        [LT_tran_xr, LT_tran_yr] = np.dot(self.RzMat, [LTx_tran, LTy_tran])
        [RT_tran_xr, RT_tran_yr] = np.dot(self.RzMat, [RTx_tran, RTy_tran])
        [LB_tran_xr, LB_tran_yr] = np.dot(self.RzMat, [LBx_tran, LBy_tran])
        [RB_tran_xr, RB_tran_yr] = np.dot(self.RzMat, [RBx_tran, RBy_tran])

        # logger.info("LT_tran_r: %s, %s;" % (LT_tran_xr, LT_tran_yr))
        # logger.info("LB_tran_r: %s, %s;" % (LB_tran_xr, LB_tran_yr))
        # logger.info("RT_tran_r: %s, %s;" % (RT_tran_xr, RT_tran_yr))
        # logger.info("RB_tran_r: %s, %s;" % (RB_tran_xr, RB_tran_yr))

        LT_Tran_MC_lat, LT_Tran_MC_lng = center_Tran_MC_lat + LT_tran_xr, center_Tran_MC_lng + LT_tran_yr
        RT_Tran_MC_lat, RT_Tran_MC_lng = center_Tran_MC_lat + RT_tran_xr, center_Tran_MC_lng + RT_tran_yr
        LB_Tran_MC_lat, LB_Tran_MC_lng = center_Tran_MC_lat + LB_tran_xr, center_Tran_MC_lng + LB_tran_yr
        RB_Tran_MC_lat, RB_Tran_MC_lng = center_Tran_MC_lat + RB_tran_xr, center_Tran_MC_lng + RB_tran_yr
        #################################################################################################################

        # 经过透视变换后，照片四个角的坐标（注意，底角是有黑边的）
        self.img_all_info["LT_lat_lng_MC_Tran"] = self.img_all_info["LT_lat_lng_MC"]
        self.img_all_info["RT_lat_lng_MC_Tran"] = self.img_all_info["RT_lat_lng_MC"]
        self.img_all_info["LB_lat_lng_MC_Tran"] = [2 * self.img_all_info["Center_Tran_MC"][0] - self.img_all_info["RT_lat_lng_MC_Tran"][0],
                                                   2 * self.img_all_info["Center_Tran_MC"][1] - self.img_all_info["RT_lat_lng_MC_Tran"][1]]
        self.img_all_info["RB_lat_lng_MC_Tran"] = [2 * self.img_all_info["Center_Tran_MC"][0] - self.img_all_info["LT_lat_lng_MC_Tran"][0],
                                                   2 * self.img_all_info["Center_Tran_MC"][1] - self.img_all_info["LT_lat_lng_MC_Tran"][1]]

        # logger.info("透视变换后照片中心的坐标:",self.img_all_info["Center_Tran_MC"])
        # logger.info("LT After Tran", self.img_all_info["LT_lat_lng_MC_Tran"], LT_Tran_MC_lat, LT_Tran_MC_lng)
        # logger.info("RT After Tran", self.img_all_info["RT_lat_lng_MC_Tran"], RT_Tran_MC_lat, RT_Tran_MC_lng)
        # logger.info("LB After Tran", self.img_all_info["LB_lat_lng_MC_Tran"], LB_Tran_MC_lat, LB_Tran_MC_lng)
        # logger.info("RB After Tran", self.img_all_info["RB_lat_lng_MC_Tran"], RB_Tran_MC_lat, RB_Tran_MC_lng)

        # 以下用于在QGIS里，标示出各个点。用于测试验证
        with open(self.key_points, "w") as file:
            # 在QGIS里：X: longitude, Y: latitude.
            file.write("X, Y, Seq\n")
            file.write("%s, %s, Camera\n" % (self.img_all_info["camera_MC_lng"],self.img_all_info["camera_MC_lat"]))        # 相机/无人机的位置
            # file.write("%s, %s, GC\n" % (GCMClng, GCMClat))
            file.write("%s, %s, GCT\n" % (self.img_all_info["Center_Tran_MC"][1],self.img_all_info["Center_Tran_MC"][0]))   # 照片透视变换后的地面中心点

            # 透视变换前四个角的坐标，透视变换前后是不变的，注意此时的LB, RB是没有黑边的LB, RB
            file.write("%s, %s, LT\n" % (self.img_all_info["LT_lat_lng_MC"][1], self.img_all_info["LT_lat_lng_MC"][0]))
            file.write("%s, %s, LB\n" % (self.img_all_info["LB_lat_lng_MC"][1], self.img_all_info["LB_lat_lng_MC"][0]))
            file.write("%s, %s, RT\n" % (self.img_all_info["RT_lat_lng_MC"][1], self.img_all_info["RT_lat_lng_MC"][0]))
            file.write("%s, %s, RB\n" % (self.img_all_info["RB_lat_lng_MC"][1], self.img_all_info["RB_lat_lng_MC"][0]))

            # file.write("%s, %s, lto\n" % (ltoMCLng,ltoMCLat))     # 未做Yaw矫正前的 LT, lt original
            # file.write("%s, %s, lbo\n" % (lboMCLng,lboMCLat))     # 未做Yaw矫正前的 LB, lb original
            # file.write("%s, %s, rto\n" % (rtoMCLng,rtoMCLat))     # 未做Yaw矫正前的 RT, rt original
            # file.write("%s, %s, rbo\n" % (rboMCLng,rboMCLat))     # 未做Yaw矫正前的 RB, rb original

            # file.write("%s, %s, TLT\n" % (self.img_all_info["LT_lat_lng_MC_Tran"][1], self.img_all_info["LT_lat_lng_MC_Tran"][0]))      # 透视变换后的 LT', 照片包括黑影部分
            # file.write("%s, %s, TRT\n" % (self.img_all_info["RT_lat_lng_MC_Tran"][1], self.img_all_info["RT_lat_lng_MC_Tran"][0]))      # 透视变换后的 RT', 照片包括黑影部分
            file.write("%s, %s, TLB\n" % (self.img_all_info["LB_lat_lng_MC_Tran"][1], self.img_all_info["LB_lat_lng_MC_Tran"][0]))      # 透视变换后的 LB', 照片包括黑影部分
            file.write("%s, %s, TRB\n" % (self.img_all_info["RB_lat_lng_MC_Tran"][1], self.img_all_info["RB_lat_lng_MC_Tran"][0]))      # 透视变换后的 RB', 照片包括黑影部分



    def get_point_lat_lng_Geo(self, m, n):
        """
        m, n 对应像素坐标系的 宽，高
        计算某个点的经纬度，需要使用到照片的旋转矩阵
        使用几何方法
        """
        pitch = abs(self.img_all_info["GimbalPitchDegree"])     # 相机 pitch 角
        OA = self.img_all_info["RelativeAltitude"]              # 相机的飞行高度
        DM = self.img_all_info["LHA"]
        OE = self.img_all_info["LOA"]


        n = self.img_all_info["height"] - n
        dh = DM / self.img_all_info["height"]
        Dn = n * dh
        nE = (self.img_all_info["height"] / 2 - n) * dh
        # print(self.img_all_info["height"])

        angleJArc =  np.arctan(nE / OE)        # np.arctan 返回的是弧度
        angleJ = angleJArc * 180 / np.pi
        angleK = 90 - angleJ - pitch
        angleKArc = angleK * np.pi / 180

        Os = OA / np.cos(angleKArc)
        Og = Os * np.cos(angleJArc)

        dm = DM * Og / OE

        ddh = dm / self.img_all_info["height"]

        # 计算像素点 m,n 相对于地面中心（照片中心）的 XY 坐标
        X = ddh * n - self.img_all_info["LGB"]          # LGB, 即线段 GB
        Y = ddh * m - self.img_all_info["LWB"] / 2
        # logger.info("n:",n)
        # logger.info("m:",m)
        # logger.info("Os:", Os)
        # logger.info("Og:", Og)
        # logger.info("OE:", OE)
        # logger.info("DM:", DM)
        # logger.info("nE:", nE)
        # logger.info("J:", angleJ)
        # logger.info("K:", angleK)
        # logger.info("dm:", dm)
        # logger.info("ddh:", ddh)
        # logger.info("LGB:", self.img_all_info["LGB"])
        # logger.info("LWB:", self.img_all_info["LWB"])
        # logger.info("X: %s, Y: %s" % (X, Y))

        # 旋转 单位还是 米
        # RX: X 旋转 yaw 度后; RY: Y 旋转 yaw 度后
        [RX, RY] = np.dot(self.RzMat, [X,Y])

        GCTranMClat,GCTranMClng = self.img_all_info["Center_Tran_MC"][0], self.img_all_info["Center_Tran_MC"][1]  # Web Mercator 3857 地面中心点纬度 坐标轴为N, Ground Center latitude
        RX_MC, RY_MC = GCTranMClat + RX , GCTranMClng + RY

        return RX_MC, RY_MC # Web Mercarot 3857

    def get_coners_lat_lng(self,width, height):
        """
        计算四个角点的经纬度，需要使用到照片的旋转矩阵
        """
        pass


    def gen_result(self, output_dir, file_name, result_list, result_type="yolo"):
        """
        1. 生成压缩 JPG;
        2. 计算地理坐标
        3. 生成geo tiff 以及 cog 图片;
        4. 生成 _pts.json;
        """
        # 生成压缩 JPG
        self.gen_compress_jpg(file_name, result_list, result_type=result_type)

        # 计算地理坐标
        self.calculate_image_positions()

        # 生成cog, geotiff
        self.gen_cogtiff(output_dir)

        # 生成geotiff
        self.gen_geotiff(output_dir)

        # 生成 pts.json文件，此文件存放全部被检测到的羊的坐标
        self.gen_result_pts_json(output_dir, file_name, result_list, result_type=result_type)


    def gen_compress_jpg(self, file_name, result_list, result_type="yolo"):
        """
        Create a compress JPG for presenting
        """

        if self.log_level == "debug":
            logger.debug("Creating a Compressed JPG for presenting")
        basename = file_name            # 文件名
        ori_jpg = gdal.Open(self.img)                  # 用原始的JPG生成预览用的压缩 JPG
        width, height, img_channels = ori_jpg.RasterXSize, ori_jpg.RasterYSize, ori_jpg.RasterCount

        driver = gdal.GetDriverByName("GTiff")
        tmp_tiff = os.path.join(self.tmp_folder,  basename + '_tmp.tif')          # 转变成CogTiff前的 原始 tiff照片
        tmp_dataset = driver.Create(tmp_tiff, width, height, img_channels, gdal.GDT_Byte)

        # 读取原图中的每个波段
        in_band_ori1 = ori_jpg.GetRasterBand(1)
        in_band_ori2 = ori_jpg.GetRasterBand(2)
        in_band_ori3 = ori_jpg.GetRasterBand(3)

        # 从每个波段中切需要的矩形框内的数据(注意读取的矩形框不能超过原图大小)
        out_band1 = in_band_ori1.ReadAsArray(0, 0, width, height)
        out_band2 = in_band_ori2.ReadAsArray(0, 0, width, height)
        out_band3 = in_band_ori3.ReadAsArray(0, 0, width, height)

        # 在原始 JPG 图片中用蓝点标记出检测结果
        marker_size = 3
        if result_type == "yolo":
            for dts in result_list:
                # 检测框中心点坐标
                box_center_width  = int((dts["box"]["x1"] + dts["box"]["x2"]) * 0.5)
                box_center_height = int((dts["box"]["y1"] + dts["box"]["y2"]) * 0.5)

                out_band1[box_center_height - marker_size:box_center_height + marker_size, box_center_width - marker_size:box_center_width + marker_size] = 0
                out_band2[box_center_height - marker_size:box_center_height + marker_size, box_center_width - marker_size:box_center_width + marker_size] = 0
                out_band3[box_center_height - marker_size:box_center_height + marker_size, box_center_width - marker_size:box_center_width + marker_size] = 250

        elif result_type == "sahi":
            for dts in result_list:
                ## ObjectPrediction<
                ## bbox: BoundingBox: <(2741.4375915527344, 2739.9431762695312, 2756.602081298828, 2749.43953704834), w: 15.16448974609375, h: 9.496360778808594>,
                ## bbox: list, [minx, miny, maxx, maxy]
                ## mask: None,
                ## score: PredictionScore: <value: 0.6970506310462952>,
                ## category: Category: <id: 0, name: 玉米苗>>

                # 检测框中心点坐标
                box_center_width  = int(dts.bbox.minx + dts.bbox.maxx * 0.5)
                box_center_height = int(dts.bbox.miny + dts.bbox.maxy * 0.5)

                out_band1[box_center_height - marker_size:box_center_height + marker_size, box_center_width - marker_size:box_center_width + marker_size] = 0
                out_band2[box_center_height - marker_size:box_center_height + marker_size, box_center_width - marker_size:box_center_width + marker_size] = 0
                out_band3[box_center_height - marker_size:box_center_height + marker_size, box_center_width - marker_size:box_center_width + marker_size] = 250

        # 将 原图像数据写入 GeoTIFF 预测文件，
        tmp_dataset.GetRasterBand(1).WriteArray(out_band1)
        tmp_dataset.GetRasterBand(2).WriteArray(out_band2)
        tmp_dataset.GetRasterBand(3).WriteArray(out_band3)

        # 生成压缩JPG
        saveOptions = []
        saveOptions.append("QUALITY=20")
        # saveOptions.append("QUALITY=100")
        jpegDriver = gdal.GetDriverByName("JPEG")
        jpegDriver.CreateCopy(self.compress_jpg_path, tmp_dataset, 0, saveOptions)
        jpegDriver.CreateCopy(self.tag_jpg_path, tmp_dataset, 0, saveOptions)

        tmp_dataset = None

        os.remove(tmp_tiff)

        if self.log_level == "debug":
            logger.debug("Finish Creating a Compressed JPG for presenting")



    def gen_cogtiff(self, output_dir, media=False):
        """
        output_dir: 生成的照片图片存放目录
        对透视变换后的JPG照片进行处理
        生成结果文件, 存放在output_dir目录里
        _cog.tif: cogeotif
        """

        if self.log_level == "debug":
            logger.debug("Create a COG Tiff to present in MAP")
        # basename = os.path.basename(result.path)            # 文件名

        # self.img_tran = os.path.join(self.out_folder, os.path.splitext(os.path.basename(img))[0] + '_tran.JPG')
        # img_tran: 原始照片 经过 透视变换后得到的照片。是原始照片的俯视图
        # self.img_tran_ndarray = cv2.warpPerspective(im1, self.proj_matrix, (tran_width, tran_height))     # 做透视变换，得到计算透视后的照片, 不写入磁盘。
        [height, width, img_channels] = self.img_tran_ndarray.shape

        driver = gdal.GetDriverByName("GTiff")

        # self.raw_geotiff_path = os.path.join(out_folder,  os.path.splitext(os.path.basename(img))[0] + '_raw.tif')
        # self.raw_geotiff_path, 未做Yaw角矫正前的 goetiff照片
        ## ******************************************************************
        geotiff_dataset = driver.Create(self.raw_geotiff_path, width, height, img_channels, gdal.GDT_Byte)

        out_band_tran1 = self.img_tran_ndarray[:, :, 0]
        out_band_tran2 = self.img_tran_ndarray[:, :, 1]
        out_band_tran3 = self.img_tran_ndarray[:, :, 2]
        # logger.info("out_band_tran1:", type(out_band_tran1), out_band_tran1.shape)
        # logger.info("out_band_tran2:", type(out_band_tran2), out_band_tran2.shape)
        # logger.info("out_band_tran3:", type(out_band_tran3), out_band_tran3.shape)

        # 将 原图像数据写入 GeoTIFF 预测文件，
        geotiff_dataset.GetRasterBand(1).WriteArray(out_band_tran3)
        geotiff_dataset.GetRasterBand(2).WriteArray(out_band_tran2)
        geotiff_dataset.GetRasterBand(3).WriteArray(out_band_tran1)

        # 定义 GeoTIFF 文件的空间参考（Spatial Reference）空间参照系
        spatial_reference = osr.SpatialReference()
        # spatial_reference.ImportFromEPSG(4326)  # WGS84 EPSG:4326 code
        spatial_reference.ImportFromEPSG(3857)  # 球面墨卡托投影 WGS 84 / Pseudo-Mercator EPSG:3857

        # geotiff_dataset.SetGeoTransform(geotransform)
        geotiff_dataset.SetProjection(spatial_reference.ExportToWkt())
        # self.raw_geotiff_path = os.path.join(out_folder,  os.path.splitext(os.path.basename(img))[0] + '_raw.tif')
        geotiff_dataset.FlushCache()

        # 对 geotiff 进行Yaw角矫正
        # self.rotation(self.raw_geotiff_path, self.rotate_raw_geotiff_path)
        if media:
            self.rotation(self.img_tran, self.rotate_raw_geotiff_path)
        else:
            self.rotation(self.img_tag_tran, self.rotate_raw_geotiff_path)
        translateToCOG(geotiff_dataset, self.raw_cog_tiff_path)

        # 以下两行使用tif2cog.py
        raw_geotiff_dataset = gdal.Open(self.rotate_raw_geotiff_path, gdal.GA_ReadOnly)
        rotate_raw_geotiff_dataset = getTifDataset(raw_geotiff_dataset, 4326)      # 3857, 4326

        translateToCOG(rotate_raw_geotiff_dataset, self.rotate_cog_tiff_path)

        if self.log_level == "debug":
            logger.debug("Finish Creating a COG Tiff to present in MAP")


    def gen_geotiff(self, output_dir, media=False):
        # media: 当导入照片到媒体库时，media = True

        if self.log_level == "debug":
            logger.debug("Create a Geo Tiff")

        driver = gdal.GetDriverByName("GTiff")
        # 定义 GeoTIFF 文件的空间参考（Spatial Reference）空间参照系
        spatial_reference = osr.SpatialReference()
        # spatial_reference.ImportFromEPSG(4326)  # WGS84 EPSG:4326 code
        spatial_reference.ImportFromEPSG(3857)  # 球面墨卡托投影 WGS 84 / Pseudo-Mercator EPSG:3857

        if media:
            [height, width, img_channels] = self.img_tran_ndarray.shape
            geotiff_dataset = driver.Create(self.tag_geotiff_path, width, height, img_channels, gdal.GDT_Byte)

            # 将 原图像数据写入 GeoTIFF 预测文件，
            geotiff_dataset.GetRasterBand(1).WriteArray(self.img_tran_ndarray[:, :, 2])
            geotiff_dataset.GetRasterBand(2).WriteArray(self.img_tran_ndarray[:, :, 1])
            geotiff_dataset.GetRasterBand(3).WriteArray(self.img_tran_ndarray[:, :, 0])

            geotiff_dataset.SetProjection(spatial_reference.ExportToWkt())
            geotiff_dataset.FlushCache()

            # 对 geotiff 进行Yaw角矫正
            self.rotation(self.img_tran, self.rotate_tag_geotiff_path)

        else:
            [height, width, img_channels] = self.tag_img_tran_ndarray.shape
            tag_geotiff_dataset = driver.Create(self.tag_geotiff_path, width, height, img_channels, gdal.GDT_Byte)

            # 将 原图像数据写入 GeoTIFF 预测文件，
            tag_geotiff_dataset.GetRasterBand(1).WriteArray(self.tag_img_tran_ndarray[:, :, 2])
            tag_geotiff_dataset.GetRasterBand(2).WriteArray(self.tag_img_tran_ndarray[:, :, 1])
            tag_geotiff_dataset.GetRasterBand(3).WriteArray(self.tag_img_tran_ndarray[:, :, 0])

            tag_geotiff_dataset.SetProjection(spatial_reference.ExportToWkt())
            tag_geotiff_dataset.FlushCache()

            # 对 geotiff 进行Yaw角矫正
            self.rotation(self.img_tag_tran, self.rotate_tag_geotiff_path)

        if self.log_level == "debug":
            logger.debug("Finish Creating a Geo Tiff")


    def gen_result_pts_json(self, output_dir, file_name, result_list, result_type="yolo"):
        """
        result: yolo检测完成后返回的result
        output_dir: 生成的照片图片存放目录
        对透视变换后的JPG照片进行处理
        生成结果文件, 存放在output_dir目录里
        detected_pts.json json文件，标识了识别的标点数量和位置。
        result.tif 打上结果标点之后的，geotiff格式的原始图片。
        result.jpg 压缩之后便于web展示的图片。

        """

        if self.log_level == "debug":
            logger.debug("Create a JSON file to present the position of detected Objects. Create a COG Tiff to present in MAP")

        pts_path = os.path.join(output_dir,file_name.split('.')[0]+'_pts.json')

        """
        # 生成以下 json格式的文件
        {
            "count": 2,
            "coordinates": [
                {
                    "lat": 39.874509379697585,
                    "lng": 108.49329464041566
                }
        }
        """

        res_pts = {}    # 用于生成json的字典
        res_pts_coordinates = []
        res_pts["count"] = len(result_list)

        # 在旋转完成后，把每个检测点的像素坐标转换为X, Y 坐标
        with open(self.sheep_points, "w") as file:
            # 在QGIS里：X: longitude, Y: latitude.
            file.write("X, Y, Seq\n")

        i = 1
        for dts in result_list:
            # 检测框中心点坐标
            if result_type == "yolo":
                box_center_width  = int((dts["box"]["x1"] + dts["box"]["x2"]) * 0.5)
                box_center_height = int((dts["box"]["y1"] + dts["box"]["y2"]) * 0.5)
            elif result_type == "sahi":
                # 检测框中心点坐标
                box_center_width  = int(dts.bbox.minx + dts.bbox.maxx * 0.5)
                box_center_height = int(dts.bbox.miny + dts.bbox.maxy * 0.5)

            pos = [box_center_width, box_center_height]
            box_center_width_tran, box_center_height_tran = self.cvt_pos(pos, self.proj_matrix)         # 通过透视变换矩阵proj_matrix, 计算出 box 中点经过透视变换后的像素坐标
            box_center_width_tran, box_center_height_tran = int(box_center_width_tran), int(box_center_height_tran)
            # print(box_center_width_tran, box_center_height_tran)

            LHG = self.img_all_info["LHG"]
            LWB = self.img_all_info["LWB"]
            GCTMClat = self.img_all_info["Center_Tran_MC"][0]  # Web Mercator 3857 地面中心点纬度 坐标轴为N, Ground Center latitude
            GCTMClng = self.img_all_info["Center_Tran_MC"][1]  # WGS Mercator 3857 地面中心点经度 坐标轴为E, Ground Center longitude

            tran_width = self.img_all_info["tran_width"]        # 透视变换后的分辨率
            tran_height = self.img_all_info["tran_height"]      # 透视变换后的分辨率

            X_tran = LHG / 2 - LHG * box_center_height_tran / tran_height            # row, lat, 透视变换后的X
            Y_tran = LWB * box_center_width_tran / tran_width - LWB / 2              # col, lng, 透视变换后的Y

            [X_rotate, Y_rotate] = np.dot(self.RzMat, [X_tran, Y_tran])             # 旋转
            X_lat, Y_lng = GCTMClat + X_rotate, GCTMClng + Y_rotate                 # 平移

            with open(self.sheep_points, "a") as file:
                # 在QGIS里：X: longitude, Y: latitude.
                if i == 1:
                    file.write("%s, %s, %s\n" % (Y_lng, X_lat, i))
                if i == len(result_list):
                    file.write("%s, %s, %s\n" % (Y_lng, X_lat, i))
                else:
                    file.write("%s, %s, \n" % (Y_lng, X_lat))

            # print(lat,lng)
            i += 1

            # Web Mercator 3857 坐标转换成 WGS 4326 坐标
            dts_wgs_lat_lng = self.webMercator_to_WGS84([X_lat, Y_lng])
            dts_lat_lng = {"lat": dts_wgs_lat_lng[0], "lng": dts_wgs_lat_lng[1]}
            res_pts_coordinates.append(dts_lat_lng)
            #################################################################################################

        res_pts["coordinates"] = res_pts_coordinates

        # 在json最后面写入照片左上角的坐标
        # Web Mercator 3857 坐标转换成 WGS 4326 坐标
        latlng = [self.img_all_info["LT_lat_lng_MC"][0], self.img_all_info["LT_lat_lng_MC"][1]]
        wgs_latlng = self.webMercator_to_WGS84([latlng[0], latlng[1]])
        res_pts["latlng"] = {"lat": wgs_latlng[0], "lng": wgs_latlng[1]}

        json_data = json.dumps(res_pts,indent=2)

        # 写入 json 文件
        with open(pts_path, 'w') as file:
            file.write(json_data)

        if self.log_level == "debug":
            logger.debug("Finish Creating a JSON file of detected Objects.")





    def cvt_pos(self, pos, cvt_mat_t):
        """
        pos: 原图的像素坐标
        cvt_mat_t: 透视变换矩阵
        x,y: 原像素坐标经过透视变换后，在新图片中的新像素坐标
        """
        u,v = pos[0], pos[1]
        x = (cvt_mat_t[0][0] * u + cvt_mat_t[0][1] * v + cvt_mat_t[0][2]) / (cvt_mat_t[2][0] * u + cvt_mat_t[2][1] * v + cvt_mat_t[2][2])
        y = (cvt_mat_t[1][0] * u + cvt_mat_t[1][1] * v + cvt_mat_t[1][2]) / (cvt_mat_t[2][0] * u + cvt_mat_t[2][1] * v + cvt_mat_t[2][2])
        return x, y

    def rotation(self,input_file,output_file):
        """
        input:
        output:

        1: 旋转照片, Yaw矫正. 自适应调整图片大小
        2: 裁剪照片，裁掉多余的黑色
            1) 把照片二值化
            2) 寻找最大轮廓
            3) 沿最大轮廓边界裁剪原旋转后的照片
        3:
        """
        [lat, lng] = self.img_all_info["Center_Tran_MC"]         # 透视变换后照片中心的坐标

        # roll = self.img_all_info["GimbalRollDegree"]               # 云台 Roll 角, 翻滚角
        # pitch = self.img_all_info["GimbalPitchDegree"]             # 云台 Pitch 角, 仰角
        # gimbalyaw = self.img_all_info["GimbalYawDegree"]                 # 云台 Yaw 偏航角
        # flightroll = self.img_all_info["FlightRollDegree"]               # 飞机 Roll 角, 翻滚角
        # flightpitch = self.img_all_info["FlightPitchDegree"]             # 飞机 Pitch 角, 仰角
        # flightyaw = self.img_all_info["FlightYawDegree"]                 # 飞机 Yaw 偏航角
        # yaw = self.img_all_info["Yaw"]                 # 云台 Yaw 偏航角
        rotateyaw = self.img_all_info["RotateYaw"]                 # 云台 Yaw 偏航角

        # img = cv2.imdecode(np.fromfile(self.img_tran, dtype=np.uint8),-1)                  # imdecode得到的影像波段顺序是RGB
        img = cv2.imdecode(np.fromfile(input_file, dtype=np.uint8),-1)                  # imdecode得到的影像波段顺序是RGB
        # img = self.img_tran_ndarray                  # imdecode得到的影像波段顺序是RGB

        # 填充黑色
        # print("img.Shape:", img.shape[:2])
        rotated_image = self.rotate_image(img, - rotateyaw)
        rotated_image_tran_bin = self.rotate_image(self.img_tran_R_bin, - rotateyaw)
        # print("Shape of Rotate:", rotated_image.shape[:2])
        # cv2.imwrite("02-Rotate-IMG_Tran.JPG",rotated_image)
        # cv2.imwrite("02-Rotate-IMG_Tran_Bin.JPG",rotated_image_tran_bin)
        # cv2.imwrite("02-TMP_Rotate-IMG.JPG",tmp_rotated_image)

        # Temp_Arr.Shape: (9236, 10560)
        # cropped_image = self.find_edge(rotated_image, tmp_rotated_image)               # 对经过旋转的照片进行裁剪，切除原照片场景周围的黑框
        cropped_image = self.find_edge(rotated_image, rotated_image_tran_bin)               # 对经过旋转的照片进行裁剪，切除原照片场景周围的黑框
        # cv2.imwrite("04-Cropped-IMG_Tran.JPG", cropped_image)
        # print("Shape of Cropped:", cropped_image.shape[:2])
        new_height,new_width = cropped_image.shape[:2]

        # 照片经过透视变换 + 偏航角矫正后 + 裁剪多余黑边 后，包括一些黑边的整体照片
        max_lat = max([self.img_all_info["LT_lat_lng_MC"][0], self.img_all_info["LB_lat_lng_MC"][0], self.img_all_info["RT_lat_lng_MC"][0], self.img_all_info["RB_lat_lng_MC"][0]])
        min_lat = min([self.img_all_info["LT_lat_lng_MC"][0], self.img_all_info["LB_lat_lng_MC"][0], self.img_all_info["RT_lat_lng_MC"][0], self.img_all_info["RB_lat_lng_MC"][0]])
        max_lng = max([self.img_all_info["LT_lat_lng_MC"][1], self.img_all_info["LB_lat_lng_MC"][1], self.img_all_info["RT_lat_lng_MC"][1], self.img_all_info["RB_lat_lng_MC"][1]])
        min_lng = min([self.img_all_info["LT_lat_lng_MC"][1], self.img_all_info["LB_lat_lng_MC"][1], self.img_all_info["RT_lat_lng_MC"][1], self.img_all_info["RB_lat_lng_MC"][1]])

        full_top_left = [max_lat, min_lng]
        full_top_right = [max_lat, max_lng]
        full_bottom_left = [min_lat, min_lng]
        full_bottom_right = [min_lat, max_lng]

        # x_res = self.img_all_info["LWA"]/ self.img_all_info["width"]        # 单位: 米 meter, 做透视变换时，近边不变
        # x_res = self.img_all_info["LWM"]/ self.img_all_info["width"]        # 单位: 米 meter, 做透视变换时，中边不变
        # x_res = self.img_all_info["LWB"]/ self.img_all_info["width"]        # 单位: 米 meter, 做透视变换时，远边不变
        x_res = abs((max_lng - min_lng)) / new_width
        y_res = abs((max_lat - min_lat)) / new_height

        # 照片经过透视变换 + 偏航角矫正后 + 裁剪多余黑边 后，包括一些黑边的整体照片
        with open(self.key_points, "a") as file:
            # 在QGIS里：X: longitude, Y: latitude.
            file.write("%s, %s, flt\n" % (full_top_left[1], full_top_left[0]))
            file.write("%s, %s, frt\n" % (full_top_right[1], full_top_right[0]))
            file.write("%s, %s, flb\n" % (full_bottom_left[1], full_bottom_left[0]))
            file.write("%s, %s, frb\n" % (full_bottom_right[1], full_bottom_right[0]))


        self.geotransform = [
            full_top_left[1],  # 0：图像左上角的X坐标, latitude 纬度;
            abs(full_top_right[1] - full_top_left[1]) / new_width,  # 1：图像东西方向分辨率;
            0.0,  # 2：旋转角度，如果图像北方朝上，该值为0;
            # self.img_all_info["GimbalYawDegree"],  # 2：旋转角度，如果图像北方朝上，该值为0;
            # self.img_all_info["Yaw"],  # 2：旋转角度，如果图像北方朝上，该值为0;
            full_top_left[0],  # 3：图像左上角的Y坐标, longitude 经度;
            0.0,  # 4：旋转角度，如果图像北方朝上，该值为0;
            -1 * abs(full_bottom_left[0] - full_top_left[0]) / new_height  # 5：图像南北方向分辨率;
        ]
        # print("GeoTransform in Rotate:", self.geotransform)

        srs = osr.SpatialReference() # 空间参照系
        # srs.ImportFromEPSG(4326)    # WGS84, EPSG:4326
        srs.ImportFromEPSG(3857)  # 球面墨卡托投影 WGS 84 / Pseudo-Mercator EPSG:3857

        # export the jpg tif
        driver = gdal.GetDriverByName('GTiff')
        # rotate_out_tif = driver.Create(self.rotate_out_name, new_width, new_height, 3, eType=gdal.GDT_Byte)
        rotate_out_tif = driver.Create(output_file, new_width, new_height, 3, eType=gdal.GDT_Byte)
        j=2
        for i in range(3):

            band = rotate_out_tif.GetRasterBand(i + 1).WriteArray(cropped_image[:,:,j-i])
            # band = rotate_out_tif.GetRasterBand(i + 1).WriteArray(rotated_image[:,:,j-i])
            del band

        rotate_out_tif.SetProjection(srs.ExportToWkt())
        rotate_out_tif.SetGeoTransform(self.geotransform)
        rotate_out_tif.FlushCache()

    def find_edge(self,arr, arr_tran_bin):
        """
        arr: 照片
        """
        # 删减图像中的黑框
        # tmp_arr = arr[:,:,0]           # 影像波段顺序是R  黑色: [0,0,0]; 白色: [255,255,255]
        # print("Temp_Arr.Shape:", tmp_arr.shape)
        # Padded_Image.Shape: (9236, 10560, 3)
        # Rotate_Image.Shape: (9236, 10560, 3)
        # Temp_Arr.Shape: (9236, 10560)

        # 二值化
        """
        ret, dst = cv2.threshold(src, thresh, maxval, type[, dst])
        参数:
        src：源图像，必须是单通道灰度图像。
        thresh：阈值，用于确定像素是否应该被视为前景或背景。
        maxval：二值化操作中使用的最大值，通常设为255。
        type：阈值类型，定义了多种二值化方法，包括：
        cv2.THRESH_BINARY：简单二值化。
        cv2.THRESH_BINARY_INV：反向二值化。
        cv2.THRESH_TRUNC：截断二值化，所有高于阈值的像素被设为阈值。
        cv2.THRESH_TOZERO：高于阈值的像素被设为0。
        cv2.THRESH_TOZERO_INV：低于阈值的像素被设为0。
        cv2.THRESH_OTSU：使用Otsu's方法自动确定阈值。
        cv2.THRESH_TRIANGLE：使用三角方法自动确定阈值。
        dst：（可选）目标图像，用于存储二值化结果。
        
        cv2.THRESH_BINARY：大于阈值的像素设置为最大值，小于等于阈值的像素设置为0。
        cv2.THRESH_BINARY_INV：大于阈值的像素设置为0，小于等于阈值的像素设置为最大值。
        cv2.THRESH_TRUNC：大于阈值的像素设置为阈值，小于等于阈值的像素保持不变。
        cv2.THRESH_TOZERO：大于阈值的像素保持不变，小于等于阈值的像素设置为0。
        cv2.THRESH_TOZERO_INV：大于阈值的像素设置为0，小于等于阈值的像素保持不变
        """
        # _, thresh = cv2.threshold(arr, 1, 255, cv2.THRESH_BINARY)
        _, thresh = cv2.threshold(arr_tran_bin, 1, 255, cv2.THRESH_BINARY)
        # cv2.imwrite("03-IMG_Tran_Binary.Thresh.JPG",thresh)
        # cv2.imshow("Binary Thresh",thresh)
        # cv2.waitKey(0)

        # 找到轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # print("Contours:",contours)

        # 如果没有检测到轮廓，则退出
        if not contours:
            logger.error("No contours found.")
            exit()

        # 获取最大轮廓
        c = max(contours, key=cv2.contourArea)
        # print("Max c:", c)
        # 计算边界框
        x, y, w, h = cv2.boundingRect(c)
        # print("X, Y, W, H:",x, y, w, h)
        cropped_image = arr[y:y+h, x:x+w,:]
        # plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
        # plt.show()
        return cropped_image

    def rotate_image(self, image, yaw):
        # 获取图像尺寸
        # 自适应大小
        # height, width = image.shape[:2]
        rows, cols = image.shape[:2]

        # 计算旋转中心
        # center = (width // 2, height // 2)
        center = (cols // 2, rows // 2)

        # 使用CV2旋转照片
        # 第一个参数旋转中心，第二个参数旋转角度，第三个参数：缩放比例

        self.rotation_matrix = cv2.getRotationMatrix2D(center, yaw, 1.0)        # 计算旋转矩阵

        # 自适应图片边框大小
        cos = np.abs(self.rotation_matrix[0, 0])
        sin = np.abs(self.rotation_matrix[0, 1])
        new_w = rows * sin + cols * cos
        new_h = rows * cos + cols * sin
        self.rotation_matrix[0, 2] += (new_w - cols) * 0.5
        self.rotation_matrix[1, 2] += (new_h - rows) * 0.5
        w = int(np.round(new_w))
        h = int(np.round(new_h))
        rotated_image = cv2.warpAffine(image, self.rotation_matrix, (w, h))     # 应用偏航旋转

        return rotated_image


def get_file_names(file_dir, file_types):
    """
    搜索指定目录下具有给定后缀名的文件，不包括子目录。

    参数:
    file_dir (str): 目录路径。
    file_types (list[str] or str): 后缀名列表或单个后缀名（如 ['.txt', '.py'] 或 '.txt'）。

    返回:
    list[str]: 匹配的文件完整路径列表。
    """
    if isinstance(file_types, str):
        # 如果只传入了一个后缀名，将其转换为列表
        file_types = [file_types]

    # 使用glob模块搜索文件
    file_paths = []
    for file_type in file_types:
        # 使用glob的通配符模式搜索文件
        pattern = os.path.join(file_dir, '*' + file_type)
        file_paths.extend(glob.glob(pattern))
    filter_path = []
    for file in file_paths:
        if file not in filter_path:
            filter_path.append(file)
    return filter_path


def main(inpath, outpath):

    if os.path.exists(outpath) is False:
        logger.warning("Path: does not exists, try to create the path" % outpath)
        os.makedirs(outpath)

    file_types = ['.JPG', '.jpg']  #
    isfile = os.path.isfile(inpath)
    if isfile:
        """
        inpath is a file, not a dir
        """
        file_type = os.path.splitext(inpath)[-1]
        if file_type == '.JPG' or file_type == '.jpg':
            IMG = imgProc(inpath, outpath)
            IMG.calculate_image_positions()
            IMG.collect_info()

        else:
            logger.error("That file is not JPG: %s" % inpath)
    else:
        """
        inpath is a dir
        """
        file_list1 = get_file_names(inpath, file_types)
        for file in file_list1:
            IMG = imgProc(file, outpath)
            IMG.calculate_image_positions()
            IMG.collect_info()



if __name__ == '__main__':

    # path="D:\ChenQiu\DrLong\牛羊马放牧\羊"
    input_path = "D:/ChenQiu/Project/cropmirror/counting/counting/algoyolo/sheep_dataset/test/images"
    output_path = "D:/ChenQiu/Project/cropmirror/counting/counting/algoyolo/sheep_dataset/results"
    main(input_path, output_path)