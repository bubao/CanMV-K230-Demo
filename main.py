from src.services.utils import logging, load_config
from src.services.wifi import test_wifi_connections
from src.services.ntptime import sync_ntp
from src.services.mqtt import MQTTPublish
import os, time, utime, gc, ujson
from src.yolo import initialize_pipeline, initialize_yolo, process_frame

LOGNAME = "main"


# 主函数
# 1. 获取配置，根据配置选择初始化wifi连接，
# 2. 只有wifi连接成功才能同步时间，
# 3. 只有wifi连接成功才能初始化mqtt连接
# 4. 运行yolo模型
# 5. 第二步是否失败不影响执行，但是wifi和mqtt连接失败会导致yolo模型无法运行
def main():
    # 获取配置
    success, config = load_config()
    if not success:
        logging("Failed to load config, exiting...", log_name=LOGNAME)
        return
    wifi_config = config.get("wifi", None)
    yolo_config = config.get("yolo", None)
    mqtt_config = config.get("mqtt", None)
    ntptime_config = config.get("ntptime", None)
    if (
        not wifi_config
        or not yolo_config
        or not mqtt_config
        or wifi_config.get("enabled", False) == False
        or mqtt_config.get("enabled", False) == False
    ):
        logging("Config missing required fields, exiting...", log_name=LOGNAME)
        return
    if test_wifi_connections(wifi_config):
        # 联网成功
        if ntptime_config and ntptime_config.get("enabled", False):
            sync_ntp(ntptime_config)

        # 初始化 MQTT 连接并运行 YOLO 模型
        try:
            # 初始化MQTT客户端
            mqtt_client = MQTTPublish(mqtt_config)
            ret = mqtt_client.connect()
            if ret is False:
                return
            topic_detection = mqtt_config["topic_detection"]
            pl = initialize_pipeline(yolo_config)
            yolo = initialize_yolo(yolo_config)

            last_time = utime.time()
            while True:
                os.exitpoint()
                current_time = utime.time()
                if current_time - last_time >= 1:  # 每秒处理一帧
                    last_time = current_time
                    res, fps = process_frame(yolo, pl, yolo_config)

                    # 处理推理结果，准备发送到 MQTT
                    detection_data = []
                    if not res or len(res) == 0:
                        pass
                    else:
                        for item in res:
                            obj = {
                                "label": item["label"],
                                "confidence": item["confidence"],
                                "bbox": item["bbox"],
                                "fps": float(fps),
                            }
                            detection_data.append(obj)

                        # 上报数据到 MQTT
                        str_data = ujson.dumps(detection_data)
                        logging(
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
            logging("yolo done", log_name=LOGNAME)

    else:
        logging("No WiFi configurations enabled.", log_name=LOGNAME)
        return False


main()
