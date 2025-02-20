import socket
import uasyncio as asyncio


class DNSServer:
    def __init__(self, host_ip: str, domain: str = "ap.net"):
        """初始化DNS服务器

        Args:
            host_ip: 要映射的主机IP地址字符串
            domain: 要处理的自定义域名，默认为"ap.net"
        """
        self.host_ip = host_ip
        self.domain = domain

    async def start(self) -> asyncio.Future:
        """启动DNS服务器，监听和处理DNS请求

        Returns:
            asyncio.Future 对象，用于异步操作管理
        """
        addr = socket.getaddrinfo("0.0.0.0", 53)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(addr)
        print("DNS server listening on", addr)

        while True:
            try:
                data = self._recvfrom_nonblocking(s)
                if data:
                    addr = data[1]
                    data = data[0]
                    print(f"Received data: {data}")  # 打印接收到的数据进行调试

                    # 解析DNS请求
                    domain = data[12 : data.find(b"\x00", 12)].decode("utf-8")
                    print("DNS request for:", domain)
                    if domain == self.domain:
                        # 构建DNS响应
                        response = (
                            data[:2]
                            + b"\x81\x80"
                            + data[4:6]
                            + b"\x00\x01\x00\x00\x00\x00"
                            + data[12 : data.find(b"\x00", 12) + 5]
                            + b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04"
                            + socket.inet_aton(self.host_ip)
                        )
                        s.sendto(response, addr)
            except Exception as e:
                print(f"Error handling DNS request: {e}")
                await asyncio.sleep(1)

    def _recvfrom_nonblocking(self, sock, buffer_size: int = 512) -> tuple | None:
        """非阻塞方式接收数据包

        Args:
            sock: 要监听的socket对象
            buffer_size: 接收缓冲区大小，默认512字节

        Returns:
            成功接收返回(data, addr)元组，失败或无数据返回None
        """
        try:
            # 设置 socket 为非阻塞模式
            sock.setblocking(False)
            data = sock.recvfrom(buffer_size)
            return data
        except OSError:
            # 如果没有数据接收到，返回 None
            return None


# Example usage:
# dns_server = DNSServer("192.168.4.1")
# asyncio.run(dns_server.start())
