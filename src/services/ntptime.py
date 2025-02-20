# import libs.ntptime as ntptime
import utime
from machine import RTC
from src.services.utils import logging

LOGNAME = "ntptime"


def sync_ntp() -> bool:
    """同步 NTP 时间"""

    try:
        # 记录开始同步时间日志
        logging("Start syncing time with NTP...", log_name=LOGNAME)
        # 调用NTP同步函数并获取返回状态码
        ret = utime.ntp_sync()  # 设置时间，返回状态码
        # 获取当前RTC时间，并转换为元组格式 (year, month, day, hour, minute, second, weekday, leap_year_flag)
        current_time = RTC().datetime()
        # 格式化时间为字符串 (YYYY-MM-DD HH:MM:SS)
        formatted_time = f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
        # 记录当前时间日志
        logging(f"Current time: {formatted_time}", log_name=LOGNAME)
        return ret  # 返回NTP同步状态码
    except Exception as e:
        # 记录同步时间错误日志并返回False表示失败
        logging(f"Error syncing time with NTP: {e}", log_name=LOGNAME)
        return False
