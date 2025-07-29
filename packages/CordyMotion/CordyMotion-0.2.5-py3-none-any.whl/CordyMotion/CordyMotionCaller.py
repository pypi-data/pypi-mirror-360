import socket
import time
from tracemalloc import Statistic


class MotionCaller:
    def __init__(self, ip="127.0.0.1", port=8899, timeout=300000):
        """
        初始化 TCP 客户端
        :param ip: 服务器 IP 地址，默认为 127.0.0.1
        :param port: 服务器端口，默认为 8888
        :param timeout: 超时时间（毫秒），默认为 10000
        """
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def send_command(self, message):
        """
        发送 TCP 消息并接收响应
        :param message: 要发送的消息
        :return: 响应消息或错误信息
        """
        # 创建 socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            return f"|Result=FAIL|error=Socket creation error: {e}|"

        # 设置超时（将毫秒转换为秒）
        timeout_sec = self.timeout / 1000.0
        sock.settimeout(timeout_sec)

        # 连接服务器
        retry_connect_times = 3
        connected = False
        for i in range(retry_connect_times):
            try:
                sock.connect((self.ip, self.port))
                connected = True
                break
            except socket.error as e:
                print(f"Connect failed. Retry: {i + 1} times")
                time.sleep(1)  # 等待 1 秒后重试
        if not connected:
            sock.close()
            return f"|Result=FAIL|error=errno: {str(e)}|"

        # 发送消息
        try:
            sock.sendall(message.encode('utf-8'))
            print(f"Sent: {message}")
        except socket.error as e:
            sock.close()
            return f"|Result=FAIL|error=Send error: {e}|"

        # 接收响应
        response_message = ""
        try:
            buffer_size = 1024
            data = sock.recv(buffer_size)
            if data:
                response_message = data.decode('utf-8')
        except socket.error as e:
            response_message = f"|Result=FAIL|error=Receive error: {e}|"

        sock.close()
        return response_message

    @staticmethod
    def run_check():
        print("cordymotioncaller installed.")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="Server IP address")
    parser.add_argument("port", help="Server port", type=int)
    parser.add_argument("command", help="Command to send")
    parser.add_argument("timeout", help="Connection timeout(ms)")
    args = parser.parse_args()

    client = MotionCaller(args.ip, args.port, args.timeout)
    print(client.send_command(args.command))

if __name__ == "__main__":
    main()
