# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@prgram: YOLO prediction for sheep counting
@time: 2025-06-23 12:00:00
@author: Peng ChenQiu 

changelog:
2025-06-23 12:00, 创建文件, 用于切片预测。
2025-06-24 11:00, 优化custom_nms_postprocess。
2025-06-24 11:40, 新函数run_slicing，用于对外调用。
2025-06-24 14:00, 优化run_slicing，增加详细统计信息。
2025-06-30 10:00, 修改结构，集成到counting项目中。
2025-07-01 01:00, 只对重叠区域进行NMS，减少计算量，提高效率。清除重复定义的函数。
2025-07-01 22:00, run_slicing增加参数local_run，用于本地测试。
2025-07-02 01:00, 不再保存shp, 改为保存geojson。
2025-07-02 10:00, 对重叠区域的检测点，生成geojson。- 未完成
2025-07-03 02:00, run_slicing, 直接复制输入tif 为 _raw.tif. 不重新生成。节省时间。

"""

import os
import gc
import time
import numpy as np
import torch
import json
from datetime import datetime
from sahi.slicing import get_slice_bboxes
from sahi.prediction import ObjectPrediction
from ultralytics import YOLO
from typing import List, Optional, Tuple, Dict, Any
import cv2
import psutil
import rasterio
from rasterio.transform import from_bounds
from rasterio.warp import transform_bounds
from rasterio.crs import CRS
from rasterio.windows import Window
from osgeo import gdal
import tifffile
import shutil

from ..utils import download

_CLASS_LIST = {
    "玉米苗": 0,
    "杂草1": 1,
    "杂草2": 2,
    "杂草3": 3,
    "杂草4": 4,
    "杂草5": 5,
    "杂草6": 6,
    "杂草7": 7
}

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
    # "default": "corn.pt"       # 已训练
    "default": "corn-20250627.pt",       # 已训练
    "download_url": "https://cropmirror-sharedata.obs.cn-north-4.myhuaweicloud.com/counting/slice-pt/corn.pt"
}

# 配置参数
TILE_SIZE = 1280  # 切片大小
OVERLAP_RATIO = 0.02  # 切片重叠比例
MEMORY_LIMIT = 6 * 1024**3  # 6GB内存限制
CONFIDENCE_THRESHOLD = 0.3  # 检测置信度阈值
# MODEL_PATH = "yolov8n.pt"  # YOLOv8模型路径
# MODEL_PATH = "D:/ChenQiu/Project/cropmirror/ai-engine-local/_internal/model/cornpt/kaitu-corn-0.446.pt"
MODEL_PATH = "D:/ChenQiu/Project/cropmirror/ai-engine-local/_internal/model/cornpt/corn.pt"

class YOLOv8Model:
    """
    YOLOv8模型包装器，适配SAHI工作流，支持批量推理
    """
    def __init__(self, model_path: str, confidence_threshold: float = 0.3, device: str = None):
        """
        初始化YOLOv8模型
        
        Args:
            model_path: 模型文件路径
            confidence_threshold: 置信度阈值
            device: 设备类型 ('auto', 'cpu', 'cuda', 'mps')，None表示自动选择
        """
        # 自动选择最佳设备
        if device is None:
            device = self._select_best_device()
        
        self.device = device
        self.confidence_threshold = confidence_threshold
        
        # 加载模型到指定设备
        self.model = YOLO(model_path)
        
        # 设置模型设备
        if device == 'cuda':
            self.model.to('cuda')
        elif device == 'mps':
            self.model.to('mps')
        
        print(f"Loaded YOLOv8 model on {device.upper()} | Confidence: {confidence_threshold}")
        
        # 显示设备信息
        self._show_device_info()
        
        # 计算最佳批量大小
        self.batch_size = self._calculate_optimal_batch_size()
        print(f"Optimal batch size: {self.batch_size}")
    
    def _select_best_device(self) -> str:
        """
        自动选择最佳可用设备
        优先级: CUDA > MPS > CPU
        """
        if torch.cuda.is_available():
            # 检查CUDA设备
            cuda_device_count = torch.cuda.device_count()
            if cuda_device_count > 0:
                # 选择显存最大的GPU
                best_gpu = 0
                max_memory = 0
                for i in range(cuda_device_count):
                    memory = torch.cuda.get_device_properties(i).total_memory
                    if memory > max_memory:
                        max_memory = memory
                        best_gpu = i
                
                # 设置当前设备
                torch.cuda.set_device(best_gpu)
                return 'cuda'
        
        # 检查MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return 'mps'
        
        # 默认使用CPU
        return 'cpu'
    
    def _calculate_optimal_batch_size(self) -> int:
        """
        根据设备内存/显存计算最佳批量大小
        """
        if self.device == 'cuda':
            # 获取GPU显存信息
            total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
            print(f"GPU total memory: {total_memory:.2f}GB")
            
            # 根据显存大小计算批量大小
            # 假设每个1280x1280x3的切片需要约50MB显存（包括模型和中间结果）
            estimated_memory_per_tile = 50 / 1024  # GB
            
            # 保留30%显存给模型和其他开销
            available_memory = total_memory * 0.7

            # 计算批量大小
            batch_size = max(1, int(available_memory / estimated_memory_per_tile))
            
            # 限制最大批量大小
            batch_size = min(batch_size, 16)  # 最大16个切片
            
            return batch_size
            
        elif self.device == 'mps':
            # MPS设备，使用较小的批量大小
            return 4
            
        else:
            # CPU设备，根据系统内存计算批量大小
            try:
                import psutil
                # 获取系统内存信息
                memory_info = psutil.virtual_memory()
                total_ram = memory_info.total / (1024**3)  # GB
                available_ram = memory_info.available / (1024**3)  # GB
                
                print(f"System RAM: {total_ram:.2f}GB (Available: {available_ram:.2f}GB)")
                
                # 假设每个1280x1280x3的切片需要约100MB内存（CPU处理需要更多内存）
                estimated_memory_per_tile = 100 / 1024  # GB
                
                # 保留50%内存给系统和其他进程
                safe_available_memory = available_ram * 0.5
                
                # 计算批量大小
                batch_size = max(1, int(safe_available_memory / estimated_memory_per_tile))
                
                # 限制最大批量大小（CPU处理较慢，不宜过大）
                batch_size = min(batch_size, 8)  # 最大8个切片
                
                # 如果可用内存很少，使用最小批量大小
                if available_ram < 2.0:  # 小于2GB
                    batch_size = 2
                elif available_ram < 4.0:  # 小于4GB
                    batch_size = 4
                
                batch_size = 2
                return batch_size
                
            except ImportError:
                # 如果没有psutil，使用保守的默认值
                print("psutil未安装，使用默认CPU批量大小")
                return 2
            except Exception as e:
                # 如果获取内存信息失败，使用保守的默认值
                print(f"获取系统内存信息失败: {e}，使用默认CPU批量大小")
                return 2
    
    def _show_device_info(self):
        """
        显示设备信息
        """
        if self.device == 'cuda':
            device_name = torch.cuda.get_device_name()
            memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            memory_reserved = torch.cuda.memory_reserved(0) / (1024**3)
            
            print(f"GPU: {device_name}")
            print(f"GPU Memory: {memory_allocated:.2f}GB / {memory_total:.2f}GB (Reserved: {memory_reserved:.2f}GB)")
            
        elif self.device == 'mps':
            print("Using Apple Silicon MPS (Metal Performance Shaders)")
        else:
            print("Using CPU")

    def predict_batch(self, images: List[np.ndarray], imgsz: int = 1280) -> List[List[ObjectPrediction]]:
        """
        批量预测多个图像
        
        Args:
            images: 图像列表
            imgsz: 输入图像大小，默认1280
            
        Returns:
            预测结果列表，每个元素对应一个图像的预测结果
        """
        if not images:
            return []
        
        # 确保所有图像都是RGB格式
        rgb_images = []
        for img in images:
            rgb_img = self._ensure_rgb(img)
            if rgb_img is not None:
                rgb_images.append(rgb_img)
        
        if not rgb_images:
            return []
        
        # 批量推理，classes=[0]，只检测玉米苗。
        results = self.model.predict(source=rgb_images, save=False, save_txt=False, imgsz=imgsz, conf=0.3, device=self.device, nms=True, verbose=False, classes=[_CLASS_LIST["玉米苗"]])
        # print(results)
        
        # 处理结果
        all_predictions = []
        for i, result in enumerate(results):
            predictions = []
            if result.boxes is not None:
                boxes = result.boxes
                names = result.names
                for j in range(len(boxes)):
                    # 获取边界框坐标
                    bbox = boxes.xyxy[j].cpu().numpy()  # [x1, y1, x2, y2]
                    confidence = float(boxes.conf[j].cpu().numpy())
                    class_id = int(boxes.cls[j].cpu().numpy())
                    
                    # 创建SAHI格式的预测对象
                    prediction = ObjectPrediction(
                        bbox=bbox.tolist(),
                        category_id=class_id,
                        category_name=names[class_id] if class_id in names else f"class_{class_id}",
                        score=confidence
                    )
                    predictions.append(prediction)
            
            all_predictions.append(predictions)
        
        return all_predictions

    def predict(self, image: np.ndarray, imgsz: int = 1280) -> List[ObjectPrediction]:
        """
        单图像预测（保持向后兼容）
        
        Args:
            image: 输入图像
            imgsz: 输入图像大小，默认1280
            
        Returns:
            预测结果列表
        """
        results = self.predict_batch([image], imgsz=imgsz)
        return results[0] if results else []
    
    def _ensure_rgb(self, image: np.ndarray) -> np.ndarray:
        """
        确保图像是3通道RGB格式
        """
        if image is None:
            return None
        
        # 检查图像维度
        if len(image.shape) == 2:
            # 灰度图转RGB
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif len(image.shape) == 3:
            if image.shape[2] == 1:
                # 单通道转RGB
                return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 3:
                # 已经是3通道，检查是否是BGR
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            elif image.shape[2] == 4:
                # 4通道RGBA转RGB
                return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            else:
                # 其他通道数，取前3个通道
                return image[:, :, :3]
        else:
            raise ValueError(f"不支持的图像格式: shape={image.shape}")
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        获取当前设备信息
        """
        info = {
            "device": self.device,
            "device_name": "Unknown",
            "batch_size": self.batch_size
        }
        
        if self.device == 'cuda':
            info["device_name"] = torch.cuda.get_device_name()
            info["memory_total"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            info["memory_allocated"] = torch.cuda.memory_allocated(0) / (1024**3)
            info["memory_reserved"] = torch.cuda.memory_reserved(0) / (1024**3)
            info["device_count"] = torch.cuda.device_count()
        elif self.device == 'mps':
            info["device_name"] = "Apple Silicon MPS"
        else:
            info["device_name"] = "CPU"
        
        return info
    
    def clear_gpu_memory(self):
        """
        清理GPU内存
        """
        if self.device == 'cuda':
            torch.cuda.empty_cache()
            gc.collect()
            print("GPU memory cleared")

def is_blank_tile(tile: np.ndarray, threshold: float = 0.95) -> bool:
    """检查是否为空白切片"""
    if tile is None:
        return True
    
    # 转换为灰度图
    if len(tile.shape) == 3:
        if tile.shape[2] == 4:
            gray = cv2.cvtColor(tile, cv2.COLOR_RGBA2GRAY)
        else:
            gray = cv2.cvtColor(tile, cv2.COLOR_RGB2GRAY)
    else:
        gray = tile
    
    # 计算标准差
    std_dev = np.std(gray)
    
    # 如果标准差很小，说明图像变化很小，可能是空白
    return std_dev < 10

def read_tile_with_gdal(image_path: str, x_min: int, y_min: int, x_max: int, y_max: int) -> Optional[np.ndarray]:
    """
    使用GDAL读取TIFF文件的特定区域
    """
    try:
        # 打开数据集
        dataset = gdal.Open(image_path, gdal.GA_ReadOnly)
        if dataset is None:
            print(f"无法打开图像文件: {image_path}")
            return None
        
        # 获取图像信息
        width = dataset.RasterXSize
        height = dataset.RasterYSize
        bands = dataset.RasterCount
        
        # 确保读取区域在图像范围内
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(width, x_max)
        y_max = min(height, y_max)
        
        if x_max <= x_min or y_max <= y_min:
            print(f"无效的读取区域: ({x_min},{y_min})-({x_max},{y_max})")
            return None
        
        # 计算读取窗口
        win_xsize = x_max - x_min
        win_ysize = y_max - y_min
        
        # 读取数据
        if bands == 1:
            # 单波段
            band = dataset.GetRasterBand(1)
            tile = band.ReadAsArray(x_min, y_min, win_xsize, win_ysize)
        else:
            # 多波段
            tile = np.empty((win_ysize, win_xsize, bands), dtype=np.uint8)
            for i in range(bands):
                band = dataset.GetRasterBand(i + 1)
                tile[:, :, i] = band.ReadAsArray(x_min, y_min, win_xsize, win_ysize)
        
        # 关闭数据集
        dataset = None
        
        return tile
        
    except Exception as e:
        print(f"GDAL读取失败: {e}")
        return None

def read_tile_with_rasterio(image_path: str, x_min: int, y_min: int, x_max: int, y_max: int) -> Optional[np.ndarray]:
    """
    使用rasterio读取TIFF文件的特定区域
    """
    try:
        
        with rasterio.open(image_path) as src:
            # 确保读取区域在图像范围内
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(src.width, x_max)
            y_max = min(src.height, y_max)
            
            if x_max <= x_min or y_max <= y_min:
                print(f"无效的读取区域: ({x_min},{y_min})-({x_max},{y_max})")
                return None
            
            # 创建读取窗口
            window = Window(x_min, y_min, x_max - x_min, y_max - y_min)
            
            # 读取数据
            tile = src.read(window=window)
            
            # 调整维度顺序 (bands, height, width) -> (height, width, bands)
            if len(tile.shape) == 3:
                tile = np.transpose(tile, (1, 2, 0))
            
            return tile
            
    except Exception as e:
        print(f"rasterio读取失败: {e}")
        return None

def read_tile_with_tifffile(image_path: str, x_min: int, y_min: int, x_max: int, y_max: int) -> Optional[np.ndarray]:
    """
    使用tifffile读取TIFF文件的特定区域
    """
    try:
        
        # 检查文件大小
        file_size = os.path.getsize(image_path)
        if file_size > 2 * 1024**3:  # 大于2GB
            print(f"文件过大({file_size/1024**3:.1f}GB)，跳过tifffile方法")
            return None
        
        with tifffile.TiffFile(image_path) as tif:
            # 确保读取区域在图像范围内
            image_shape = tif.series[0].shape
            if len(image_shape) == 3:
                height, width, _ = image_shape
            else:
                height, width = image_shape
            
            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(width, x_max)
            y_max = min(height, y_max)
            
            if x_max <= x_min or y_max <= y_min:
                print(f"无效的读取区域: ({x_min},{y_min})-({x_max},{y_max})")
                return None
            
            # 读取指定区域
            tile = tif.series[0].asarray(key=0)[y_min:y_max, x_min:x_max]
            return tile
            
    except Exception as e:
        print(f"tifffile读取失败: {e}")
        return None

def read_tile_safe(image_path: str, x_min: int, y_min: int, x_max: int, y_max: int) -> Optional[np.ndarray]:
    """
    安全地读取图像切片，优先使用GDAL或rasterio
    """
    # 方法1: 使用GDAL（推荐用于超大TIFF）
    tile = read_tile_with_gdal(image_path, x_min, y_min, x_max, y_max)
    if tile is not None:
        return tile
    
    # 方法2: 使用rasterio
    tile = read_tile_with_rasterio(image_path, x_min, y_min, x_max, y_max)
    if tile is not None:
        return tile
    
    # 方法3: 使用tifffile（仅适用于较小的区域）
    tile = read_tile_with_tifffile(image_path, x_min, y_min, x_max, y_max)
    if tile is not None:
        return tile
    
    print(f"所有读取方法都失败，无法读取区域 ({x_min},{y_min})-({x_max},{y_max})")
    return None

def custom_nms_postprocess(object_predictions: List[ObjectPrediction], iou_threshold: float = 0.5) -> List[ObjectPrediction]:
    """
    智能选择NMS策略的主函数
    
    策略选择：
    - 小数据量 (< 1000): 使用原始OpenCV NMS
    - 中等数据量 (1000-50000): 使用分块NMS，减少内存占用
    - 超大数据量 (> 200000): 优先使用GPU加速
    """
    if not object_predictions:
        return []
    
    data_size = len(object_predictions)
    print(f"NMS处理开始，检测框数量: {data_size}")
    
    # 根据数据量选择最优策略
    if data_size < 1000:
        # 小数据量：使用原始方法
        print("使用原始OpenCV NMS (小数据量)")
        return custom_nms_postprocess_original(object_predictions, iou_threshold)
        
    elif data_size < 100000:
        # 中等数据量：使用分块NMS
        print("使用分块NMS (中等数据量)")
        return custom_nms_chunked(object_predictions, iou_threshold, 10000)
        
    else:
        # 超大数据量：优先使用GPU加速
        print("超大数据量，尝试GPU加速NMS...")
        try:
            result = custom_nms_gpu_optimized(object_predictions, iou_threshold)
            print("GPU加速NMS成功")
            return result
        except Exception as e:
            print(f"GPU加速NMS失败: {e}")
            print("回退到分块NMS")
            return custom_nms_chunked(object_predictions, iou_threshold, 10000)

def custom_nms_postprocess_original(object_predictions: List[ObjectPrediction], 
                                  iou_threshold: float = 0.5) -> List[ObjectPrediction]:
    """
    原始NMS实现（保持向后兼容）
    适用于小数据量 (< 1000)
    """
    if not object_predictions:
        return []
    
    # 转换为numpy数组进行NMS
    boxes = []
    scores = []
    indices = []
    
    for i, pred in enumerate(object_predictions):
        # 获取边界框坐标
        if hasattr(pred.bbox, 'to_xyxy'):
            bbox = pred.bbox.to_xyxy()
        else:
            # 如果bbox已经是列表格式
            bbox = pred.bbox if isinstance(pred.bbox, list) else pred.bbox.tolist()
        
        boxes.append(bbox)
        scores.append(pred.score.value)
        indices.append(i)
    
    boxes = np.array(boxes)
    scores = np.array(scores)
    
    # 使用OpenCV的NMS
    try:
        # 转换为OpenCV格式 [x1, y1, x2, y2] -> [x1, y1, width, height]
        boxes_cv = []
        for box in boxes:
            x1, y1, x2, y2 = box
            boxes_cv.append([x1, y1, x2 - x1, y2 - y1])
        boxes_cv = np.array(boxes_cv, dtype=np.float32)
        
        # 执行NMS
        keep_indices = cv2.dnn.NMSBoxes(
            boxes_cv.tolist(), 
            scores.tolist(), 
            score_threshold=0.0, 
            nms_threshold=iou_threshold
        )
        
        if len(keep_indices) > 0:
            keep_indices = keep_indices.flatten()
            return [object_predictions[i] for i in keep_indices]
        else:
            return []
            
    except Exception as e:
        print(f"NMS处理失败: {e}")
        # 如果NMS失败，返回所有预测结果
        return object_predictions

def custom_nms_chunked(object_predictions: List[ObjectPrediction], 
                      iou_threshold: float = 0.5,
                      chunk_size: int = 10000) -> List[ObjectPrediction]:
    """
    分块NMS处理，减少内存占用
    适用于中等数据量 (1000-50000)
    """
    print(f"使用分块NMS，块大小: {chunk_size}")
    
    if len(object_predictions) <= chunk_size:
        return custom_nms_postprocess_original(object_predictions, iou_threshold)
    
    # 按置信度排序
    sorted_predictions = sorted(object_predictions, key=lambda x: x.score.value, reverse=True)
    
    # 分块处理
    all_kept_predictions = []
    total_chunks = (len(sorted_predictions) + chunk_size - 1) // chunk_size
    
    for i in range(total_chunks):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, len(sorted_predictions))
        chunk_predictions = sorted_predictions[start_idx:end_idx]
        
        print(f"处理分块 {i+1}/{total_chunks}: {len(chunk_predictions)} 个检测框")
        
        # 对当前分块执行NMS
        chunk_kept = custom_nms_postprocess_original(chunk_predictions, iou_threshold)
        all_kept_predictions.extend(chunk_kept)
        
        # 清理内存
        del chunk_predictions
        gc.collect()
    
    # 对最终结果再次执行NMS
    print(f"最终合并，总保留检测框: {len(all_kept_predictions)}")
    final_result = custom_nms_postprocess_original(all_kept_predictions, iou_threshold)
    
    return final_result

