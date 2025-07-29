import socket
import random


def is_port_available(port: int) -> bool:
    """
    检查本地端口是否可用

    参数:
        port (int): 要检查的端口号

    返回:
        bool: 如果端口可用返回True，否则返回False
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 设置套接字选项，允许地址重用
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 尝试绑定端口
            s.bind(('localhost', port))
            # 尝试监听端口
            s.listen(1)
        return True
    except OSError:
        return False


def get_random_available_port(min_port: int = 1024, max_port: int = 65535, max_attempts: int = 10) -> int:
    """
    生成随机可用端口

    参数:
        min_port (int): 最小端口号 (默认: 1024)
        max_port (int): 最大端口号 (默认: 65535)
        max_attempts (int): 最大尝试次数 (默认: 100)

    返回:
        int: 可用的随机端口号，如果没有找到则返回0
    """
    if min_port < 0 or max_port > 65535 or min_port > max_port:
        raise ValueError("端口号范围无效")

    for _ in range(max_attempts):
        # 生成随机端口号
        port = random.randint(min_port, max_port)
        # 检查端口是否可用
        if is_port_available(port):
            return port

    return 0  # 返回0表示未能找到可用端口


# 示例使用
if __name__ == "__main__":
    try:
        # 获取随机可用端口
        port = get_random_available_port(min_port=49152, max_port=65535)

        if port:
            print(f"找到可用端口: {port}")
        else:
            print("经过多次尝试，未能找到可用端口")
    except ValueError as e:
        print(f"错误: {e}")