import socket
from server import Servidor

HOST = "127.0.0.1"
PORT = 5000

def main():
    server = TCPServer(
        host = HOST,
        port = PORT,
        keepalive_timeout = 10,
        buffer_size = 1024
    )

    server.start()

if __name__ == "__main__":
    main()