import network
import time
from services.utils.log import write_log

LOGNAME = "wifi"


# 读取 WiFi 配置
def load_wifi_config():
    try:
        with open("/sdcard/config/wifi_config.csv", "r") as f:
            lines = f.readlines()
            headers = lines[0].strip().split(",")  # 获取标题行
            wifi_configs = []

            # 遍历文件中的每一行，获取启用的 WiFi 配置
            for line in lines[1:]:
                values = line.strip().split(",")
                config = dict(zip(headers, values))

                # 只处理 enabled 为 1 的配置
                if config.get("enabled") == "1":
                    wifi_configs.append(config)

            if not wifi_configs:
                write_log("No enabled Wi-Fi configurations found.", log_name=LOGNAME)
            return wifi_configs
    except OSError as e:
        write_log(f"Error reading CSV file: {e}", log_name=LOGNAME)
        return None


# WiFi 连接测试函数
def connect_wifi(ssid, password):
    sta = network.WLAN(network.STA_IF)  # 创建 WLAN 对象
    if not sta.active():
        sta.active(True)  # 激活 WLAN
        write_log("WiFi STA mode activated.", log_name=LOGNAME)

    write_log(f"WiFi active: {sta.active()}", log_name=LOGNAME)  # 查看 sta 是否激活
    write_log(f"WiFi status: {sta.status()}", log_name=LOGNAME)  # 查看 sta 状态

    # 尝试连接 WiFi
    write_log(f"Attempting to connect to WiFi: {ssid}", log_name=LOGNAME)
    sta.connect(ssid, password)

    # 等待连接并检查连接状态
    timeout = 10  # 设置超时时间（秒）
    while not sta.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        write_log(f"Waiting for connection... {timeout}s left", log_name=LOGNAME)

    # 如果连接成功，等待获取 IP 地址
    if sta.isconnected():
        ip_address = sta.ifconfig()[0]
        write_log(f"Connected to {ssid}", log_name=LOGNAME)
        write_log(f"IP Address: {ip_address}", log_name=LOGNAME)

        # 如果 IP 地址仍然是 0.0.0.0，继续等待
        retries = 5  # 最大重试次数
        while ip_address == "0.0.0.0" and retries > 0:
            time.sleep(1)
            ip_address = sta.ifconfig()[0]
            retries -= 1
            write_log(f"Retrying to get IP... Attempt {5 - retries}", log_name=LOGNAME)

        if ip_address != "0.0.0.0":
            write_log(
                f"Successfully obtained IP Address: {ip_address}", log_name=LOGNAME
            )
            return True
        else:
            write_log(
                f"Failed to obtain valid IP Address after retries.", log_name=LOGNAME
            )
            return False
    else:
        write_log(f"Failed to connect to {ssid}", log_name=LOGNAME)
        return False


# 读取配置并循环尝试连接
def sta_test():
    wifi_configs = load_wifi_config()
    if wifi_configs:
        for config in wifi_configs:
            ssid = config.get("ssid")
            password = config.get("password")
            if not ssid or not password:
                write_log(
                    "SSID or password missing in configuration.", log_name=LOGNAME
                )
                continue  # 跳过无效的配置

            write_log(f"Attempting to connect to WiFi: {ssid}", log_name=LOGNAME)
            if connect_wifi(ssid, password):
                write_log(f"Successfully connected to {ssid}", log_name=LOGNAME)
                return True  # 成功连接后停止尝试
        else:
            write_log("All WiFi connections failed.", log_name=LOGNAME)
    else:
        write_log("No WiFi configurations enabled.", log_name=LOGNAME)
