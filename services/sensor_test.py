# main.py -- put your code here!
import time, os, sys

import utime
from media.sensor import *
from media.display import *
from media.media import *

# 用CSI0接口的摄像头
sensor_id = 2
sensor = None

try:
    # 构造一个具有默认配置的摄像头对象
    sensor = Sensor(id=sensor_id)
    # 重置摄像头sensor
    sensor.reset()

    # 无需进行镜像翻转
    # 设置水平镜像
    # sensor.set_hmirror(False)
    # 设置垂直翻转
    # sensor.set_vflip(False)

    # 设置通道0的输出尺寸为1920x1080
    sensor.set_framesize(Sensor.FHD, chn=CAM_CHN_ID_0)
    # 设置通道0的输出像素格式为RGB888
    sensor.set_pixformat(Sensor.RGB888, chn=CAM_CHN_ID_0)

    # 使用IDE的帧缓冲区作为显示输出
    Display.init(Display.VIRT, width=1920, height=1080, to_ide=True)
    # 初始化媒体管理器
    MediaManager.init()
    # 启动传感器
    sensor.run()

    # 构造clock
    clock = utime.clock()

    while True:
        os.exitpoint()

        # 更新当前时间（毫秒）
        clock.tick()

        # 捕获通道0的图像
        img = sensor.snapshot(chn=CAM_CHN_ID_0)
        # 显示捕获的图像
        Display.show_image(img)

        # 打印当前fps
        print("fps = ", clock.fps())

except KeyboardInterrupt as e:
    print("用户停止: ", e)
except BaseException as e:
    print(f"异常: {e}")
finally:
    # 停止传感器运行
    if isinstance(sensor, Sensor):
        sensor.stop()
    # 反初始化显示模块
    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    # 释放媒体缓冲区
    MediaManager.deinit()
