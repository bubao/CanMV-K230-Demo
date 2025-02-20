import network
import time
import ujson
from src.services.utils import logging, load_config


LOGNAME = "wifi"


# WiFi 连接测试函数
def connect_wifi(ssid: str, password: str) -> tuple[bool, str]:
    """连接到指定的WiFi网络
    参数:
        ssid: 需要连接的WiFissid字符串
        password: 对应的wifi密码字符串
    返回值:
        (success: bool, ip_address: str)
        success为True表示连接成功，ip_address是获取到的IP地址
        如果连接失败，返回(False, "0.0.0.0")
    """
    sta = network.WLAN(network.STA_IF)  # 创建 WLAN 对象
    ip_address = None
    if not sta.active():
        sta.active(True)  # 激活 WLAN
        logging("WiFi STA mode activated.", log_name=LOGNAME)

    logging(f"WiFi active: {sta.active()}", log_name=LOGNAME)  # 查看 sta 是否激活
    logging(f"WiFi status: {sta.status()}", log_name=LOGNAME)  # 查看 sta 状态

    # 尝试连接 WiFi
    logging(f"Attempting to connect to WiFi: {ssid}", log_name=LOGNAME)
    sta.connect(ssid, password)

    # 等待连接并检查连接状态
    timeout = 10  # 设置超时时间（秒）
    while not sta.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        logging(f"Waiting for connection... {timeout}s left", log_name=LOGNAME)

    # 如果连接成功，等待获取 IP 地址
    if sta.isconnected():
        ip_address = sta.ifconfig()[0]
        logging(f"Connected to {ssid}", log_name=LOGNAME)
        logging(f"IP Address: {ip_address}", log_name=LOGNAME)

        # 如果 IP 地址仍然是 0.0.0.0，继续等待
        retries = 5  # 最大重试次数
        while ip_address == "0.0.0.0" and retries > 0:
            time.sleep(1)
            ip_address = sta.ifconfig()[0]
            retries -= 1
            logging(f"Retrying to get IP... Attempt {5 - retries}", log_name=LOGNAME)

        if ip_address != "0.0.0.0":
            logging(f"Successfully obtained IP Address: {ip_address}", log_name=LOGNAME)
            return True, ip_address
        else:
            logging(
                f"Failed to obtain valid IP Address after retries.", log_name=LOGNAME
            )
            return False, ip_address
    else:
        logging(f"Failed to connect to {ssid}", log_name=LOGNAME)
        return False, ip_address


# 读取配置并循环尝试连接
def test_wifi_connections(wifi_configs: dict) -> bool:
    """测试可用的WiFi连接，按顺序尝试连接
    参数:
        wifi_configs: 包含多个WiFi配置的字典列表
    返回值:
        bool: 连接成功返回True，否则False
    """
    if wifi_configs:
        for config in wifi_configs.get("networks", []):
            ssid = config.get("ssid")
            password = config.get("password")
            enabled = config.get("enabled", False)
            if enabled == False or not ssid or not password:
                # logging("SSID or password missing in configuration.", log_name=LOGNAME)
                continue  # 跳过无效的配置

            logging(f"Attempting to connect to WiFi: {ssid}", log_name=LOGNAME)
            success, ip_address = connect_wifi(ssid, password)
            if success:
                logging(
                    f"Successfully connected to {ssid}, ip is {ip_address}",
                    log_name=LOGNAME,
                )
                return True  # 成功连接后停止尝试
        else:
            logging("All WiFi connections failed.", log_name=LOGNAME)
            return False
    else:
        logging("No WiFi configurations enabled.", log_name=LOGNAME)
        return False
