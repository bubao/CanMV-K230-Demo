from libs.YOLO import YOLOv8
from libs.PipeLine import PipeLine, ScopedTiming
import time, os, sys
import ulab.numpy as np
import image
import time
import ujson
import gc
import utime

# from libs.Utils import *
from media.sensor import *
from media.display import *
from media.media import *

LOGNAME = "yolo"

sensor_id = 2
sensor = None

from services.utils.log import write_log
from services.mqtt import MQTTPublish
from services.utils.config import load_config


def run_yolo_and_publish_data():
    os.exitpoint(os.EXITPOINT_ENABLE)
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
        # mqtt_client = MQTTPublish(mqtt_config)
        # ret = mqtt_client.connect()
        # if ret is False:
        #     return

        kmodel_path = yolo_config["kmodel_path"]
        labels = yolo_config["labels"]
        rgb888p_size = yolo_config["rgb888p_size"]
        model_input_size = yolo_config["model_input_size"]
        # display_size = yolo_config["display_size"]
        conf_thresh = yolo_config["conf_thresh"]
        nms_thresh = yolo_config["nms_thresh"]
        max_boxes_num = yolo_config["max_boxes_num"]

        # # 初始化YOLOv8模型
        # yolo = YOLOv8(
        #     task_type="detect",
        #     mode="image",
        #     kmodel_path=kmodel_path,
        #     labels=labels,
        #     rgb888p_size=rgb888p_size,
        #     model_input_size=model_input_size,
        #     conf_thresh=conf_thresh,
        #     nms_thresh=nms_thresh,
        #     max_boxes_num=max_boxes_num,
        #     debug_mode=1,
        # )
        # yolo.config_preprocess()

        # topic_detection = mqtt_config["topic_detection"]
        # sensor = Sensor(id=sensor_id)
        # sensor.reset()
        # sensor.set_framesize(framesize=Sensor.B320X320, chn=CAM_CHN_ID_0)
        # sensor.set_pixformat(Sensor.RGB888, chn=CAM_CHN_ID_0)
        # # Display.init(Display.VIRT, width=1920, height=1080, to_ide=False)
        # # MediaManager.init()
        # sensor.run()
        # clock = utime.clock()
        # fps = 0
        # while True:
        #     os.exitpoint()
        #     # with ScopedTiming("total", 1):
        #     # img = sensor.snapshot(chn=CAM_CHN_ID_0)
        #     res = None
        #     # try:
        #     #     print(
        #     #         f"Captured image size: {img.width}x{img.height}, Format: {img.format}"
        #     #     )

        #     #     # 转换图像为 numpy 数组
        #     #     np_img = np.array(img)

        #     #     # 使用 ulab 的方法来调整大小（例如通过重采样）
        #     #     # 这将需要更多的计算资源，但可以提供更高的灵活性
        #     #     np_resized = np_img.resize((320, 320))  # 假设有 resize 方法支持

        #     #     # 将处理后的数组转换回图像对象
        #     #     img_resized = image.Image.from_bytes(np_resized)
        #     #     clock.tick()
        #     #     # res, score = yolo.run(img_resized)
        #     #     fps = clock.fps()
        #     # except Exception as e:
        #     #     write_log(f"Error during YOLO run: {e}", log_name=LOGNAME)
        #     #     continue

        #     # 处理推理结果，准备发送到 MQTT
        #     detection_data = []
        #     if not res:
        #         write_log(f"No detections in this frame.{fps}", log_name=LOGNAME)
        #     else:
        #         print("res")
        #         for item in res:
        #             obj = {
        #                 "label": item["label"],
        #                 "confidence": item["confidence"],
        #                 "bbox": item["bbox"],
        #                 "fps": float(fps),
        #                 "score": float(score),
        #             }
        #             detection_data.append(obj)

        #         # 上报数据到 MQTT
        #         str_data = ujson.dumps(detection_data)
        #         write_log(
        #             f"send topic {topic_detection} data: {str_data}",
        #             log_name=LOGNAME,
        #         )
        #         mqtt_client.publish(topic_detection, str_data)
        #         gc.collect()
    except KeyboardInterrupt as e:
        print("用户停止: ", e)
    except BaseException as e:
        print(f"异常: {e}")
    finally:
        # 停止传感器运行
        # if isinstance(sensor, Sensor):
        #     sensor.stop()
        #     sensor.deinit()
        # mqtt_client.disconnect()
        os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
        time.sleep_ms(100)
        # 释放媒体缓冲区
        write_log("yolo done", log_name=LOGNAME)
