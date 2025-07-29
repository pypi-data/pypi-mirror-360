# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# SAHI 预测时，必须把整个图像加载到内存中。在处理超大图像时，内存占用会非常大。
@prgram: YOLO prediction for 玉米苗计数
@time: 2025-04-28 17:40
@author: Peng ChenQiu 

changelog:
- 2025-04-28 17:40: 创建文件。
"""

import json
# import logging
# from loguru import logger
import os
# from datetime import datetime

import torch
# from osgeo import gdal
# from ultralytics import YOLO
# import sahi


from ..utils import imageProc       # 用于CropMirror
from ..utils import tiffProc       # 用于CropMirror
# import imageProc                # 用于直接测试
# import tiffProc                 # 用于直接测试


_MODEL_LIST = {
    # 1: 0.002 < GSD
    # 2: 0.002 <= GSD < 0.003
    # 3: 0.005 <= GSD < 0.004
    # 4: 0.004 <= GSD < 0.005
    # 5: 0.005 <= GSD
    # "1": "gsd1.pt",      # 已训练
    # "2": "gsd2.pt",      # 已训练
    # "3": "gsd3.pt",      # 已训练
    # "4": "gsd4.pt",      # 已训练
    # "5": "gsd5.pt"       # 已训练
    "1": "corn.pt",      # 已训练
    "2": "corn-gsd0.000-0.002.pt",      # 已训练
    "3": "corn-gsd0.003-0.004.pt",      # 已训练
    "4": "corn.pt",      # 已训练
    "5": "corn.pt",       # 已训练
    "default": "corn-20250627.pt"       # 已训练
    # "default": "kaitu-corn-0.446.pt"       # 用于KaiTu测试
}


def process_file(model_dir, input_file, output_dir):
    file_name = os.path.basename(input_file)
    # logging.info("%s: Start to Process...... =================================================" % file_name)
    # logger.info(f"Model Dir Process File: {model_dir}")

    if file_name.rsplit('.', 1)[-1].lower() in ['jpg','jpeg']:
        try:
            IMG = imageProc.imgProc(input_file, output_dir)
            # IMG = imageProc.imgProc(input_file, output_dir, loglevel="debug")
            """
            1: 0.000 < GSD <0.001
            2: 0.002 <= GSD < 0.003
            3: 0.005 <= GSD < 0.004
            4: 0.004 <= GSD < 0.005
            5: 0.005 <= GSD
            """
            # logger.info("%s: GSD: %s" % (file_name, IMG.img_all_info["gsd"]))
            # cur_dir = os.getcwd()
            # logger.info(cur_dir)
            if IMG.img_all_info["gsd"] < 0.002:
                model_file = os.path.join(model_dir, _MODEL_LIST["1"])
            elif 0.02 <= IMG.img_all_info["gsd"] < 0.003:
                model_file = os.path.join(model_dir, _MODEL_LIST["2"])
            elif 0.03 <= IMG.img_all_info["gsd"] < 0.004:
                model_file = os.path.join(model_dir, _MODEL_LIST["3"])
            elif 0.04 <= IMG.img_all_info["gsd"] < 0.005:
                model_file = os.path.join(model_dir, _MODEL_LIST["4"])
            elif 0.05 <= IMG.img_all_info["gsd"]:
                model_file = os.path.join(model_dir, _MODEL_LIST["5"])
            else:
                model_file = os.path.join(model_dir, _MODEL_LIST["default"])
                # model_file = os.path.join(model_dir, _MODEL_LIST["5"])

            # result = process_sahi(model_file=model_file, input_file=input_file, output_dir=output_dir)
            # model_file = "D:/ChenQiu/Project/MAF-YOLOv2/runs/detect/train2/weights/best.pt"
            # model_file = "D:/ChenQiu/Project/corn_zzgj/code/runs/detect/train3/weights/best.pt"
            # logger.info("Image: %s: Model: %s" % (file_name, model_file))
            # process_sahi(input_file=None, model_file=None, results_dir=None, detection_jpg_name=None):
            # logging.info(f"Start Predicting on {file_name}")
            result = process_sahi(model_file=model_file, input_file=input_file)
            result_list = result.object_prediction_list
            # logging.info(f"Finished Predicting on {file_name}")
            # logging.info(f"Start Post Processing on {file_name}")
            IMG.gen_result(output_dir, file_name, result_list, result_type="sahi")
            # logging.info(f"Finished Post processing on {file_name}")

        # except Exception as e:
        #     logger.error("%s: Error occur when processing this image!" % file_name)
        #     logger.error(e)  # 捕获所有异常并忽略，这通常不是一个好的做法，应该明确指定要捕获的异常
        #     logger.error("%s: End Processing with Error ===============================\n" % file_name)
        #     raise e

        finally:
            IMG.cleanup()
        # logger.info("%s: End Processing =========================================================\n" % file_name)

    elif file_name.rsplit('.', 1)[-1].lower() in ['tif','tiff']:

        ### 需要从拼接图像以及其附属文件中获取 GSD信息。

        model_file = os.path.join(model_dir, _MODEL_LIST["default"])            ### 暂时没有GSD信息，先使用默认的 model
        # logger.info("%s: Model: %s" % (file_name, model_file))
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        # logging.info(f"Start predicting on {file_name}")
        result = process_sahi(model_file=model_file, input_file=input_file)
        result_list = result.to_coco_predictions() 

        # # 保存COCO格式JSON文件
        # coco_json_path = os.path.join(output_dir, f"{base_name}_coco.json")
        # with open(coco_json_path, 'w') as f:
        #     json.dump(result_list, f)

        # logging.info(f"Finished predicting on {file_name}")

        # logging.info(f"Start Post processing on {file_name}")
        # 生成标GeoTIFF
        raw_tif_path = os.path.join(output_dir, f"{base_name}_raw.tif")
        # tiffProc.create_detection_geotiff(result_list, input_file, raw_tif_path)
        tiffProc.create_detection_geotiff(input_file, raw_tif_path)

        # 生成COG GeoTIFF
        cog_tif_path = os.path.join(output_dir, f"{base_name}_cog.tif")
        tiffProc.convert_to_cog(input_file, cog_tif_path, compress="JPEG", quality=75, block_size=512)        ### 使用原始tiff, 压缩算法:JPEG; block size = 512
        
        # 生成JPG图像
        jpg_path = os.path.join(output_dir, f"{base_name}.jpg")
        tiffProc.convert_to_jpg(raw_tif_path, jpg_path)
    
        # 生成坐标JSON
        json_path = os.path.join(output_dir, f"{base_name}_pts.json")
        tiffProc.create_detection_json(result_list, input_file, json_path)
        # logging.info(f"Finished Post processing on {file_name}")


# def process_sahi(input_file=None, model_file=None, results_dir, detection_jpg_name):
# PIL 加载图像, 使用惰性加载, 避免内存溢出
def process_sahi(input_file=None, model_file=None):
    """运行YOLO检测并返回结果列表"""
    from sahi import AutoDetectionModel
    from sahi.predict import get_sliced_prediction
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None  # 禁用限制

    # logger.info(f"process_sahi Model File: {model_file}")
    img = Image.open(input_file)
    
    # 处理各种图像格式
    if img.mode not in ['RGB']:
        try:
            # 尝试转换为RGB
            img = img.convert('RGB')
        except Exception as e:
            print(f"图像格式转换失败: {img.mode} -> RGB")
            print(f"错误信息: {str(e)}")
            raise e

    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    detection_model = AutoDetectionModel.from_pretrained(
        model_type='ultralytics',
        model_path=model_file,
        confidence_threshold=0.2,
        device=device,
    )
    slice_result = get_sliced_prediction(
        # input_file,   ### 使用原始图像
        img,    ### 使用PIL 惰性加载图像
        detection_model,
        slice_height=1280,
        slice_width=1280,
        # slice_height=320, # KaiTu 测试
        # slice_width=320, # KaiTu 测试
        overlap_height_ratio=0.05,
        overlap_width_ratio=0.05,
        exclude_classes_by_id=[1,2,3,4,5],      ### 只检测玉米苗
        verbose=0
    )
    
    # slice_result.export_visuals(export_dir=results_dir, hide_labels=True, hide_conf=True, file_name=detection_jpg_name, text_size=1.0, rect_th=2, export_format="jpg")
    # return slice_result.to_coco_predictions()     # 返回coco 格式的结果
    return slice_result

# run_sahi(input_path=input_path, output_path=output_dir)
def run_sahi(model_dir=None, input_path=None, output_dir=None):
    """
    model_dir: model所在目录
    input_path: 单个图像或者包含图像的目录。
    """
    if os.path.isdir(input_path):
        for filepath, dirnames, filenames in os.walk(input_path):
            for filename in filenames:
                if filename.rsplit('.', 1)[-1].lower() in ['jpg','jpeg','tif','tiff']:
                    input_file = os.path.join(filepath, filename)
                    process_file(model_dir, input_file, output_dir)
    else:
        filename = input_path
        if filename.rsplit('.', 1)[-1].lower() in ['jpg','jpeg','tif','tiff']:
            process_file(model_dir, input_path, output_dir)


if __name__ == '__main__':

    # input_path = "D:/ChenQiu/DrLong/sheep_crowd_counting/sheep_dataset/test/images"
    # input_path = "D:/ChenQiu/Project/cropmirror/counting/counting/sahi_predict/DJI_20250425165659_0059_D.JPG"
    # input_path = "D:/ChenQiu/Project/cropmirror/counting/counting/sahi_predict/corn_20250501.tif"
    input_path = "D:/ChenQiu/Project/CropMirrorDataSets/corn_dataset_heshan_20250318_12/test/images/DJI_20240622113736_0160.JPG"
    # output_dir = "results-" + datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_dir = "results"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    # model_dir = "D:/ChenQiu/Project/cropmirror/counting/counting/algoyolo/yolopt/" # ../../yoloqt
    model_dir = "./models/" # ../../yoloqt
    # model_file = "D:/ChenQiu/Project/corn_zzgj/code/runs/detect/train3/weights/best.pt"
    run_sahi(model_dir=model_dir, input_path=input_path, output_dir=output_dir)

    # get_img_info_only()

    # PT 转 onnx
    # yolo export model=./best.pt format=onnx opset=12