def custom_nms_gpu_optimized(object_predictions: List[ObjectPrediction], 
                           iou_threshold: float = 0.5) -> List[ObjectPrediction]:
    """
    GPU加速的NMS实现（需要torch）
    """
    try:
        import torch
        from torchvision.ops import nms
        
        if not torch.cuda.is_available():
            raise RuntimeError("GPU不可用")
        
        print("使用GPU加速NMS")
        
        # 转换为torch张量
        boxes = []
        scores = []
        
        for pred in object_predictions:
            if hasattr(pred.bbox, 'to_xyxy'):
                bbox = pred.bbox.to_xyxy()
            else:
                bbox = pred.bbox if isinstance(pred.bbox, list) else pred.bbox.tolist()
            
            boxes.append(bbox)
            scores.append(pred.score.value)
        
        boxes_tensor = torch.tensor(boxes, dtype=torch.float32, device='cuda')
        scores_tensor = torch.tensor(scores, dtype=torch.float32, device='cuda')
        
        # 执行GPU NMS
        keep_indices = nms(boxes_tensor, scores_tensor, iou_threshold)
        
        # 转换回CPU
        keep_indices = keep_indices.cpu().numpy()
        
        # 返回保留的预测结果
        return [object_predictions[i] for i in keep_indices]
        
    except ImportError:
        raise RuntimeError("torchvision未安装")
    except Exception as e:
        raise RuntimeError(f"GPU NMS失败: {e}")

