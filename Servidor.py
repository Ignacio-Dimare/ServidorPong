import socket

class TCPServer:

    def __init__(self, host, port, buffer_size, keepalive_timeout=10):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.keepalive_timeout = keepalive_timeout
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Servidor iniciado en {self.host}:{self.port}")

        while True:
            conn , addr = self.server_socket.accept()
            print(f"Conexion recibida de: {addr}")

    def keep_alive(self):


    def stop(self):
        self.server_socket.close()
        print("Servidor detenido.")