import network
import socket
import urandom
import uasyncio as asyncio
import machine
import json

# from .dns import DNSServer
from .utils import (
    update_config,
    add_wifi_network,
    remove_wifi_network,
    modify_wifi_network,
    get_wifi_network,
)


class WiFiAP:
    def __init__(self, ssid=None, password=None):

        self.sta = network.WLAN(network.STA_IF)
        # 初始化WiFi AP类，设置SSID和密码
        existing_ssids = self.scan_networks()
        if ssid is None:
            while True:
                ssid = "AP_" + "".join(
                    urandom.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                    for _ in range(6)
                )
                if ssid not in existing_ssids:
                    break
        if password is None:
            password = "12345678"
        # self.ssid = ssid
        self.ssid = "test"
        self.password = password
        self.existing_ssids = existing_ssids
        self.sta.active(False)
        self.ap = network.WLAN(network.AP_IF)

    def scan_networks(self):
        # 忽略设置活动状态的步骤
        try:
            self.sta.active(True)
        except AttributeError:
            print("网络堆栈不支持设置活动状态，跳过。")

        # 扫描 WiFi 网络
        try:
            networks = self.sta.scan()
        except Exception as e:
            print("扫描失败:", str(e))
            return []

        # 解析扫描结果
        ssids = []
        for net in networks:
            if hasattr(net, "ssid"):  # 确保每项是字典
                ssid = (
                    getattr(net, "ssid", b"").decode("utf-8")
                    if isinstance(getattr(net, "ssid", b""), bytes)
                    else getattr(net, "ssid", "")
                )
                if ssid:  # 确保 SSID 不为空
                    ssids.append(ssid)
                else:
                    print("跳过隐藏或无效网络:", net)
            else:
                print("扫描结果格式不符:", net)

        return ssids

    async def start(self):
        # 启动AP模式并配置SSID和密码
        try:
            self.sta.active(True)
        except AttributeError as e:
            print("网络堆栈不支持设置活动状态，跳过。异常详情:", str(e))
        except Exception as e:
            print("未知错误:", str(e))

        if self.password:
            self.ap.config(ssid=self.ssid, key=self.password)
        else:
            self.ap.config(ssid=self.ssid)

        while not self.ap.active():
            await asyncio.sleep(1)  # 异步等待AP启动

        print("AP started with SSID:", self.ssid)

        # 设置固定的IP地址
        # self.ap.ifconfig(("192.168.4.1", "255.255.255.0", "192.168.4.1", "8.8.8.8"))
        print("AP IP address:", self.ap.ifconfig()[0])

        # 启动DNS服务器
        # self.dns_server = DNSServer("192.168.4.1")
        # await asyncio.create_task(self.dns_server.start())  # 异步启动DNS服务器

    def stop(self):
        # 停止AP模式
        self.ap.active(False)
        print("AP stopped")

    def handle_client(self, conn):
        # 处理客户端请求
        request = conn.read()

        if request is None:
            return
        print("Request:", request)

        if "GET /api/scanned_networks" in request:
            # 获取扫描到的 WiFi 配置信息
            wifi_config = self.existing_ssids
            response = (
                "HTTP/1.1 200 OK\nContent-Type: application/json\n\n"
                + json.dumps(wifi_config)
            )
            conn.write(response)
            conn.close()
            return

        if "GET /api/config_file_networks" in request:
            # 获取配置文件中的 WiFi 配置信息
            config_file_networks = get_wifi_network()
            response = (
                "HTTP/1.1 200 OK\nContent-Type: application/json\n\n"
                + json.dumps(config_file_networks)
            )
            conn.write(response)
            conn.close()
            return

        # 处理 POST 请求 /api/add_update
        if "POST /api/add_update" in request:
            # 提取请求体部分
            body_start = request.find(b"\r\n\r\n") + 4  # 定位到请求体的开始
            body = request[body_start:]  # 获取请求体内容
            print("Request body:", body)

            try:
                # 解析 JSON 请求体
                data = json.loads(body)
                ssid = data.get("ssid")
                password = data.get("password")
                enabled = data.get("enabled")

                print("Received SSID:", ssid)
                print("Received Password:", password)
                print("Enabled:", enabled)

                # 添加或更新 WiFi 配置
                modify_wifi_network(ssid=ssid, new_password=password, enabled=enabled)

                # 返回响应
                response = "HTTP/1.1 200 OK\n\nWiFi 配置已添加或修改!"
                conn.write(response.encode())  # 发送字节响应
                conn.close()
                return

            except Exception as e:
                # JSON 解析失败时返回错误
                print(e)
                response = "HTTP/1.1 400 Bad Request\n\nInvalid JSON format!"
                conn.write(response.encode())  # 发送字节响应
                conn.close()
                return

        if "DELETE /api/delete" in request:
            # 提取请求体部分
            body_start = request.find(b"\r\n\r\n") + 4  # 定位到请求体的开始
            body = request[body_start:]  # 获取请求体内容
            print("Request body:", body)

            try:
                # 解析 JSON 请求体
                data = json.loads(body)
                ssid = data.get("ssid")

                if ssid:
                    print("Received SSID to remove:", ssid)

                    # 删除WiFi网络配置
                    remove_wifi_network(ssid)

                    # 返回响应
                    response = "HTTP/1.1 200 OK\n\nWiFi 配置已删除!"
                    conn.write(response.encode())  # 发送字节响应
                else:
                    # 如果没有提供 SSID，返回错误响应
                    response = "HTTP/1.1 400 Bad Request\n\nSSID is required!"
                    conn.write(response.encode())  # 发送字节响应

                conn.close()
                return

            except Exception as e:
                # JSON 解析失败时返回错误
                response = "HTTP/1.1 400 Bad Request\n\nInvalid JSON format!"
                conn.write(response.encode())  # 发送字节响应
                conn.close()
                return

        if "POST /reset" in request:
            print("Received reset request")
            response = "HTTP/1.1 200 OK\n\nSystem will reset!"
            conn.write(response)
            conn.close()
            machine.reset()  # 重置系统
            return

        # 读取 /sdcard/src/static/index.html 文件并返回
        try:
            with open("/sdcard/src/static/index.html", "r") as html_file:
                html_content = html_file.read()
            response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + html_content
        except Exception as e:
            response = f"HTTP/1.1 500 Internal Server Error\n\nFailed to read HTML file: {str(e)}"

        conn.write(response)
        conn.close()

    def start_server(self, micropython_optimize=True):
        s = socket.socket()
        ai = socket.getaddrinfo("0.0.0.0", 80)
        addr = ai[0][-1]
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)
        print("Listening on", addr)

        while True:
            try:
                print("xxx aaa")
                res = s.accept()
                client_sock = res[0]
                client_addr = res[1]
                client_sock.setblocking(True)  # 设置非阻塞模式
                client_sock.settimeout(1)
                print("Client connected from", client_addr)

                client_stream = (
                    client_sock if micropython_optimize else client_sock.makefile("rwb")
                )
                self.handle_client(client_stream)
            except OSError as e:
                print("Error accepting connection:", e)
            except Exception as e:
                print("Client:", str(e))


# Example usage:
# ap = WiFiAP('MyAP', 'password123')
# ap.start()
# asyncio.run(ap.start_server())
