import os
from loguru import logger

from . import imageProc
# from ..algoyolo import imageProc
# import imageProc                # 用于直接测试


def jpgtocog(input_file, output_path):
    """
    将jpg转为cog文件
    :param in_file: 输入dataset
    :param out_path: 输出路径
    :return:
    """

    # logger.info("Input File: %s" % input_file)
    # logger.info("Output Path: %s" % output_path)
    basename = os.path.basename(input_file)
    out_dir = os.path.dirname(output_path)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir,exist_ok=True)

    try:
        # IMG = imageProc.imgProc(input_file, output_path, loglevel="debug")
        IMG = imageProc.imgProc(input_file, output_path)
        # media: 当在上传照片到媒体库时调用，media=True
        IMG.calculate_image_positions(media=True)
        # IMG.gen_geotiff(output_path, media=True)
        IMG.gen_cogtiff(output_path, media=True)

    except Exception as e:
        logger.error("%s: Error occur when processing this image!" % basename)
        logger.error(e)  # 捕获所有异常并忽略，这通常不是一个好的做法，应该明确指定要捕获的异常
        logger.error("%s: End Processing with Error ===============================\n" % basename)
        print(e)
        raise e

    finally:

        IMG.cleanup(media=False)     # 添加照片到媒体库时，media=True, 做对应有clean up


if __name__ == '__main__':

    # 定义JPG图像文件的路径和输出的TIFF文件名
    # jpg_file = 'DJI_20230311165059_0001_D.JPG'
    # jpg_file = 'DJI_20240306151938_0045_D.JPG'
    jpg_file = "DJI_20240306160334_0176_D.JPG"
    output_path = 'D:/ChenQiu/Project/cropmirror/counting/counting/algoyolo/Test/'
    # logger.info(jpg_file)
    jpgtocog(jpg_file, output_path)

