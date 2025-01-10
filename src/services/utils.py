from machine import RTC
import json


# 写日志的函数
def logging(message, log_name="log"):
    try:
        current_time = RTC().datetime()
        # 格式化时间为字符串 (YYYY-MM-DD HH:MM:SS)
        print(f"[{format_time(current_time)}] {log_name}: {message}")
    except Exception as e:
        print(f"Error writing to log: {e}")


def format_time(current_time):
    return f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"


def load_config(config_path="/sdcard/.config.json"):
    """读取配置文件并返回配置字典"""
    try:
        with open(config_path) as f:
            return True, json.load(f)
    except Exception as e:
        logging(
            f"Error loading config from {config_path}: {e}", log_name="utils.config"
        )
        return False, None
