from libs.YOLO import YOLOv8
from libs.PipeLine import PipeLine
import time, os
import time
import ujson
import gc
import utime

from media.sensor import *
from media.display import *
from media.media import *

LOGNAME = "yolo"

sensor_id = 2
sensor = None

from services.utils.log import write_log
from services.mqtt import MQTTPublish
from services.utils.config import load_config


def initialize_pipeline(CONFIG):
    """初始化显示管道"""
    pl = PipeLine(
        rgb888p_size=CONFIG["rgb888p_size"],
        display_size=CONFIG["display_size"],
        display_mode=CONFIG["display_mode"],
    )
    pl.create()
    return pl


def initialize_yolo(CONFIG):
    """初始化 YOLO 模型"""
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


def process_frame(yolo, pl, CONFIG):
    """处理当前帧，返回检测结果和物体数量"""
    img = pl.get_frame()
    if img is None:
        write_log("Unable to capture frame.")
        return [], 0
    result = yolo.run(img)
    write_log(f"YOLO run result: {result}", log_name=LOGNAME)  # 添加日志记录返回值

    # 解析结果
    if len(result) == 0:
        return [], 0

    detections = []
    for item in result:
        detection = {
            "label": CONFIG["labels"][int(item[5])],
            "label_id": int(item[5]),
            "confidence": float(item[4]),
            "bbox": [float(item[0]), float(item[1]), float(item[2]), float(item[3])],
        }
        detections.append(detection)
    score = (
        sum([d["confidence"] for d in detections]) / len(detections)
        if detections
        else 0
    )
    return detections, score


def calculate_cycle_result(cycle_data, frame_index):
    """统计周期内物体数量的众数"""
    if frame_index == 0:
        return 0
    return max(set(cycle_data[:frame_index]), key=cycle_data[:frame_index].count)


def run_yolo_and_publish_data():
    try:
        # 加载配置文件
        yolo_config = load_config("/sdcard/config/yolo.json")
        mqtt_config = load_config("/sdcard/config/mqtt_config.json")
        write_log("yolo running", log_name=LOGNAME)

        if not yolo_config or not mqtt_config:
            write_log(
                "Error loading YOLO or MQTT configuration. Exiting.", log_name=LOGNAME
            )
            return

        # 初始化MQTT客户端
        mqtt_client = MQTTPublish(mqtt_config)
        ret = mqtt_client.connect()
        if ret is False:
            return

        topic_detection = mqtt_config["topic_detection"]

        pl = initialize_pipeline(yolo_config)

        yolo = initialize_yolo(yolo_config)

        clock = utime.clock()
        fps = 0
        last_time = utime.time()
        while True:
            os.exitpoint()
            current_time = utime.time()
            if current_time - last_time >= 1:  # 每秒处理一帧
                last_time = current_time
                clock.tick()
                res, score = process_frame(yolo, pl, yolo_config)
                fps = clock.fps()

                # 处理推理结果，准备发送到 MQTT
                detection_data = []
                if not res or len(res) == 0:
                    # write_log(f"No detections in this frame.{fps}", log_name=LOGNAME)
                    pass
                else:
                    for item in res:
                        obj = {
                            "label": item["label"],
                            "confidence": item["confidence"],
                            "bbox": item["bbox"],
                            "fps": float(fps),
                            "score": float(score),
                        }
                        detection_data.append(obj)

                    # 上报数据到 MQTT
                    str_data = ujson.dumps(detection_data)
                    write_log(
                        f"send topic {topic_detection} data: {str_data}",
                        log_name=LOGNAME,
                    )
                    mqtt_client.publish(topic_detection, str_data)
                    gc.collect()
    except KeyboardInterrupt as e:
        print("用户停止: ", e)
    except BaseException as e:
        print(f"异常: {e}")
    finally:
        mqtt_client.disconnect()  # 断开MQTT连接
        yolo.deinit()  # 销毁YOLO模型
        pl.destroy()  # 销毁显示管道
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)  # 使能休眠
        time.sleep_ms(100)
        # 释放媒体缓冲区
        write_log("yolo done", log_name=LOGNAME)
