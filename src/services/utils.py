from machine import RTC
import json


# 写日志的函数，支持自定义日志名称
def logging(message: str, log_name: str = "log"):
    try:
        current_time = RTC().datetime()
        # 格式化时间为字符串 (YYYY-MM-DD HH:MM:SS)
        print(f"[{format_time(current_time)}] {log_name}: {message}")
    except Exception as e:
        print(f"Error writing to log: {e}")


# 格式化时间函数，将RTC返回的时间元组格式化为字符串
def format_time(current_time) -> str:
    return f"{current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"


# 读取配置文件并返回配置字典
def load_config(config_path: str = "/sdcard/.config.json") -> tuple[bool, dict]:
    """读取配置文件并返回配置字典"""
    try:
        with open(config_path) as f:
            return True, json.load(f)
    except Exception as e:
        logging(
            f"Error loading config from {config_path}: {e}", log_name="utils.config"
        )
        return False, None


# 更新配置文件中的配置
def update_config(new_config: dict, config_path: str = "/sdcard/.config.json") -> bool:
    """更新配置文件中的配置"""
    success, config = load_config(config_path)
    if not success:
        return False

    # 更新配置
    config.update(new_config)

    # 保存更新后的配置
    return save_config(config, config_path)


# 获取WiFi网络配置列表
def get_wifi_network(config_path: str = "/sdcard/.config.json") -> list | bool:
    """获取WiFi网络配置"""
    success, config = load_config(config_path)
    if not success:
        return False

    return config["wifi"]["networks"]


# 新增WiFi网络配置
def add_wifi_network(
    ssid: str, password: str, config_path: str = "/sdcard/.config.json"
) -> bool:
    """新增WiFi网络配置"""
    success, config = load_config(config_path)
    if not success:
        return False

    new_network = {"enabled": True, "ssid": ssid, "password": password}
    config["wifi"]["networks"].append(new_network)

    return save_config(config, config_path)


# 删除WiFi网络配置
def remove_wifi_network(ssid: str, config_path: str = "/sdcard/.config.json") -> bool:
    """删除WiFi网络配置"""
    success, config = load_config(config_path)
    if not success:
        return False

    config["wifi"]["networks"] = [
        net for net in config["wifi"]["networks"] if net["ssid"] != ssid
    ]

    return save_config(config, config_path)


# 修改WiFi网络配置
def modify_wifi_network(
    ssid: str,
    new_password: str | None = None,
    enabled: bool = True,
    config_path: str = "/sdcard/.config.json",
) -> bool:
    """修改WiFi网络配置"""
    try:
        success, config = load_config(config_path)
        if not success:
            return False

        is_modify = False
        for net in config["wifi"]["networks"]:
            if net["ssid"] == ssid:
                if new_password:
                    net["password"] = new_password
                net["enabled"] = enabled
                is_modify = True
                break

        # 如果没有修改现有网络配置，则添加新的网络
        if not is_modify:
            new_network = {"enabled": enabled, "ssid": ssid, "password": new_password}
            config["wifi"]["networks"].append(new_network)

        # 保存修改后的配置
        return save_config(config, config_path)
    except Exception as e:
        logging.error(f"Error modify_wifi_network : {e}")
        return False


# 保存配置字典到配置文件
def save_config(config: dict, config_path: str = "/sdcard/.config.json") -> bool:
    """保存配置字典到配置文件"""
    try:
        with open(config_path, "w") as f:
            json.dump(config, f)  # 格式化输出，便于调试
        logging.info(f"Config saved to {config_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving config to {config_path}: {e}")
        return False
