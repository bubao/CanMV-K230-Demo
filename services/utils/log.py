import time
from machine import RTC

# 日志文件路径
log_path = "/sdcard/logs/"
boot_log = "boot.log"


# 写日志的函数
def write_log(message, log_name="log"):
    try:
        # current_time = time.localtime()  # 获取本地时间
        current_time = RTC().datetime()
        # 格式化时间为字符串 (YYYY-MM-DD HH:MM:SS)
        formatted_time = f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
        print(f"[{formatted_time}] {log_name}: {message}")

        # with open(log_path + boot_log, "a") as log_file:
        #     log_file.write(f"[{formatted_time}] {log_name}: {message}\n")
    except Exception as e:
        print(f"Error writing to log: {e}")
