# import libs.ntptime as ntptime
import utime
from machine import RTC
from src.services.utils import logging

LOGNAME = "ntptime"


def sync_ntp(CONFIG):
    """同步 NTP 时间"""

    try:
        logging("Start syncing time with NTP...", log_name=LOGNAME)
        ret = utime.ntp_sync()  # 设置时间
        current_time = RTC().datetime()
        # 格式化时间为字符串 (YYYY-MM-DD HH:MM:SS)
        formatted_time = f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
        logging(f"Current time: {formatted_time}", log_name=LOGNAME)
        return ret
    except Exception as e:
        logging(f"Error syncing time with NTP: {e}", log_name=LOGNAME)
        return False
