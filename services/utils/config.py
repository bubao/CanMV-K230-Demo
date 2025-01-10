import json
from services.utils.log import write_log


def load_config(config_path):
    """读取配置文件并返回配置字典"""
    try:
        with open(config_path) as f:
            return json.load(f)
    except Exception as e:
        write_log(f"Error loading config from {config_path}: {e}", log_name="config")
        return None
