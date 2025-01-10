from services.utils.log import write_log
from services.wifi import sta_test
from services.yolo import run_yolo_and_publish_data
import libs.ntptime as ntptime
from machine import RTC

LOGNAME = "main"


def boot_sequence():
    """执行启动流程"""

    try:
        # Wi-Fi 连接测试
        if sta_test():
            write_log("WiFi connection test completed.", log_name=LOGNAME)
            return True
        else:
            write_log("WiFi connection failed.", log_name=LOGNAME)
            return False
    except Exception as e:
        write_log(f"WiFi connection test failed: {e}", log_name=LOGNAME)
        return False


def sync_ntp():
    """同步 NTP 时间"""

    ntptime.NTP_DELTA = 3155644800  # 可选 UTC+8偏移时间（秒）
    ntptime.host = "ntp6.aliyun.com"  # 可选，ntp服务器

    try:
        write_log("Start syncing time with NTP...", log_name=LOGNAME)
        ntptime.settime()  # 设置时间
        current_time = RTC().datetime()
        # 格式化时间为字符串 (YYYY-MM-DD HH:MM:SS)
        formatted_time = f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
        write_log(f"Current time: {formatted_time}", log_name=LOGNAME)
    except Exception as e:
        write_log(f"Error syncing time with NTP: {e}", log_name=LOGNAME)
        return False

    return True


# 执行启动流程
if boot_sequence():
    write_log("Wi-Fi connected successfully.", log_name="main")

    if sync_ntp():
        write_log("Time synchronized successfully.", log_name="main")
        run_yolo_and_publish_data()  # 运行 YOLO 检测并发布数据
    else:
        write_log("Failed to synchronize time. YOLO will not run.", log_name="main")
    run_yolo_and_publish_data()  # 运行 YOLO 检测并发布数据

else:
    write_log("Wi-Fi connection failed. Boot process halted.", log_name="main")
