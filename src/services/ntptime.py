import libs.ntptime as ntptime
from machine import RTC
from src.services.utils import logging

LOGNAME = "ntptime"


def sync_ntp(CONFIG):
    """同步 NTP 时间"""
    ntptime.NTP_DELTA = CONFIG["ntp_delta"]  # 可选 UTC+8偏移时间（秒）
    ntptime.host = CONFIG["host"]  # 可选，ntp服务器

    try:
        logging("Start syncing time with NTP...", log_name=LOGNAME)
        ntptime.settime()  # 设置时间
        current_time = RTC().datetime()
        # 格式化时间为字符串 (YYYY-MM-DD HH:MM:SS)
        formatted_time = f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
        logging(f"Current time: {formatted_time}", log_name=LOGNAME)
        return True
    except Exception as e:
        logging(f"Error syncing time with NTP: {e}", log_name=LOGNAME)
        return False
