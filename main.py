import os
import time
import utime
import gc
import ujson
import machine
import uasyncio as asyncio
from src.services.utils import logging, load_config, update_config
from src.services.wifi import test_wifi_connections
from src.services.ntptime import sync_ntp
from src.services.mqtt import MQTTPublish
from src.services.ap import WiFiAP
from src.services.yolo import initialize_pipeline, initialize_yolo, process_frame

LOGNAME = "main"


async def main_task():
    """
    主函数初始化并运行带有MQTT通信的YOLO模型。

    此函数执行以下步骤：
    1. 加载配置。
    2. 检查所需的配置（WiFi、YOLO、MQTT）是否存在并启用。
    3. 测试WiFi连接。
    4. 如果启用了NTP时间同步，则同步时间。
    5. 初始化MQTT客户端并连接到MQTT代理。
    6. 初始化YOLO模型和处理管道。
    7. 每秒处理帧，进行目标检测，并将结果发送到MQTT代理。
    8. 处理异常并确保资源的正确清理。

    返回:
        None
    """
    # 获取配置
    success, config = load_config()
    if not success:
        logging("Failed to load config, exiting...", log_name=LOGNAME)
        return

    wifi_config = config.get("wifi", {})
    yolo_config = config.get("yolo", {})
    mqtt_config = config.get("mqtt", {})
    ntptime_config = config.get("ntptime", {})

    # 检查配置项是否存在并启用
    if not yolo_config:
        logging("YOLO config missing, exiting...", log_name=LOGNAME)
        return

    if wifi_config.get("enabled", False):
        try:
            # 测试WiFi连接
            if test_wifi_connections(wifi_config):
                logging("WiFi connection successful", log_name=LOGNAME)

                # 同步NTP时间
                if ntptime_config.get("enabled", False):
                    sync_ntp()
                    logging("NTP time synced", log_name=LOGNAME)

                # 初始化MQTT客户端
                mqtt_client = None
                if mqtt_config.get("enabled", False):
                    mqtt_client = MQTTPublish(mqtt_config)
                    ret = mqtt_client.connect()
                    if ret is False:
                        logging("Failed to connect to MQTT broker", log_name=LOGNAME)
                        mqtt_client = None
                    else:
                        topic_detection = mqtt_config.get("topic_detection", "")
                        mqtt_client_id = mqtt_config.get("client_id", "")

                # 初始化YOLO模型和处理管道
                pl = initialize_pipeline(yolo_config)
                yolo = initialize_yolo(yolo_config)

                last_time = utime.ticks_ms()
                while True:
                    await asyncio.sleep_ms(100)  # 允许事件循环运行
                    current_time = utime.ticks_ms()
                    if (
                        utime.ticks_diff(current_time, last_time) >= 1000
                    ):  # 每秒处理一帧
                        last_time = current_time
                        res, fps, frame = process_frame(
                            yolo, pl, yolo_config
                        )  # 获取当前帧

                        # 处理推理结果，准备发送到MQTT
                        detection_data = []
                        if res and len(res) > 0:
                            for item in res:
                                obj = {
                                    "label": item.get("label", ""),
                                    "confidence": item.get("confidence", 0.0),
                                    "bbox": item.get("bbox", []),
                                    "fps": float(fps),
                                }
                                detection_data.append(obj)
                            logging(
                                f"Detection data: {detection_data}", log_name=LOGNAME
                            )

                            if mqtt_client and mqtt_client.is_connected():
                                # 发送检测数据到MQTT
                                str_data = ujson.dumps(
                                    {
                                        "data": detection_data,
                                        "client_id": mqtt_client_id,
                                    }
                                )
                                topic = f"{topic_detection}/{mqtt_client_id}"
                                logging(
                                    f"Sending topic {topic} data: {str_data}",
                                    log_name=LOGNAME,
                                )
                                mqtt_client.publish(topic, str_data)
                            else:
                                logging("MQTT client not connected", log_name=LOGNAME)

                    # 定期收集垃圾
                    gc.collect()

        except KeyboardInterrupt as e:
            print("用户停止: ", e)
        except BaseException as e:
            print(f"异常: {e}")
        finally:
            if mqtt_client:
                mqtt_client.disconnect()  # 断开MQTT连接
                logging("MQTT client disconnected", log_name=LOGNAME)
            yolo.deinit()  # 销毁YOLO模型
            pl.destroy()  # 销毁显示管道
            logging("YOLO model and pipeline destroyed", log_name=LOGNAME)
            os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)  # 使能休眠
            time.sleep_ms(100)
            logging("yolo done", log_name=LOGNAME)
            return  # 添加缺少的 return 语句

    else:
        try:
            logging(
                "No WiFi configurations enabled. Starting AP mode...", log_name=LOGNAME
            )
            ap = WiFiAP()
            asyncio.run(ap.start())
            asyncio.run(ap.start_server())

            # 创建一个无限循环任务以保持事件循环运行
            async def keep_alive():
                while True:
                    await asyncio.sleep_ms(1000)  # 每秒运行一次

            keep_alive_task = asyncio.create_task(keep_alive())

            # 等待任务完成（理论上不会完成）
            await keep_alive_task
        except KeyboardInterrupt as e:
            print("用户停止: ", e)
        except BaseException as e:
            print(f"异常: {e}")
        finally:
            if ap:
                ap.stop()
                logging("AP mode stopped", log_name=LOGNAME)


async def run_main():
    await main_task()


if __name__ == "__main__":
    asyncio.run(run_main())
