import platform
import socket
def hostname() -> str:
    return socket.gethostname()

def ip() -> str:
    return socket.gethostbyname(hostname())