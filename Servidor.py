
import socket
import select
import time
import os


class TCPServer:

    def __init__(self, host, port, buffer_size, keepalive_timeout=10):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.keepalive_timeout = keepalive_timeout

        # TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # UDP (puerto aleatorio)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind((self.host, 0))
        print("UDP escuchando en:", self.udp_sock.getsockname()[1])

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Servidor TCP iniciado en {self.host}:{self.port}")

    def acceptConnections(self):
        conn, addr = self.server_socket.accept()
        print(f"Conexion TCP desde: {addr}")

        # Enviar puerto UDP al cliente
        udp_port = self.udp_sock.getsockname()[1]
        conn.sendall(str(udp_port).encode())

        # El servidor espera recibir el puerto UDP del cliente
        data = conn.recv(self.buffer_size)
        udp_port_cliente = int(data.decode())
        print(f"Cliente {addr} tiene puerto UDP: {udp_port_cliente}")

        udp_addr_cliente = (addr[0], udp_port_cliente)

        return conn, addr, udp_addr_cliente

    def tcp_send(self, conn, data):
        conn.sendall(data)

    # -------- UDP --------

    def udp_send(self, udp_addr, data: bytes):
        self.udp_sock.sendto(data, udp_addr)

    def udp_receive(self, block):
        """Recibe cualquier mensaje UDP"""
        self.udp_sock.setblocking(block)
        try:
            data, addr = self.udp_sock.recvfrom(self.buffer_size)
            return data, addr
        except BlockingIOError:
            return None, None

    # -------- KEEPALIVE TCP --------

    def keepAlive(self, conn, addr):
        while True:
            r, _, _ = select.select([conn], [], [], self.keepalive_timeout)

            if not r:
                print(f"Timeout keepalive de {addr}")
                conn.close()
                break

            try:
                data = conn.recv(self.buffer_size)
                if not data:
                    print(f"Cliente {addr} cerro TCP")
                    break

            except:
                break

        conn.close()
