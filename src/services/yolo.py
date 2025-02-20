from libs.YOLO import YOLOv8
from libs.PipeLine import PipeLine

from media.sensor import *
from media.display import *
from media.media import *
import utime

LOGNAME = "yolo"

sensor_id = 2
sensor = None

from src.services.utils import logging


def initialize_pipeline(CONFIG: dict) -> PipeLine:
    """
    初始化显示管道

    参数：
        CONFIG: 配置字典，包含rgb888p_size、display_size、display_mode等参数
    返回：
        PipeLine对象：初始化后的显示管道实例
    """
    pl = PipeLine(
        rgb888p_size=CONFIG["rgb888p_size"],
        display_size=CONFIG["display_size"],
        display_mode=CONFIG["display_mode"],
    )
    pl.create()
    return pl


def initialize_yolo(CONFIG: dict) -> YOLOv8:
    """
    初始化 YOLO 模型

    参数：
        CONFIG: 配置字典，包含模型相关参数
    返回：
        YOLOv8对象：初始化后的YOLO检测模型实例
    """
    yolo = YOLOv8(
        task_type="detect",
        mode="video",
        kmodel_path=CONFIG["kmodel_path"],
        labels=CONFIG["labels"],
        rgb888p_size=CONFIG["rgb888p_size"],
        model_input_size=CONFIG["model_input_size"],
        display_size=CONFIG["display_size"],
        conf_thresh=CONFIG["conf_thresh"],
        nms_thresh=CONFIG["nms_thresh"],
        max_boxes_num=CONFIG["max_boxes_num"],
        debug_mode=CONFIG["debug_mode"],
    )
    yolo.config_preprocess()
    return yolo


def process_frame(yolo: YOLOv8, pl: PipeLine, CONFIG: dict) -> tuple:
    """
    处理当前帧，返回检测结果和物体数量

    参数：
        yolo: YOLOv8模型实例
        pl: PipeLine管道实例
        CONFIG: 配置字典
    返回：
        检测结果列表，FPS值，当前帧图像
    """
    img = pl.get_frame()
    if img is None:
        logging("Unable to capture frame.")
        return []
    fps = 0
    clock = utime.clock()
    clock.tick()
    result = yolo.run(img)
    fps = clock.fps()
    # logging(f"YOLO run result: {result}", log_name=LOGNAME)  # 添加日志记录返回值

    # 解析结果
    if len(result) == 0:
        return [], fps, img  # 返回检测结果、FPS 和当前帧

    detections = []
    for item in result:
        detection = {
            "label": CONFIG["labels"][int(item[5])],
            "label_id": int(item[5]),
            "confidence": float(item[4]),
            "bbox": [float(item[0]), float(item[1]), float(item[2]), float(item[3])],
        }
        detections.append(detection)
    return detections, fps, img  # 返回检测结果、FPS 和当前帧


def calculate_cycle_result(cycle_data: list[int], frame_index: int) -> int:
    """
    统计周期内物体数量的众数

    参数：
        cycle_data: 历史检测结果数据，整数列表
        frame_index: 当前帧索引，整数
    返回：
        最常见的物体数量：int
    """
    if frame_index == 0:
        return 0
    return max(set(cycle_data[:frame_index]), key=cycle_data[:frame_index].count)