def benchmark_advance_nms(
    object_predictions: List[ObjectPrediction],
    slice_bboxes: List[Tuple[int, int, int, int]],
    tile_size: int,
    overlap_ratio: float,
    iou_threshold: float = 0.5,
    blank_slice_indices: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    基准测试高级NMS方法的性能
    
    Args:
        object_predictions: 检测结果列表
        slice_bboxes: 切片边界框列表
        tile_size: 切片大小
        overlap_ratio: 重叠比例
        iou_threshold: IoU阈值
        blank_slice_indices: 空白切片的索引列表，如果为None则不跳过任何切片
        
    Returns:
        性能测试结果字典
    """
    results = {}
    data_size = len(object_predictions)
    
    print(f"开始高级NMS性能基准测试，数据量: {data_size}")
    if blank_slice_indices:
        print(f"空白切片数量: {len(blank_slice_indices)}")
    
    # 测试1: 原始NMS
    gc.collect()
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024**2  # MB
    
    result_original = custom_nms_postprocess_original(object_predictions, iou_threshold)
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss / 1024**2  # MB
    
    results["原始NMS"] = {
        "时间": end_time - start_time,
        "内存峰值": end_memory - start_memory,
        "结果数量": len(result_original)
    }
    
    # 测试4: 高级NMS V3（正确的重叠区域定义）
    gc.collect()
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024**2  # MB
    
    result_advance = advance_nms_postprocess(object_predictions, slice_bboxes, tile_size, overlap_ratio, iou_threshold, blank_slice_indices, overlap_expansion_ratio=1.6)
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss / 1024**2  # MB
    
    results["高级NMS V3"] = {
        "时间": end_time - start_time,
        "内存峰值": end_memory - start_memory,
        "结果数量": len(result_advance)
    }
    
    # 打印结果
    print("\n" + "="*60)
    print("高级NMS性能基准测试结果")
    print("="*60)
    
    for method, metrics in results.items():
        print(f"\n{method}:")
        print(f"  处理时间: {metrics['时间']:.3f}秒")
        print(f"  内存峰值: {metrics['内存峰值']:.1f}MB")
        print(f"  结果数量: {metrics['结果数量']}")
        if method != "原始NMS":
            speedup = results["原始NMS"]["时间"] / metrics["时间"]
            print(f"  速度提升: {speedup:.2f}x")
    
    return results

def get_image_info_safe(image_path: str) -> Optional[Tuple[int, int, int, float]]:
    """
    安全地获取图像信息
    """
    # 方法1: 使用GDAL
    try:
        dataset = gdal.Open(image_path, gdal.GA_ReadOnly)
        if dataset is not None:
            width = dataset.RasterXSize
            height = dataset.RasterYSize
            bands = dataset.RasterCount
            image_size_gb = (width * height * bands) / (1024**3)
            dataset = None
            return height, width, bands, image_size_gb
    except:
        pass
    
    # 方法2: 使用rasterio
    try:
        with rasterio.open(image_path) as src:
            height = src.height
            width = src.width
            bands = src.count
            image_size_gb = (width * height * bands) / (1024**3)
            return height, width, bands, image_size_gb
    except:
        pass
    
    # 方法3: 使用tifffile（仅适用于较小的文件）
    try:
        with tifffile.TiffFile(image_path) as tif:
            shape = tif.series[0].shape
            if len(shape) == 3:
                height, width, bands = shape
            else:
                height, width = shape
                bands = 1
            image_size_gb = (width * height * bands) / (1024**3)
            return height, width, bands, image_size_gb
    except:
        pass
    
    return None

def export_results_to_coco_json(predictions: List[ObjectPrediction], 
                               image_path: str, 
                               output_path: str,
                               image_id: int = 1) -> None:
    """
    将检测结果导出为COCO格式的JSON文件
    """
    print(f"导出COCO格式检测结果到: {output_path}")
    
    # 准备COCO格式数据
    coco_data = {
        "info": {
            "description": "Object detection results",
            "url": "",
            "version": "1.0",
            "year": datetime.now().year,
            "contributor": "CropMirror",
            "date_created": datetime.now().isoformat()
        },
        "licenses": [],
        "images": [
            {
                "id": image_id,
                "file_name": os.path.basename(image_path),
                "path": image_path,
                "width": 0,  # 需要从图像信息获取
                "height": 0   # 需要从图像信息获取
            }
        ],
        "detections": [],
        "categories": []
    }
    
    # 获取图像信息
    image_info = get_image_info_safe(image_path)
    if image_info:
        height, width, _, _ = image_info
        coco_data["images"][0]["width"] = width
        coco_data["images"][0]["height"] = height
    
    # 收集所有类别
    categories = {}
    for pred in predictions:
        category_id = pred.category.id
        category_name = pred.category.name
        if category_id not in categories:
            categories[category_id] = {
                "id": category_id,
                "name": category_name,
                "supercategory": "object"
            }
    
    coco_data["categories"] = list(categories.values())
    
    # 准备标注数据
    for i, pred in enumerate(predictions):
        if hasattr(pred.bbox, 'to_xyxy'):
            bbox = pred.bbox.to_xyxy()
        else:
            bbox = pred.bbox if isinstance(pred.bbox, list) else pred.bbox.tolist()
        
        # COCO格式的bbox: [x, y, width, height]
        coco_bbox = [
            float(bbox[0]),  # x
            float(bbox[1]),  # y
            float(bbox[2] - bbox[0]),  # width
            float(bbox[3] - bbox[1])   # height
        ]
        
        annotation = {
            "id": i + 1,
            "image_id": image_id,
            "category_id": pred.category.id,
            "category_name": pred.category.name,
            "bbox": coco_bbox,
            "area": float(coco_bbox[2] * coco_bbox[3]),
            "iscrowd": 0,
            "score": pred.score.value
        }
        coco_data["detections"].append(annotation)
    
    # 保存COCO格式JSON文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(coco_data, f, indent=2, ensure_ascii=False)
        print(f"COCO格式检测结果已成功导出到: {output_path}")
        print(f"共导出 {len(coco_data['detections'])} 个检测结果")
    except Exception as e:
        print(f"导出COCO JSON文件失败: {e}")

# 批量处理大图像
def process_large_image_batch(
    image_path: str,
    model: YOLOv8Model,
    output_dir: str,
    tile_size: int = 1280,
    overlap_ratio: float = 0.02,
    memory_limit: int = 6 * 1024**3,
    skip_blank_tiles: bool = True,
    coco_json_output_path: Optional[str] = None,
    save_tiles: bool = False,
    tiles_output_dir: Optional[str] = None,
    generate_pts: bool = True
) -> List[ObjectPrediction]:
    """
    使用批量处理方式处理大图像
    
    Args:
        image_path: 输入图像路径
        model: YOLOv8模型
        output_dir: 输出目录
        tile_size: 切片大小
        overlap_ratio: 重叠比例
        memory_limit: 内存限制
        skip_blank_tiles: 是否跳过空白切片
        coco_json_output_path: COCO格式JSON输出路径
        save_tiles: 是否保存切片到文件夹
        tiles_output_dir: 切片保存目录，如果为None则使用默认目录
        generate_pts: 是否生成检测点GPS坐标文件
    """
    print(f"开始批量处理图像: {image_path}")
    
    # 创建切片保存目录
    if save_tiles:
        if tiles_output_dir is None:
            # 使用默认目录：基于输入图像名称
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            tiles_output_dir = os.path.join(output_dir, f"tiles_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        blank_tiles_dir = os.path.join(tiles_output_dir, "blank_tiles")
        efficient_tiles_dir = os.path.join(tiles_output_dir, "efficient_tiles")
        
        # 创建目录
        os.makedirs(blank_tiles_dir, exist_ok=True)
        os.makedirs(efficient_tiles_dir, exist_ok=True)
        
        print(f"切片将保存到: {tiles_output_dir}")
        print(f"空白切片目录: {blank_tiles_dir}")
        print(f"有效切片目录: {efficient_tiles_dir}")
    
    # 显示设备信息
    device_info = model.get_device_info()
    print(f"使用设备: {device_info['device_name']}")
    print(f"批量大小: {device_info['batch_size']}")
    if device_info['device'] == 'cuda':
        print(f"GPU内存: {device_info['memory_allocated']:.2f}GB / {device_info['memory_total']:.2f}GB")
    
    # 阶段1: 获取图像信息
    stage1_start = time.time()
    image_info = get_image_info_safe(image_path)
    if image_info is None:
        print("无法获取图像信息，请检查文件是否存在且格式正确")
        return []
    
    height, width, bands, image_size_gb = image_info
    print(f"Image dimensions: {width}x{height} | Channels: {bands}")
    print(f"Image size: {image_size_gb:.2f}GB")
    
    stage1_time = time.time() - stage1_start
    print(f"阶段1 - 获取图像信息: {stage1_time:.3f}s")
    
    # 阶段2: 生成切片边界框
    stage2_start = time.time()
    slice_bboxes = get_slice_bboxes(
        image_height=height,
        image_width=width,
        slice_height=tile_size,
        slice_width=tile_size,
        overlap_height_ratio=overlap_ratio,
        overlap_width_ratio=overlap_ratio
    )
    
    print(f"Generated {len(slice_bboxes)} slice bboxes")
    stage2_time = time.time() - stage2_start
    print(f"阶段2 - 生成切片边界框: {stage2_time:.3f}s")
    
    # 阶段3: 批量处理切片
    stage3_start = time.time()
    all_object_predictions = []
    
    # 统计变量 - 严格区分读取失败和空白切片
    processed_tiles = 0          # 成功处理的有效切片数量
    read_failed_tiles = 0        # 读取失败的切片数量
    blank_tiles = 0              # 空白切片数量（成功读取但内容为空白）
    white_tiles = 0              # 全白切片数量
    black_tiles = 0              # 全黑切片数量
    saved_blank_tiles = 0        # 保存的空白切片数量
    saved_efficient_tiles = 0    # 保存的有效切片数量
    
    # 新增：收集空白切片索引
    blank_slice_indices = []     # 空白切片的索引列表
    
    batch_size = model.batch_size
    total_batches = (len(slice_bboxes) + batch_size - 1) // batch_size
    
    print(f"Processing {len(slice_bboxes)} tiles in {total_batches} batches (batch_size={batch_size})...")
    
    for batch_idx in range(total_batches):
        batch_start = time.time()
        
        # 准备当前批次的切片
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(slice_bboxes))
        current_batch_bboxes = slice_bboxes[start_idx:end_idx]
        
        # 读取当前批次的所有切片
        read_start = time.time()
        batch_tiles = []
        batch_bboxes = []
        batch_indices = []
        
        # 批次内统计
        batch_read_failed = 0
        batch_blank_tiles = 0
        batch_white_tiles = 0
        batch_black_tiles = 0
        
        for i, slice_bbox in enumerate(current_batch_bboxes):
            tile = read_tile_safe(
                image_path, 
                slice_bbox[0], slice_bbox[1], 
                slice_bbox[2], slice_bbox[3]
            )
            
            if tile is None:
                # 读取失败
                batch_read_failed += 1
                read_failed_tiles += 1
                print(f"读取切片 {start_idx + i + 1} 失败 (坐标: {slice_bbox})")
                continue
            
            # 成功读取，检查是否为空白切片
            is_blank = is_blank_tile(tile, threshold=0.95)
            
            # 保存切片到相应文件夹
            if save_tiles:
                tile_filename = f"tile_{start_idx + i + 1:06d}_x{slice_bbox[0]}_y{slice_bbox[1]}.jpg"
                
                if is_blank:
                    # 保存空白切片
                    blank_tile_path = os.path.join(blank_tiles_dir, tile_filename)
                    try:
                        # 确保图像是3通道RGB格式
                        if len(tile.shape) == 3:
                            if tile.shape[2] == 4:
                                tile_rgb = cv2.cvtColor(tile, cv2.COLOR_RGBA2RGB)
                            else:
                                tile_rgb = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
                        else:
                            tile_rgb = cv2.cvtColor(tile, cv2.COLOR_GRAY2RGB)
                        
                        cv2.imwrite(blank_tile_path, tile_rgb)
                        saved_blank_tiles += 1
                    except Exception as e:
                        print(f"保存空白切片失败: {e}")
                else:
                    # 保存有效切片
                    efficient_tile_path = os.path.join(efficient_tiles_dir, tile_filename)
                    try:
                        # 确保图像是3通道RGB格式
                        if len(tile.shape) == 3:
                            if tile.shape[2] == 4:
                                tile_rgb = cv2.cvtColor(tile, cv2.COLOR_RGBA2RGB)
                            else:
                                tile_rgb = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
                        else:
                            tile_rgb = cv2.cvtColor(tile, cv2.COLOR_GRAY2RGB)
                        
                        cv2.imwrite(efficient_tile_path, tile_rgb)
                        saved_efficient_tiles += 1
                    except Exception as e:
                        print(f"保存有效切片失败: {e}")
            
            if is_blank:
                # 统计空白切片类型
                batch_blank_tiles += 1
                blank_tiles += 1
                
                # 记录空白切片索引
                blank_slice_indices.append(start_idx + i)
                
                if len(tile.shape) == 3:
                    if tile.shape[2] == 4:
                        gray = cv2.cvtColor(tile, cv2.COLOR_RGBA2GRAY)
                    else:
                        gray = cv2.cvtColor(tile, cv2.COLOR_RGB2GRAY)
                else:
                    gray = tile
                mean_val = np.mean(gray)
                if mean_val > 200:
                    batch_white_tiles += 1
                    white_tiles += 1
                else:
                    batch_black_tiles += 1
                    black_tiles += 1
                
                # 如果跳过空白切片，不添加到批次中
                if skip_blank_tiles:
                    continue
            
            # 添加到批次中（非空白切片或未跳过空白切片）
            batch_tiles.append(tile)
            batch_bboxes.append(slice_bbox)
            batch_indices.append(start_idx + i)
        
        read_time = time.time() - read_start
        
        # 批量推理
        inference_start = time.time()
        batch_predictions = model.predict_batch(batch_tiles, imgsz=tile_size)
        inference_time = time.time() - inference_start
        
        # 处理批量预测结果
        for i, (predictions, slice_bbox, tile_idx) in enumerate(zip(batch_predictions, batch_bboxes, batch_indices)):
            # 调整预测坐标到原图坐标系
            for pred in predictions:
                if hasattr(pred.bbox, 'to_xyxy'):
                    bbox = pred.bbox.to_xyxy()
                else:
                    bbox = pred.bbox if isinstance(pred.bbox, list) else pred.bbox.tolist()
                
                # 调整坐标
                adjusted_bbox = [
                    bbox[0] + slice_bbox[0],  # x1
                    bbox[1] + slice_bbox[1],  # y1
                    bbox[2] + slice_bbox[0],  # x2
                    bbox[3] + slice_bbox[1]   # y2
                ]
                
                # 创建新的预测对象
                adjusted_pred = ObjectPrediction(
                    bbox=adjusted_bbox,
                    category_id=pred.category.id,
                    category_name=pred.category.name,
                    score=pred.score.value
                )
                all_object_predictions.append(adjusted_pred)
            
            processed_tiles += 1
        
        batch_time = time.time() - batch_start
        batch_detections = sum(len(preds) for preds in batch_predictions)
        
        print(f"批次 {batch_idx + 1}/{total_batches} | 切片 {start_idx + 1}-{end_idx} | 读取: {read_time:.3f}s | 批量推理: {inference_time:.3f}s | 检测: {batch_detections}个 | 总时间: {batch_time:.3f}s")
        
        # 定期清理内存
        if batch_idx % 10 == 0:
            gc.collect()
            if model.device == 'cuda':
                model.clear_gpu_memory()
    
    stage3_time = time.time() - stage3_start
    print(f"阶段3 - 批量处理切片: {stage3_time:.3f}s")
    
    # 详细的统计报告
    print(f"\n=== 切片处理统计报告 ===")
    print(f"总切片数量: {len(slice_bboxes)}")
    print(f"成功读取切片: {len(slice_bboxes) - read_failed_tiles}")
    print(f"读取失败切片: {read_failed_tiles} ({read_failed_tiles/len(slice_bboxes)*100:.1f}%)")
    print(f"空白切片: {blank_tiles} ({blank_tiles/len(slice_bboxes)*100:.1f}%)")
    print(f"  - 全白切片: {white_tiles}")
    print(f"  - 全黑切片: {black_tiles}")
    print(f"有效处理切片: {processed_tiles} ({processed_tiles/len(slice_bboxes)*100:.1f}%)")
    print(f"空白切片索引: {len(blank_slice_indices)} 个")
    
    if save_tiles:
        print(f"切片保存统计: 空白切片 {saved_blank_tiles}, 有效切片 {saved_efficient_tiles}")
    
    # 阶段4: 后处理合并
    stage4_start = time.time()
    print("开始合并结果...")
    print(f"合并前检测数量: {len(all_object_predictions)}")
    
    # 根据检测数量选择NMS策略
    detection_count = len(all_object_predictions)
    
    # 优先使用高级NMS（基于切片重叠信息）
    print("优先使用高级NMS（基于切片重叠信息）...")
    try:
        combined_predictions, overlap_predictions = advance_nms_postprocess(
            all_object_predictions, 
            slice_bboxes, 
            tile_size, 
            overlap_ratio, 
            iou_threshold=0.5,
            blank_slice_indices=blank_slice_indices,
            overlap_expansion_ratio=1.6
        )
        print("高级NMS处理成功")
    except Exception as e:
        print(f"高级NMS处理失败: {e}")
        print("回退到传统NMS策略")
        
        # 检查GPU是否可用
        gpu_available = torch.cuda.is_available() if hasattr(torch, 'cuda') else False
        
        if gpu_available:
            # GPU可用，优先使用GPU NMS
            print(f"GPU可用，优先使用GPU NMS")
            try:
                combined_predictions = custom_nms_gpu_optimized(all_object_predictions, iou_threshold=0.5)
                print("GPU NMS处理成功")
            except Exception as e:
                print(f"GPU NMS处理失败: {e}")
                print("回退到CPU NMS策略")
                # GPU NMS失败，回退到CPU策略
                if detection_count <= 50000:
                    print(f"检测数量 {detection_count} <= 50000，使用OpenCV NMS")
                    combined_predictions = custom_nms_postprocess_original(all_object_predictions, iou_threshold=0.5)
                else:
                    print(f"检测数量 {detection_count} > 50000，使用分块NMS")
                    combined_predictions = custom_nms_chunked(all_object_predictions, iou_threshold=0.5, chunk_size=10000)
        else:
            # GPU不可用，根据检测数量选择CPU NMS策略
            if detection_count <= 50000:
                print(f"GPU不可用，检测数量 {detection_count} <= 50000，使用OpenCV NMS")
                combined_predictions = custom_nms_postprocess_original(all_object_predictions, iou_threshold=0.5)
            else:
                print(f"GPU不可用，检测数量 {detection_count} > 50000，使用分块NMS")
                combined_predictions = custom_nms_chunked(all_object_predictions, iou_threshold=0.5, chunk_size=10000)
    
    stage4_time = time.time() - stage4_start
    print(f"阶段4 - 后处理合并: {stage4_time:.3f}s")
    print(f"合并后检测结果: {len(combined_predictions)}个")
    print(f"NMS压缩比: {detection_count}/{len(combined_predictions)} = {detection_count/len(combined_predictions):.2f}:1")
    
    # 阶段5: 导出COCO JSON结果（可选）
    if coco_json_output_path:
        stage5_start = time.time()
        export_results_to_coco_json(combined_predictions, image_path, coco_json_output_path)
        stage5_time = time.time() - stage5_start
        print(f"阶段5 - 导出COCO JSON结果: {stage5_time:.3f}s")

    # 阶段6: 生成检测点GPS坐标文件
    stage6_start = time.time()
    if generate_pts:
        try:
            print("\n=== 生成检测点GPS坐标文件 ===")
            pts_start = time.time()
            pts_json_path = gen_detection_pts(image_path, combined_predictions, output_dir=output_dir)
            pts_time = time.time() - pts_start
            print(f"检测点GPS坐标文件生成完成: {pts_time:.3f}s")
            print(f"文件路径: {pts_json_path}")
        except Exception as e:
            print(f"生成检测点GPS坐标文件失败: {e}")
            print("继续执行，不影响主要功能")
    else:
        print("\n跳过生成检测点GPS坐标文件")
    stage6_time = time.time() - stage6_start
    print(f"阶段6 - 生成检测点GPS坐标文件: {stage6_time:.3f}s")
    
    # 阶段7: 生成切片边框GeoJSON文件
    stage7_start = time.time()
    try:
        print("\n=== 生成切片边框GeoJSON文件 ===")
        slices_geojson_start = time.time()
        slices_geojson_path = gen_slices_geojson(
            image_path=image_path,
            slice_bboxes=slice_bboxes,
            blank_slice_indices=blank_slice_indices,
            output_dir=output_dir,
            tile_size=tile_size,
            overlap_ratio=overlap_ratio
        )
        slices_geojson_time = time.time() - slices_geojson_start
        if slices_geojson_path:
            print(f"切片边框GeoJSON文件生成完成: {slices_geojson_time:.3f}s")
            print(f"文件路径: {slices_geojson_path}")
        else:
            print("切片边框GeoJSON文件生成失败")
    except Exception as e:
        print(f"生成切片边框GeoJSON文件失败: {e}")
        print("继续执行，不影响主要功能")
    stage7_time = time.time() - stage7_start
    print(f"阶段7 - 生成切片边框GeoJSON文件: {stage7_time:.3f}s")
    
    # 总时间统计
    total_time = time.time() - stage1_start
    print(f"\n=== 总处理时间统计 ===")
    print(f"阶段1 - 获取图像信息: {stage1_time:.3f}s")
    print(f"阶段2 - 生成切片边界框: {stage2_time:.3f}s")
    print(f"阶段3 - 批量处理切片: {stage3_time:.3f}s")
    print(f"阶段4 - 后处理合并: {stage4_time:.3f}s")
    if coco_json_output_path:
        print(f"阶段5 - 导出COCO JSON结果: {stage5_time:.3f}s")
    if generate_pts:
        print(f"阶段6 - 生成检测点GPS坐标文件: {stage6_time:.3f}s")
    print(f"阶段7 - 生成切片边框GeoJSON文件: {stage7_time:.3f}s")
    print(f"总处理时间: {total_time:.3f}s")
    print(f"平均每切片时间: {total_time/len(slice_bboxes):.3f}s")
    print(f"平均每批次时间: {total_time/total_batches:.3f}s")
    
    return combined_predictions

# 保持向后兼容的函数
def process_large_image(
    image_path: str,
    model: YOLOv8Model,
    output_dir: str,
    tile_size: int = TILE_SIZE,
    overlap_ratio: float = OVERLAP_RATIO,
    memory_limit: int = MEMORY_LIMIT,
    skip_blank_tiles: bool = True,
    output_path: Optional[str] = None,
    coco_json_output_path: Optional[str] = None,
    save_tiles: bool = False,
    tiles_output_dir: Optional[str] = None
) -> List[ObjectPrediction]:
    """
    处理大图像（单切片模式，保持向后兼容）
    """
    return process_large_image_batch(
        image_path, model, output_dir, tile_size, overlap_ratio, memory_limit,
        skip_blank_tiles, coco_json_output_path, save_tiles, tiles_output_dir
    )

def gen_detection_pts(image_path: str, predictions: List[ObjectPrediction], output_dir: Optional[str] = None) -> str:
    """生成检测点的GPS坐标JSON文件和GeoJSON文件"""
    
    print(f"开始生成检测点GPS坐标文件...")
    print(f"检测点数量: {len(predictions)}")
    
    if output_dir is None:
        output_dir = os.path.dirname(image_path)
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    json_filename = f"{base_name}_pts.json"
    json_path = os.path.join(output_dir, json_filename)
    geojson_filename = f"{base_name}_pts.geojson"
    geojson_path = os.path.join(output_dir, geojson_filename)
    
    try:
        with rasterio.open(image_path) as src:
            bounds = src.bounds
            crs = src.crs
            height, width = src.height, src.width
            transform = src.transform
            
            print(f"图像尺寸: {width} x {height}")
            print(f"图像边界: {bounds}")
            print(f"坐标系统: {crs}")
            
            center_x = (bounds.left + bounds.right) / 2
            center_y = (bounds.bottom + bounds.top) / 2
            
            # 如果坐标系统不是EPSG:4326，需要转换
            if crs != CRS.from_epsg(4326):
                print(f"转换坐标系统从 {crs} 到 EPSG:4326 (WGS84)...")
                wgs84_bounds = transform_bounds(crs, CRS.from_epsg(4326), 
                                              bounds.left, bounds.bottom, 
                                              bounds.right, bounds.top)
                center_x, center_y = transform_bounds(crs, CRS.from_epsg(4326), 
                                                    center_x, center_y, 
                                                    center_x, center_y)[:2]
            else:
                wgs84_bounds = bounds
            
            latlng = {"lat": wgs84_bounds.top, "lng": wgs84_bounds.left}
            latlng_center = {"lat": center_y, "lng": center_x}
            
            print(f"图像定位坐标 (EPSG:4326): {latlng}")
            print(f"图像中心坐标 (EPSG:4326): {latlng_center}")
            
            coordinates = []
            for pred in predictions:
                if hasattr(pred.bbox, 'to_xyxy'):
                    bbox = pred.bbox.to_xyxy()
                else:
                    bbox = pred.bbox if isinstance(pred.bbox, list) else pred.bbox.tolist()
                
                center_pixel_x = (bbox[0] + bbox[2]) / 2
                center_pixel_y = (bbox[1] + bbox[3]) / 2
                
                geo_x, geo_y = transform * (center_pixel_x, center_pixel_y)
                
                # 如果坐标系统不是EPSG:4326，需要转换
                if crs != CRS.from_epsg(4326):
                    geo_x, geo_y = transform_bounds(crs, CRS.from_epsg(4326), 
                                                  geo_x, geo_y, geo_x, geo_y)[:2]
                
                coordinates.append({"lat": geo_y, "lng": geo_x})
            
            print(f"成功计算 {len(coordinates)} 个检测点的GPS坐标 (EPSG:4326)")
            
            json_data = {
                "count": len(coordinates),
                "coordinates": coordinates,
                "latlng": latlng,
                "latlng_center": latlng_center,
                "coordinate_system": "EPSG:4326 (WGS84)"
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"检测点GPS坐标文件已保存: {json_path}")
            print(f"文件大小: {os.path.getsize(json_path) / 1024:.2f} KB")
            print(f"坐标系统: EPSG:4326 (WGS84)")
            
            # 生成GeoJSON文件
            try:
                from shapely.geometry import Point
                
                print(f"开始生成GeoJSON文件...")
                
                # 准备GeoJSON数据结构
                geojson_data = {
                    "type": "FeatureCollection",
                    "crs": {
                        "type": "name",
                        "properties": {
                            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                        }
                    },
                    "features": []
                }
                
                for i, coord in enumerate(coordinates):
                    # 创建Point几何对象 (经度, 纬度)
                    point = Point(coord['lng'], coord['lat'])
                    
                    # 创建Feature对象
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [coord['lng'], coord['lat']]
                        },
                        "properties": {
                            'id': i + 1,
                            'longitude': coord['lng'],
                            'latitude': coord['lat'],
                            'category_id': predictions[i].category.id if i < len(predictions) else 0,
                            'category_name': predictions[i].category.name if i < len(predictions) else 'unknown',
                            'confidence': predictions[i].score.value if i < len(predictions) else 0.0
                        }
                    }
                    geojson_data["features"].append(feature)
                
                # 保存为GeoJSON文件
                with open(geojson_path, 'w', encoding='utf-8') as f:
                    json.dump(geojson_data, f, indent=2, ensure_ascii=False)
                
                print(f"GeoJSON文件已保存: {geojson_path}")
                print(f"GeoJSON文件大小: {os.path.getsize(geojson_path) / 1024:.2f} KB")
                print(f"包含 {len(geojson_data['features'])} 个检测点")
                
            except ImportError:
                print("警告: shapely未安装，跳过GeoJSON生成")
                print("安装命令: pip install shapely")
            except Exception as e:
                print(f"生成GeoJSON文件失败: {e}")
                print("继续执行，不影响JSON文件生成")
            
            return json_path
            
    except Exception as e:
        print(f"生成检测点GPS坐标文件失败: {e}")
        raise
    
    finally:
        gc.collect()

def gen_detection_pts_simple(
    image_path: str,
    predictions: List[ObjectPrediction],
    output_dir: Optional[str] = None,
    gps_bounds: Optional[Tuple[float, float, float, float]] = None
) -> str:
    """
    简化版检测点GPS坐标生成函数（适用于已知GPS边界的情况）
    
    Args:
        image_path: 输入图像路径
        predictions: 检测结果列表
        output_dir: 输出目录
        gps_bounds: GPS边界 (min_lat, min_lng, max_lat, max_lng)，如果为None则尝试从图像获取
        
    Returns:
        str: 生成的JSON文件路径
    """
    print(f"开始生成检测点GPS坐标文件（简化版）...")
    print(f"检测点数量: {len(predictions)}")
    
    # 获取输出目录
    if output_dir is None:
        output_dir = os.path.dirname(image_path)
    
    # 获取文件名（不含扩展名）
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    json_filename = f"{base_name}_pts.json"
    json_path = os.path.join(output_dir, json_filename)
    geojson_filename = f"{base_name}_pts.geojson"
    geojson_path = os.path.join(output_dir, geojson_filename)
    
    try:
        # 获取图像信息
        image_info = get_image_info_safe(image_path)
        if image_info is None:
            raise ValueError(f"无法获取图像信息: {image_path}")
        
        width, height, channels, file_size = image_info
        
        # 如果没有提供GPS边界，尝试从文件名或其他方式获取
        if gps_bounds is None:
            # 这里可以添加从文件名解析GPS信息的逻辑
            # 例如：filename_lat1_lng1_lat2_lng2.tif
            print("警告: 未提供GPS边界信息，使用默认坐标")
            # 使用默认坐标（需要根据实际情况调整）
            gps_bounds = (0.0, 0.0, 1.0, 1.0)
        
        min_lat, min_lng, max_lat, max_lng = gps_bounds
        
        # 计算图像定位坐标（左上角）
        latlng = {
            "lat": max_lat,
            "lng": min_lng
        }
        
        # 计算图像中心点坐标
        latlng_center = {
            "lat": (min_lat + max_lat) / 2,
            "lng": (min_lng + max_lng) / 2
        }
        
        print(f"图像定位坐标: {latlng}")
        print(f"图像中心坐标: {latlng_center}")
        
        # 计算所有检测点的GPS坐标
        coordinates = []
        for pred in predictions:
            # 获取检测框中心点
            if hasattr(pred.bbox, 'to_xyxy'):
                bbox = pred.bbox.to_xyxy()
            else:
                bbox = pred.bbox if isinstance(pred.bbox, list) else pred.bbox.tolist()
            
            # 计算检测框中心点（像素坐标，归一化到0-1）
            center_pixel_x = (bbox[0] + bbox[2]) / 2 / width
            center_pixel_y = (bbox[1] + bbox[3]) / 2 / height
            
            # 转换为GPS坐标
            gps_lng = min_lng + center_pixel_x * (max_lng - min_lng)
            gps_lat = max_lat - center_pixel_y * (max_lat - min_lat)  # 注意Y轴方向
            
            # 添加到坐标列表
            coordinates.append({
                "lat": gps_lat,
                "lng": gps_lng
            })
        
        print(f"成功计算 {len(coordinates)} 个检测点的GPS坐标 (EPSG:4326)")
        
        # 构建JSON数据
        json_data = {
            "count": len(coordinates),
            "coordinates": coordinates,
            "latlng": latlng,
            "latlng_center": latlng_center,
            "coordinate_system": "EPSG:4326 (WGS84)"
        }
        
        # 保存JSON文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"检测点GPS坐标文件已保存: {json_path}")
        print(f"文件大小: {os.path.getsize(json_path) / 1024:.2f} KB")
        print(f"坐标系统: EPSG:4326 (WGS84)")
        
        # 生成GeoJSON文件
        try:
            from shapely.geometry import Point
            
            print(f"开始生成GeoJSON文件...")
            
            # 准备GeoJSON数据结构
            geojson_data = {
                "type": "FeatureCollection",
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                    }
                },
                "features": []
            }
            
            for i, coord in enumerate(coordinates):
                # 创建Point几何对象 (经度, 纬度)
                point = Point(coord['lng'], coord['lat'])
                
                # 创建Feature对象
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [coord['lng'], coord['lat']]
                    },
                    "properties": {
                        'id': i + 1,
                        'longitude': coord['lng'],
                        'latitude': coord['lat'],
                        'category_id': predictions[i].category.id if i < len(predictions) else 0,
                        'category_name': predictions[i].category.name if i < len(predictions) else 'unknown',
                        'confidence': predictions[i].score.value if i < len(predictions) else 0.0
                    }
                }
                geojson_data["features"].append(feature)
            
            # 保存为GeoJSON文件
            with open(geojson_path, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, indent=2, ensure_ascii=False)
            
            print(f"GeoJSON文件已保存: {geojson_path}")
            print(f"GeoJSON文件大小: {os.path.getsize(geojson_path) / 1024:.2f} KB")
            print(f"包含 {len(geojson_data['features'])} 个检测点")
            
        except ImportError:
            print("警告: shapely未安装，跳过GeoJSON生成")
            print("安装命令: pip install shapely")
        except Exception as e:
            print(f"生成GeoJSON文件失败: {e}")
            print("继续执行，不影响JSON文件生成")
        
        return json_path
        
    except Exception as e:
        print(f"生成检测点GPS坐标文件失败: {e}")
        raise
    
    finally:
        # 清理内存
        gc.collect()

def process_large_image_batch_with_nms_option(
    image_path: str,
    model: YOLOv8Model,
    output_dir: str,
    tile_size: int = 1280,
    overlap_ratio: float = 0.02,
    memory_limit: int = 6 * 1024**3,
    skip_blank_tiles: bool = True,
    coco_json_output_path: Optional[str] = None,
    save_tiles: bool = False,
    tiles_output_dir: Optional[str] = None,
    generate_pts: bool = True,
    nms_method: str = "auto"
) -> List[ObjectPrediction]:
    """
    使用批量处理方式处理大图像（支持NMS方法选择）
    
    Args:
        image_path: 输入图像路径
        model: YOLOv8模型
        output_dir: 输出目录
        tile_size: 切片大小
        overlap_ratio: 重叠比例
        memory_limit: 内存限制
        skip_blank_tiles: 是否跳过空白切片
        coco_json_output_path: COCO格式JSON输出路径
        save_tiles: 是否保存切片到文件夹
        tiles_output_dir: 切片保存目录，如果为None则使用默认目录
        generate_pts: 是否生成检测点GPS坐标文件
        nms_method: NMS方法选择
            - "auto": 自动选择（推荐）
            - "advance": 高级NMS V1（基于检测框中心点）
            - "original": 原始OpenCV NMS
            - "chunked": 分块NMS
            - "gpu": GPU加速NMS
            - "benchmark": 基准测试所有方法
        
    Returns:
        检测结果列表
    """
    print(f"开始批量处理图像: {image_path}")
    print(f"选择的NMS方法: {nms_method}")
    
    # 创建切片保存目录
    if save_tiles:
        if tiles_output_dir is None:
            # 使用默认目录：基于输入图像名称
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            tiles_output_dir = os.path.join(output_dir, f"tiles_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        blank_tiles_dir = os.path.join(tiles_output_dir, "blank_tiles")
        efficient_tiles_dir = os.path.join(tiles_output_dir, "efficient_tiles")
        
        # 创建目录
        os.makedirs(blank_tiles_dir, exist_ok=True)
        os.makedirs(efficient_tiles_dir, exist_ok=True)
        
        print(f"切片将保存到: {tiles_output_dir}")
        print(f"空白切片目录: {blank_tiles_dir}")
        print(f"有效切片目录: {efficient_tiles_dir}")
    
    # 显示设备信息
    device_info = model.get_device_info()
    print(f"使用设备: {device_info['device_name']}")
    print(f"批量大小: {device_info['batch_size']}")
    if device_info['device'] == 'cuda':
        print(f"GPU内存: {device_info['memory_allocated']:.2f}GB / {device_info['memory_total']:.2f}GB")
    
    # 阶段1: 获取图像信息
    stage1_start = time.time()
    image_info = get_image_info_safe(image_path)
    if image_info is None:
        print("无法获取图像信息，请检查文件是否存在且格式正确")
        return []
    
    height, width, bands, image_size_gb = image_info
    print(f"Image dimensions: {width}x{height} | Channels: {bands}")
    print(f"Image size: {image_size_gb:.2f}GB")
    
    stage1_time = time.time() - stage1_start
    print(f"阶段1 - 获取图像信息: {stage1_time:.3f}s")
    
    # 阶段2: 生成切片边界框
    stage2_start = time.time()
    slice_bboxes = get_slice_bboxes(
        image_height=height,
        image_width=width,
        slice_height=tile_size,
        slice_width=tile_size,
        overlap_height_ratio=overlap_ratio,
        overlap_width_ratio=overlap_ratio
    )
    
    print(f"Generated {len(slice_bboxes)} slice bboxes")
    stage2_time = time.time() - stage2_start
    print(f"阶段2 - 生成切片边界框: {stage2_time:.3f}s")
    
    # 阶段3: 批量处理切片（与原始函数相同）
    stage3_start = time.time()
    all_object_predictions = []
    
    # 统计变量 - 严格区分读取失败和空白切片
    processed_tiles = 0          # 成功处理的有效切片数量
    read_failed_tiles = 0        # 读取失败的切片数量
    blank_tiles = 0              # 空白切片数量（成功读取但内容为空白）
    white_tiles = 0              # 全白切片数量
    black_tiles = 0              # 全黑切片数量
    saved_blank_tiles = 0        # 保存的空白切片数量
    saved_efficient_tiles = 0    # 保存的有效切片数量
    
    # 新增：收集空白切片索引
    blank_slice_indices = []     # 空白切片的索引列表
    
    batch_size = model.batch_size
    total_batches = (len(slice_bboxes) + batch_size - 1) // batch_size
    
    print(f"Processing {len(slice_bboxes)} tiles in {total_batches} batches (batch_size={batch_size})...")
    
    for batch_idx in range(total_batches):
        batch_start = time.time()
        
        # 准备当前批次的切片
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(slice_bboxes))
        current_batch_bboxes = slice_bboxes[start_idx:end_idx]
        
        # 读取当前批次的所有切片
        read_start = time.time()
        batch_tiles = []
        batch_bboxes = []
        batch_indices = []
        
        # 批次内统计
        batch_read_failed = 0
        batch_blank_tiles = 0
        batch_white_tiles = 0
        batch_black_tiles = 0
        
        for i, slice_bbox in enumerate(current_batch_bboxes):
            tile = read_tile_safe(
                image_path, 
                slice_bbox[0], slice_bbox[1], 
                slice_bbox[2], slice_bbox[3]
            )
            
            if tile is None:
                # 读取失败
                batch_read_failed += 1
                read_failed_tiles += 1
                print(f"读取切片 {start_idx + i + 1} 失败 (坐标: {slice_bbox})")
                continue
            
            # 成功读取，检查是否为空白切片
            is_blank = is_blank_tile(tile, threshold=0.95)
            
            # 保存切片到相应文件夹
            if save_tiles:
                tile_filename = f"tile_{start_idx + i + 1:06d}_x{slice_bbox[0]}_y{slice_bbox[1]}.jpg"
                
                if is_blank:
                    # 保存空白切片
                    blank_tile_path = os.path.join(blank_tiles_dir, tile_filename)
                    try:
                        # 确保图像是3通道RGB格式
                        if len(tile.shape) == 3:
                            if tile.shape[2] == 4:
                                tile_rgb = cv2.cvtColor(tile, cv2.COLOR_RGBA2RGB)
                            else:
                                tile_rgb = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
                        else:
                            tile_rgb = cv2.cvtColor(tile, cv2.COLOR_GRAY2RGB)
                        
                        cv2.imwrite(blank_tile_path, tile_rgb)
                        saved_blank_tiles += 1
                    except Exception as e:
                        print(f"保存空白切片失败: {e}")
                else:
                    # 保存有效切片
                    efficient_tile_path = os.path.join(efficient_tiles_dir, tile_filename)
                    try:
                        # 确保图像是3通道RGB格式
                        if len(tile.shape) == 3:
                            if tile.shape[2] == 4:
                                tile_rgb = cv2.cvtColor(tile, cv2.COLOR_RGBA2RGB)
                            else:
                                tile_rgb = cv2.cvtColor(tile, cv2.COLOR_BGR2RGB)
                        else:
                            tile_rgb = cv2.cvtColor(tile, cv2.COLOR_GRAY2RGB)
                        
                        cv2.imwrite(efficient_tile_path, tile_rgb)
                        saved_efficient_tiles += 1
                    except Exception as e:
                        print(f"保存有效切片失败: {e}")
            
            if is_blank:
                # 统计空白切片类型
                batch_blank_tiles += 1
                blank_tiles += 1
                
                # 记录空白切片索引
                blank_slice_indices.append(start_idx + i)
                
                if len(tile.shape) == 3:
                    if tile.shape[2] == 4:
                        gray = cv2.cvtColor(tile, cv2.COLOR_RGBA2GRAY)
                    else:
                        gray = cv2.cvtColor(tile, cv2.COLOR_RGB2GRAY)
                else:
                    gray = tile
                mean_val = np.mean(gray)
                if mean_val > 200:
                    batch_white_tiles += 1
                    white_tiles += 1
                else:
                    batch_black_tiles += 1
                    black_tiles += 1
                
                # 如果跳过空白切片，不添加到批次中
                if skip_blank_tiles:
                    continue
            
            # 添加到批次中（非空白切片或未跳过空白切片）
            batch_tiles.append(tile)
            batch_bboxes.append(slice_bbox)
            batch_indices.append(start_idx + i)
        
        read_time = time.time() - read_start
        
        # 批量推理
        inference_start = time.time()
        batch_predictions = model.predict_batch(batch_tiles, imgsz=tile_size)
        inference_time = time.time() - inference_start
        
        # 处理批量预测结果
        for i, (predictions, slice_bbox, tile_idx) in enumerate(zip(batch_predictions, batch_bboxes, batch_indices)):
            # 调整预测坐标到原图坐标系
            for pred in predictions:
                if hasattr(pred.bbox, 'to_xyxy'):
                    bbox = pred.bbox.to_xyxy()
                else:
                    bbox = pred.bbox if isinstance(pred.bbox, list) else pred.bbox.tolist()
                
                # 调整坐标
                adjusted_bbox = [
                    bbox[0] + slice_bbox[0],  # x1
                    bbox[1] + slice_bbox[1],  # y1
                    bbox[2] + slice_bbox[0],  # x2
                    bbox[3] + slice_bbox[1]   # y2
                ]
                
                # 创建新的预测对象
                adjusted_pred = ObjectPrediction(
                    bbox=adjusted_bbox,
                    category_id=pred.category.id,
                    category_name=pred.category.name,
                    score=pred.score.value
                )
                all_object_predictions.append(adjusted_pred)
            
            processed_tiles += 1
        
        batch_time = time.time() - batch_start
        batch_detections = sum(len(preds) for preds in batch_predictions)
        
        print(f"批次 {batch_idx + 1}/{total_batches} | 切片 {start_idx + 1}-{end_idx} | 读取: {read_time:.3f}s | 批量推理: {inference_time:.3f}s | 检测: {batch_detections}个 | 总时间: {batch_time:.3f}s")
        
        # 定期清理内存
        if batch_idx % 10 == 0:
            gc.collect()
            if model.device == 'cuda':
                model.clear_gpu_memory()
    
    stage3_time = time.time() - stage3_start
    print(f"阶段3 - 批量处理切片: {stage3_time:.3f}s")
    
    # 详细的统计报告
    print(f"\n=== 切片处理统计报告 ===")
    print(f"总切片数量: {len(slice_bboxes)}")
    print(f"成功读取切片: {len(slice_bboxes) - read_failed_tiles}")
    print(f"读取失败切片: {read_failed_tiles} ({read_failed_tiles/len(slice_bboxes)*100:.1f}%)")
    print(f"空白切片: {blank_tiles} ({blank_tiles/len(slice_bboxes)*100:.1f}%)")
    print(f"  - 全白切片: {white_tiles}")
    print(f"  - 全黑切片: {black_tiles}")
    print(f"有效处理切片: {processed_tiles} ({processed_tiles/len(slice_bboxes)*100:.1f}%)")
    print(f"空白切片索引: {len(blank_slice_indices)} 个")
    
    if save_tiles:
        print(f"切片保存统计: 空白切片 {saved_blank_tiles}, 有效切片 {saved_efficient_tiles}")
    
    # 阶段4: 后处理合并（根据选择的NMS方法）
    stage4_start = time.time()
    print("开始合并结果...")
    print(f"合并前检测数量: {len(all_object_predictions)}")
    
    detection_count = len(all_object_predictions)
    
    if nms_method == "benchmark":
        # 基准测试所有方法
        print("执行NMS方法基准测试...")
        benchmark_results = benchmark_advance_nms(
            all_object_predictions, slice_bboxes, tile_size, overlap_ratio, iou_threshold=0.5, blank_slice_indices=blank_slice_indices
        )
        # 使用性能最好的方法的结果
        best_method = min(benchmark_results.items(), key=lambda x: x[1]["时间"] if "时间" in x[1] else float('inf'))
        print(f"选择最佳方法: {best_method[0]}")
        combined_predictions = all_object_predictions  # 基准测试会返回结果，这里需要重新计算
        
    elif nms_method == "advance":
        print("使用高级NMS（正确的重叠区域定义，支持扩展）...")
        combined_predictions = advance_nms_postprocess(
            all_object_predictions, slice_bboxes, tile_size, overlap_ratio, iou_threshold=0.5, blank_slice_indices=blank_slice_indices, overlap_expansion_ratio=1.6
        )
        
    elif nms_method == "original":
        print("使用原始OpenCV NMS...")
        combined_predictions = custom_nms_postprocess_original(all_object_predictions, iou_threshold=0.5)
        
    elif nms_method == "chunked":
        print("使用分块NMS...")
        combined_predictions = custom_nms_chunked(all_object_predictions, iou_threshold=0.5, chunk_size=10000)
        
    elif nms_method == "gpu":
        print("使用GPU加速NMS...")
        try:
            combined_predictions = custom_nms_gpu_optimized(all_object_predictions, iou_threshold=0.5)
        except Exception as e:
            print(f"GPU NMS失败: {e}，回退到原始NMS")
            combined_predictions = custom_nms_postprocess_original(all_object_predictions, iou_threshold=0.5)
            
    else:  # "auto"
        # 自动选择策略（与原始函数相同）
        print("自动选择NMS策略...")
        try:
            combined_predictions = advance_nms_postprocess(
                all_object_predictions, slice_bboxes, tile_size, overlap_ratio, iou_threshold=0.5, blank_slice_indices=blank_slice_indices, overlap_expansion_ratio=1.6
            )
            print("高级NMS处理成功")
        except Exception as e:
            print(f"高级NMS处理失败: {e}")
            print("回退到传统NMS策略")
            
            # 检查GPU是否可用
            gpu_available = torch.cuda.is_available() if hasattr(torch, 'cuda') else False
            
            if gpu_available:
                # GPU可用，优先使用GPU NMS
                print(f"GPU可用，优先使用GPU NMS")
                try:
                    combined_predictions = custom_nms_gpu_optimized(all_object_predictions, iou_threshold=0.5)
                    print("GPU NMS处理成功")
                except Exception as e:
                    print(f"GPU NMS处理失败: {e}")
                    print("回退到CPU NMS策略")
                    # GPU NMS失败，回退到CPU策略
                    if detection_count <= 50000:
                        print(f"检测数量 {detection_count} <= 50000，使用OpenCV NMS")
                        combined_predictions = custom_nms_postprocess_original(all_object_predictions, iou_threshold=0.5)
                    else:
                        print(f"检测数量 {detection_count} > 50000，使用分块NMS")
                        combined_predictions = custom_nms_chunked(all_object_predictions, iou_threshold=0.5, chunk_size=10000)
            else:
                # GPU不可用，根据检测数量选择CPU NMS策略
                if detection_count <= 50000:
                    print(f"GPU不可用，检测数量 {detection_count} <= 50000，使用OpenCV NMS")
                    combined_predictions = custom_nms_postprocess_original(all_object_predictions, iou_threshold=0.5)
                else:
                    print(f"GPU不可用，检测数量 {detection_count} > 50000，使用分块NMS")
                    combined_predictions = custom_nms_chunked(all_object_predictions, iou_threshold=0.5, chunk_size=10000)
    
    stage4_time = time.time() - stage4_start
    print(f"阶段4 - 后处理合并: {stage4_time:.3f}s")
    print(f"合并后检测结果: {len(combined_predictions)}个")
    print(f"NMS压缩比: {detection_count}/{len(combined_predictions)} = {detection_count/len(combined_predictions):.2f}:1")
    
    # 阶段6: 导出COCO JSON结果（可选）
    if coco_json_output_path:
        stage5_start = time.time()
        export_results_to_coco_json(combined_predictions, image_path, coco_json_output_path)
        stage5_time = time.time() - stage5_start
        print(f"阶段5 - 导出COCO JSON结果: {stage5_time:.3f}s")
    
    # 阶段6: 生成检测点GPS坐标文件
    stage6_start = time.time()
    if generate_pts:
        try:
            print("\n=== 生成检测点GPS坐标文件 ===")
            pts_start = time.time()
            pts_json_path = gen_detection_pts(image_path, combined_predictions, output_dir=output_dir)
            pts_time = time.time() - pts_start
            print(f"检测点GPS坐标文件生成完成: {pts_time:.3f}s")
            print(f"文件路径: {pts_json_path}")
        except Exception as e:
            print(f"生成检测点GPS坐标文件失败: {e}")
            print("继续执行，不影响主要功能")
    else:
        print("\n跳过生成检测点GPS坐标文件")
    stage6_time = time.time() - stage6_start
    print(f"阶段6 - 生成检测点GPS坐标文件: {stage6_time:.3f}s")
    
    # 阶段7: 生成切片边框GeoJSON文件
    stage7_start = time.time()
    try:
        print("\n=== 生成切片边框GeoJSON文件 ===")
        slices_geojson_start = time.time()
        slices_geojson_path = gen_slices_geojson(
            image_path=image_path,
            slice_bboxes=slice_bboxes,
            blank_slice_indices=blank_slice_indices,
            output_dir=output_dir,
            tile_size=tile_size,
            overlap_ratio=overlap_ratio
        )
        slices_geojson_time = time.time() - slices_geojson_start
        if slices_geojson_path:
            print(f"切片边框GeoJSON文件生成完成: {slices_geojson_time:.3f}s")
            print(f"文件路径: {slices_geojson_path}")
        else:
            print("切片边框GeoJSON文件生成失败")
    except Exception as e:
        print(f"生成切片边框GeoJSON文件失败: {e}")
        print("继续执行，不影响主要功能")
    stage7_time = time.time() - stage7_start
    print(f"阶段7 - 生成切片边框GeoJSON文件: {stage7_time:.3f}s")
    
    # 总时间统计
    total_time = time.time() - stage1_start
    print(f"\n=== 总处理时间统计 ===")
    print(f"阶段1 - 获取图像信息: {stage1_time:.3f}s")
    print(f"阶段2 - 生成切片边界框: {stage2_time:.3f}s")
    print(f"阶段3 - 批量处理切片: {stage3_time:.3f}s")
    print(f"阶段4 - 后处理合并: {stage4_time:.3f}s")
    if coco_json_output_path:
        print(f"阶段5 - 导出COCO JSON结果: {stage5_time:.3f}s")
    if generate_pts:
        print(f"阶段6 - 生成检测点GPS坐标文件: {stage6_time:.3f}s")
    print(f"阶段7 - 生成切片边框GeoJSON文件: {stage7_time:.3f}s")
    print(f"总处理时间: {total_time:.3f}s")
    print(f"平均每切片时间: {total_time/len(slice_bboxes):.3f}s")
    print(f"平均每批次时间: {total_time/total_batches:.3f}s")
    
    return combined_predictions

def gen_slices_geojson(
    image_path: str,
    slice_bboxes: List[Tuple[int, int, int, int]],
    blank_slice_indices: List[int],
    output_dir: Optional[str] = None,
    tile_size: int = 1280,
    overlap_ratio: float = 0.05
) -> str:
    """
    生成非空白切片的边框GeoJSON文件
    
    Args:
        image_path: 输入图像路径
        slice_bboxes: 所有切片的边界框列表 [(x1, y1, x2, y2), ...]
        blank_slice_indices: 空白切片的索引列表
        output_dir: 输出目录，如果为None则使用图像所在目录
        tile_size: 切片大小
        overlap_ratio: 重叠比例
        
    Returns:
        str: 生成的GeoJSON文件路径
    """
    print(f"开始生成切片边框GeoJSON文件...")
    print(f"总切片数量: {len(slice_bboxes)}")
    print(f"空白切片数量: {len(blank_slice_indices)}")
    print(f"非空白切片数量: {len(slice_bboxes) - len(blank_slice_indices)}")
    
    # 获取输出目录
    if output_dir is None:
        output_dir = os.path.dirname(image_path)
    
    # 获取文件名（不含扩展名）
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    geojson_filename = f"{base_name}_slices_border.geojson"
    geojson_path = os.path.join(output_dir, geojson_filename)
    
    try:
        # 获取图像信息
        image_info = get_image_info_safe(image_path)
        if image_info is None:
            raise ValueError(f"无法获取图像信息: {image_path}")
        
        height, width, bands, image_size_gb = image_info
        print(f"图像尺寸: {width} x {height}")
        
        # 尝试获取地理坐标信息
        try:
            
            with rasterio.open(image_path) as src:
                bounds = src.bounds
                crs = src.crs
                transform = src.transform
                
                print(f"图像边界: {bounds}")
                print(f"坐标系统: {crs}")
                
                # 如果坐标系统不是EPSG:4326，需要转换
                if crs != CRS.from_epsg(4326):
                    print(f"转换坐标系统从 {crs} 到 EPSG:4326 (WGS84)...")
                    wgs84_bounds = transform_bounds(crs, CRS.from_epsg(4326), 
                                                  bounds.left, bounds.bottom, 
                                                  bounds.right, bounds.top)
                else:
                    wgs84_bounds = bounds
                
                has_geo_info = True
                
        except Exception as e:
            print(f"无法获取地理坐标信息: {e}")
            print("使用像素坐标系统")
            has_geo_info = False
            wgs84_bounds = None
            transform = None
        
        # 生成非空白切片的边框
        try:
            from shapely.geometry import Polygon
            
            print(f"开始生成切片边框GeoJSON文件...")
            
            # 准备GeoJSON数据结构
            geojson_data = {
                "type": "FeatureCollection",
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                    }
                },
                "features": []
            }
            
            # 计算重叠像素数
            overlap_pixels = int(tile_size * overlap_ratio)
            
            for i, slice_bbox in enumerate(slice_bboxes):
                # 跳过空白切片
                if i in blank_slice_indices:
                    continue
                
                x1, y1, x2, y2 = slice_bbox
                
                # 计算切片的重叠区域边界
                overlap_left = x1 + overlap_pixels
                overlap_right = x2 - overlap_pixels
                overlap_top = y1 + overlap_pixels
                overlap_bottom = y2 - overlap_pixels
                
                if has_geo_info and transform is not None:
                    # 使用地理坐标
                    # 转换切片边界到地理坐标
                    geo_x1, geo_y1 = transform * (x1, y1)
                    geo_x2, geo_y2 = transform * (x2, y2)
                    geo_overlap_left, geo_overlap_top = transform * (overlap_left, overlap_top)
                    geo_overlap_right, geo_overlap_bottom = transform * (overlap_right, overlap_bottom)
                    
                    # 如果坐标系统不是EPSG:4326，需要转换
                    if crs != CRS.from_epsg(4326):
                        geo_x1, geo_y1 = transform_bounds(crs, CRS.from_epsg(4326), 
                                                        geo_x1, geo_y1, geo_x1, geo_y1)[:2]
                        geo_x2, geo_y2 = transform_bounds(crs, CRS.from_epsg(4326), 
                                                        geo_x2, geo_y2, geo_x2, geo_y2)[:2]
                        geo_overlap_left, geo_overlap_top = transform_bounds(crs, CRS.from_epsg(4326), 
                                                                           geo_overlap_left, geo_overlap_top, 
                                                                           geo_overlap_left, geo_overlap_top)[:2]
                        geo_overlap_right, geo_overlap_bottom = transform_bounds(crs, CRS.from_epsg(4326), 
                                                                               geo_overlap_right, geo_overlap_bottom, 
                                                                               geo_overlap_right, geo_overlap_bottom)[:2]
                    
                    # 计算中心点坐标
                    center_x = (geo_x1 + geo_x2) / 2
                    center_y = (geo_y1 + geo_y2) / 2
                    
                else:
                    # 使用像素坐标（简单投影）
                    # 将像素坐标转换为简单的经纬度坐标
                    # 假设图像覆盖1度x1度的区域
                    lat_range = 1.0
                    lng_range = 1.0
                    
                    # 归一化像素坐标到0-1
                    norm_x1 = x1 / width
                    norm_y1 = y1 / height
                    norm_x2 = x2 / width
                    norm_y2 = y2 / height
                    norm_overlap_left = overlap_left / width
                    norm_overlap_top = overlap_top / height
                    norm_overlap_right = overlap_right / width
                    norm_overlap_bottom = overlap_bottom / height
                    
                    # 转换为经纬度坐标（假设从(0,0)开始）
                    geo_x1 = norm_x1 * lng_range
                    geo_y1 = (1 - norm_y1) * lat_range  # 注意Y轴方向
                    geo_x2 = norm_x2 * lng_range
                    geo_y2 = (1 - norm_y2) * lat_range
                    geo_overlap_left = norm_overlap_left * lng_range
                    geo_overlap_top = (1 - norm_overlap_top) * lat_range
                    geo_overlap_right = norm_overlap_right * lng_range
                    geo_overlap_bottom = (1 - norm_overlap_bottom) * lat_range
                    
                    # 计算中心点坐标
                    center_x = (geo_x1 + geo_x2) / 2
                    center_y = (geo_y1 + geo_y2) / 2
                
                # 添加完整切片边框Feature
                full_slice_feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [geo_x1, geo_y1],  # 左上
                            [geo_x2, geo_y1],  # 右上
                            [geo_x2, geo_y2],  # 右下
                            [geo_x1, geo_y2],  # 左下
                            [geo_x1, geo_y1]   # 闭合
                        ]]
                    },
                    "properties": {
                        "id": i + 1,
                        "slice_index": i,
                        "type": "full_slice",
                        "pixel_x1": x1,
                        "pixel_y1": y1,
                        "pixel_x2": x2,
                        "pixel_y2": y2,
                        "center_lng": center_x,
                        "center_lat": center_y,
                        "width": x2 - x1,
                        "height": y2 - y1,
                        "area_pixels": (x2 - x1) * (y2 - y1),
                        "is_blank": False,
                        "overlap_ratio": overlap_ratio,
                        "tile_size": tile_size
                    }
                }
                geojson_data["features"].append(full_slice_feature)
                
                # 添加重叠区域边框Feature
                overlap_region_feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [geo_overlap_left, geo_overlap_top],      # 左上
                            [geo_overlap_right, geo_overlap_top],     # 右上
                            [geo_overlap_right, geo_overlap_bottom],  # 右下
                            [geo_overlap_left, geo_overlap_bottom],   # 左下
                            [geo_overlap_left, geo_overlap_top]       # 闭合
                        ]]
                    },
                    "properties": {
                        "id": i + 1,
                        "slice_index": i,
                        "type": "overlap_region",
                        "pixel_x1": overlap_left,
                        "pixel_y1": overlap_top,
                        "pixel_x2": overlap_right,
                        "pixel_y2": overlap_bottom,
                        "center_lng": (geo_overlap_left + geo_overlap_right) / 2,
                        "center_lat": (geo_overlap_top + geo_overlap_bottom) / 2,
                        "width": overlap_right - overlap_left,
                        "height": overlap_bottom - overlap_top,
                        "area_pixels": (overlap_right - overlap_left) * (overlap_bottom - overlap_top),
                        "is_blank": False,
                        "overlap_ratio": overlap_ratio,
                        "tile_size": tile_size
                    }
                }
                geojson_data["features"].append(overlap_region_feature)
            
            # 保存为GeoJSON文件
            with open(geojson_path, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, indent=2, ensure_ascii=False)
            
            print(f"切片边框GeoJSON文件已保存: {geojson_path}")
            print(f"GeoJSON文件大小: {os.path.getsize(geojson_path) / 1024:.2f} KB")
            print(f"包含 {len(geojson_data['features'])} 个几何对象")
            print(f"  - 完整切片边框: {len([f for f in geojson_data['features'] if f['properties']['type'] == 'full_slice'])} 个")
            print(f"  - 重叠区域边框: {len([f for f in geojson_data['features'] if f['properties']['type'] == 'overlap_region'])} 个")
            
            # 生成统计信息
            full_slices = [f for f in geojson_data['features'] if f['properties']['type'] == 'full_slice']
            overlap_regions = [f for f in geojson_data['features'] if f['properties']['type'] == 'overlap_region']
            
            if full_slices:
                total_area = sum(f['properties']['area_pixels'] for f in full_slices)
                avg_area = total_area / len(full_slices)
                print(f"切片统计:")
                print(f"  - 平均切片面积: {avg_area:.0f} 像素")
                print(f"  - 总切片面积: {total_area:.0f} 像素")
            
            if overlap_regions:
                total_overlap_area = sum(f['properties']['area_pixels'] for f in overlap_regions)
                avg_overlap_area = total_overlap_area / len(overlap_regions)
                print(f"重叠区域统计:")
                print(f"  - 平均重叠区域面积: {avg_overlap_area:.0f} 像素")
                print(f"  - 总重叠区域面积: {total_overlap_area:.0f} 像素")
                print(f"  - 重叠区域占比: {total_overlap_area/total_area*100:.1f}%")
            
            return geojson_path
            
        except ImportError:
            print("警告: shapely未安装，跳过GeoJSON生成")
            print("安装命令: pip install shapely")
            return None
        except Exception as e:
            print(f"生成GeoJSON文件失败: {e}")
            return None
        
    except Exception as e:
        print(f"生成切片边框GeoJSON文件失败: {e}")
        return None
    
    finally:
        # 清理内存
        gc.collect()

def advance_nms_postprocess(
    object_predictions: List[ObjectPrediction], 
    slice_bboxes: List[Tuple[int, int, int, int]],
    tile_size: int,
    overlap_ratio: float,
    iou_threshold: float = 0.5,
    blank_slice_indices: Optional[List[int]] = None,
    overlap_expansion_ratio: float = 1.6
) -> List[ObjectPrediction]:
    """
    高级NMS处理版本3 - 正确的切片间重叠区域判断（支持重叠区域扩展）
    
    修正的重叠区域定义：
    重叠区域 = 切片边缘的重叠部分，即相邻切片之间的重叠区域
    非重叠区域 = 切片中心的不重叠部分
    
    重叠区域扩展：
    如果切片重叠比例是0.05，那么将切片边缘的0.08作为重叠区域（按比例扩大）
    
    Args:
        object_predictions: 所有检测结果（已调整到原图坐标系）
        slice_bboxes: 切片边界框列表 [(x1, y1, x2, y2), ...]
        tile_size: 切片大小
        overlap_ratio: 重叠比例
        iou_threshold: IoU阈值
        blank_slice_indices: 空白切片的索引列表，如果为None则不跳过任何切片
        overlap_expansion_ratio: 重叠区域扩展比例，默认1.6（0.05 * 1.6 = 0.08）
        
    Returns:
        去重后的检测结果列表
    """
    if not object_predictions:
        return []
    
    # 记录预处理开始时间
    preprocessing_start = time.time()
    
    print(f"开始高级NMS处理V3，检测框数量: {len(object_predictions)}")
    print(f"切片数量: {len(slice_bboxes)}, 切片大小: {tile_size}, 重叠比例: {overlap_ratio}")
    print(f"重叠区域扩展比例: {overlap_expansion_ratio}")
    if blank_slice_indices:
        print(f"空白切片数量: {len(blank_slice_indices)}")
    
    # 计算重叠像素数（扩展后的重叠区域）
    expanded_overlap_ratio = overlap_ratio * overlap_expansion_ratio
    overlap_pixels = int(tile_size * expanded_overlap_ratio)
    original_overlap_pixels = int(tile_size * overlap_ratio)
    
    print(f"原始重叠像素数: {original_overlap_pixels}")
    print(f"扩展后重叠像素数: {overlap_pixels}")
    print(f"扩展比例: {overlap_ratio} -> {expanded_overlap_ratio}")
    
    # 分离重叠区域和非重叠区域的检测框
    overlap_predictions = []      # 需要NMS的检测框（在切片重叠区域）
    non_overlap_predictions = []  # 直接保留的检测框（在切片非重叠区域）
    
    # 统计信息
    total_predictions = len(object_predictions)
    overlap_count = 0
    non_overlap_count = 0
    skipped_blank_count = 0
    
    for pred in object_predictions:
        if hasattr(pred.bbox, 'to_xyxy'):
            bbox = pred.bbox.to_xyxy()
        else:
            bbox = pred.bbox if isinstance(pred.bbox, list) else pred.bbox.tolist()
        
        # 计算检测框中心点
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2
        
        # 检查是否在重叠区域
        is_in_overlap = False
        current_slice_index = -1
        
        for slice_idx, slice_bbox in enumerate(slice_bboxes):
            x1, y1, x2, y2 = slice_bbox
            
            # 正确的重叠区域定义（使用扩展后的重叠区域）：
            # 重叠区域 = 切片边缘的扩展重叠部分
            # 非重叠区域 = 切片中心的不重叠部分
            
            # 计算切片的非重叠区域边界（切片中心部分，使用扩展后的重叠像素数）
            non_overlap_left = x1 + overlap_pixels
            non_overlap_right = x2 - overlap_pixels
            non_overlap_top = y1 + overlap_pixels
            non_overlap_bottom = y2 - overlap_pixels
            
            # 检查检测框中心是否在非重叠区域内
            if (non_overlap_left <= center_x <= non_overlap_right and 
                non_overlap_top <= center_y <= non_overlap_bottom):
                # 检测框在非重叠区域（切片中心），不需要NMS
                is_in_overlap = False
                current_slice_index = slice_idx
                break
            elif (x1 <= center_x <= x2 and y1 <= center_y <= y2):
                # 检测框在切片内但不在非重叠区域，说明在重叠区域
                is_in_overlap = True
                current_slice_index = slice_idx
                break
        
        # 检查是否来自空白切片
        is_from_blank_slice = False
        if blank_slice_indices and current_slice_index >= 0:
            is_from_blank_slice = current_slice_index in blank_slice_indices
        
        # 如果来自空白切片，跳过该检测框
        if is_from_blank_slice:
            skipped_blank_count += 1
            continue
        
        # 根据位置分类
        if is_in_overlap:
            overlap_predictions.append(pred)
            overlap_count += 1
        else:
            non_overlap_predictions.append(pred)
            non_overlap_count += 1
    
    # 记录预处理结束时间
    preprocessing_time = time.time() - preprocessing_start
    
    print(f"检测框分类统计:")
    print(f"  重叠区域检测框: {overlap_count} ({overlap_count/total_predictions*100:.1f}%)")
    print(f"  非重叠区域检测框: {non_overlap_count} ({non_overlap_count/total_predictions*100:.1f}%)")
    if blank_slice_indices:
        print(f"  跳过空白切片检测框: {skipped_blank_count} ({skipped_blank_count/total_predictions*100:.1f}%)")
    print(f"  预处理耗时: {preprocessing_time:.3f}秒")
    
    nms_process_start = time.time()
    # 对重叠区域的检测框执行NMS
    if overlap_predictions:
        print(f"对重叠区域 {len(overlap_predictions)} 个检测框执行NMS...")
        
        # 根据重叠区域检测框数量选择NMS策略
        if len(overlap_predictions) < 50000:
            nms_result = custom_nms_postprocess_original(overlap_predictions, iou_threshold)
        elif len(overlap_predictions) >= 50000:
            nms_result = custom_nms_chunked(overlap_predictions, iou_threshold, 10000)
        
        print(f"NMS后重叠区域保留: {len(nms_result)} 个检测框")
        print(f"重叠区域NMS压缩比: {len(overlap_predictions)}/{len(nms_result)} = {len(overlap_predictions)/len(nms_result):.2f}:1")
    else:
        nms_result = []
        print("重叠区域无检测框，跳过NMS")
    
    # 合并结果
    final_result = non_overlap_predictions + nms_result
    nms_process_time = time.time() - nms_process_start
    print(f"NMS处理耗时: {nms_process_time:.3f}秒")
    
    print(f"最终结果统计 (V3):")
    print(f"  非重叠区域保留: {len(non_overlap_predictions)} 个")
    print(f"  重叠区域NMS后: {len(nms_result)} 个")
    print(f"  总计: {len(final_result)} 个")
    print(f"总体压缩比: {total_predictions}/{len(final_result)} = {total_predictions/len(final_result):.2f}:1")
    print(f"预处理耗时: {preprocessing_time:.3f}秒")
    print(f"NMS处理耗时: {nms_process_time:.3f}秒")
    
    return final_result, overlap_predictions

def run_slicing(
    input_path: str,
    model_dir: str="",
    output_dir: str=".",
    tile_size: int = 1280,
    overlap_ratio: float = 0.05,
    memory_limit: int = 6 * 1024**3,
    confidence_threshold: float = 0.3,
    skip_blank_tiles: bool = True,
    coco_json_output_path: Optional[str] = None,
    save_tiles: bool = False,
    tiles_output_dir: Optional[str] = None,
    device: str = None,
    generate_pts: bool = True,
    nms_method: str = "auto",
    local_run: bool = False
) -> List[ObjectPrediction]:
    """
    运行切片检测的主函数
    
    Args:
        input_path: 输入图像路径
        model_dir: 模型文件路径
        tile_size: 切片大小
        overlap_ratio: 切片重叠比例
        memory_limit: 内存限制
        confidence_threshold: 检测置信度阈值
        skip_blank_tiles: 是否跳过空白切片
        coco_json_output_path: COCO格式JSON输出路径
        save_tiles: 是否保存切片到文件夹
        tiles_output_dir: 切片保存目录
        device: 设备类型 ('auto', 'cpu', 'cuda', 'mps')，None表示自动选择
        generate_pts: 是否生成检测点GPS坐标文件
        nms_method: NMS方法选择
            - "auto": 自动选择（推荐）
            - "advance": 高级NMS （正确的重叠区域定义）
            - "original": 原始OpenCV NMS
            - "chunked": 分块NMS
            - "gpu": GPU加速NMS
            - "benchmark": 基准测试所有方法
        
    Returns:
        检测结果列表
    """
    if model_dir == "":
        #download model
        model_path = download.download_file_requests(_MODEL_LIST["download_url"])
    else:
        model_path = os.path.join(model_dir, _MODEL_LIST["default"]) 
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    coco_json_output_path = os.path.join(output_dir, f"{base_name}_coco.json")
    print("=" * 60)
    print("开始运行切片检测")
    print("=" * 60)
    print(f"输入图像: {input_path}")
    print(f"模型路径: {model_path}")
    print(f"切片大小: {tile_size}")
    print(f"重叠比例: {overlap_ratio}")
    print(f"置信度阈值: {confidence_threshold}")
    print(f"内存限制: {memory_limit / (1024**3):.1f}GB")
    print(f"跳过空白切片: {skip_blank_tiles}")
    print(f"保存切片: {save_tiles}")
    print(f"NMS方法: {nms_method}")
    if device:
        print(f"指定设备: {device}")
    print("=" * 60)
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入图像文件不存在: {input_path}")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    # 初始化模型
    print("正在初始化模型...")
    model = YOLOv8Model(model_path, confidence_threshold, device)
    
    # 使用批量处理模式（支持NMS方法选择）
    print("开始处理图像...")
    if nms_method != "auto":
        # 使用支持NMS选择的函数
        results = process_large_image_batch_with_nms_option(
            image_path=input_path,
            model=model,
            output_dir=output_dir,
            tile_size=tile_size,
            overlap_ratio=overlap_ratio,
            memory_limit=memory_limit,
            skip_blank_tiles=skip_blank_tiles,
            coco_json_output_path=coco_json_output_path,
            save_tiles=save_tiles,
            tiles_output_dir=tiles_output_dir,
            generate_pts=generate_pts,
            nms_method=nms_method
        )
    else:
        # 使用默认函数（已集成高级NMS）
        results = process_large_image_batch(
            image_path=input_path,
            model=model,
            output_dir=output_dir,
            tile_size=tile_size,
            overlap_ratio=overlap_ratio,
            memory_limit=memory_limit,
            skip_blank_tiles=skip_blank_tiles,
            coco_json_output_path=coco_json_output_path,
            save_tiles=save_tiles,
            tiles_output_dir=tiles_output_dir,
            generate_pts=generate_pts
        )
    
    # print(f"results: {results}")    
    # result_list = results.to_coco_predictions() 

    # 如果local_run为True，从本文件夹导入tiffProc，否则从counting/utils/tiffProc.py导入
    if local_run:
        import tiffProc
    else:
        from ..utils import tiffProc

    raw_start = time.time()
    raw_tif_path = os.path.join(output_dir, f"{base_name}_raw.tif")
    # tiffProc.create_detection_geotiff(result_list, input_file, raw_tif_path)
    # tiffProc.create_detection_geotiff(input_path, raw_tif_path)
    shutil.copy(input_path, raw_tif_path)   # 复制原始tif文件到输出目录， 没有必要另外生成raw tif。节省时间。
    raw_time = time.time() - raw_start
    print(f"生成原始Raw GeoTIFF文件: {raw_time:.3f}s")

    # 生成COG GeoTIFF
    cog_start = time.time()
    cog_tif_path = os.path.join(output_dir, f"{base_name}_cog.tif")
    tiffProc.convert_to_cog(input_path, cog_tif_path, compress="JPEG", quality=75, block_size=512)        ### 使用原始tiff, 压缩算法:JPEG; block size = 512
    cog_time = time.time() - cog_start
    print(f"生成COG GeoTIFF文件: {cog_time:.3f}s")
    
    # 生成JPG图像
    jpg_start = time.time()
    jpg_path = os.path.join(output_dir, f"{base_name}.jpg")
    tiffProc.convert_to_jpg(raw_tif_path, jpg_path)
    jpg_time = time.time() - jpg_start
    print(f"生成JPG图像: {jpg_time:.3f}s")

    print("=" * 60)
    print("检测完成")
    print(f"最终检测结果: {len(results)}个目标")
    print("=" * 60)
    

if __name__ == "__main__":

    '''
    # 方式1: 使用默认参数
    results = run_slicing("path/to/image.tif")

    # 方式2: 自定义参数
    results = run_slicing(
        image_path="path/to/image.tif",
        model_path="path/to/model.pt",
        tile_size=1024,
        overlap_ratio=0.1,
        confidence_threshold=0.5
    )

    # 方式3: 使用配置字典
    config = {
        "image_path": "path/to/image.tif",
        "tile_size": 1280,
        "overlap_ratio": 0.02,
        "confidence_threshold": 0.3
    }
    results = run_slicing(**config)
    '''
    # 大小 792M
    image_path1 = "D:/ChenQiu/云稷/20250214_张掖玉米苗情与长势/张掖国金-玉米/2025/玉米/图像切割与标注/20250529-0530-拼接结果/20250529_晨光村_4号点_12M.tif"
    # 大小 2.7G
    image_path2 = "D:/ChenQiu/云稷/20250214_张掖玉米苗情与长势/张掖国金-玉米/2025/玉米/图像切割与标注/20250529-0530-拼接结果/20250530_晨光村_2号点_12m.tif"
    # 大小 3.9G
    image_path3 = "20250522-晨光村-15区-12M-result.tif"
    # 大小 9.3G
    image_path4 = "D:/ChenQiu/云稷/20250125_中种国际/20250623_超大图像/数苗测试_15m重叠率60.tif"

    # 配置参数
    output_dir = "result-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    config = {
        "input_path": image_path4,
        "model_dir": "D:/ChenQiu/Project/cropmirror/ai-engine-local/_internal/model/cornpt",
        "output_dir": output_dir,
        "tile_size": 1280,
        "overlap_ratio": 0.05,
        "memory_limit": 6 * 1024**3,
        "confidence_threshold": 0.3,
        "skip_blank_tiles": True,
        "coco_json_output_path": os.path.join(output_dir, "detection_results_coco.json"),
        "save_tiles": False,
        "tiles_output_dir": None,
        "device": None,  # 自动选择设备
        "generate_pts": True,
        "local_run": True
    }
    
    config2 = {
        "input_path": image_path3,
        "model_dir": "D:/ChenQiu/Project/cropmirror/ai-engine-local/_internal/model/cornpt",
        "output_dir": output_dir,
        "generate_pts": True,
        "local_run": True
    }

    # 运行切片检测
    # run_slicing(model_dir=model_file, input_path=input_path, output_dir=output_dir)
    run_slicing(**config)
