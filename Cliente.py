import socket
import os
import time
import select

class Client:

    def __init__(self, server_ip, server_port, buffer_size=1024, keepalive_interval=2):
        self.server_ip = server_ip
        self.server_port = server_port
        self.buffer_size = buffer_size
        self.keepalive_interval = keepalive_interval

        # TCP
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # UDP (cliente)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(("", 0))   # cualquier puerto
        self.client_udp_port = self.udp_sock.getsockname()[1]

        print("[UDP] Puerto UDP del cliente:", self.client_udp_port)

    # ---------------- TCP ----------------

    def connectTCP(self):
        self.tcp_sock.connect((self.server_ip, self.server_port))
        print("[TCP] Conectado al servidor.")

        # Recibir puerto UDP del servidor
        server_udp_port = int(self.tcp_sock.recv(self.buffer_size).decode().strip())
        print("[TCP] Puerto UDP del servidor:", server_udp_port)

        # Enviar puerto UDP del cliente
        self.tcp_sock.sendall(f"{self.client_udp_port}\n".encode())
        print("[TCP] Enviado puerto UDP del cliente.")

        return server_udp_port

    def send_keepalive(self):
        while True:
            try:
                self.tcp_sock.sendall(b"KEEPALIVE\n")
            except:
                print("[TCP] KeepAlive falló. Cerrando proceso.")
                break
            time.sleep(self.keepalive_interval)

    # ---------------- UDP ----------------

    def udp_listen(self):
        while True:
            r, _, _ = select.select([self.udp_sock], [], [], 0.5)
            if self.udp_sock in r:
                data, addr = self.udp_sock.recvfrom(self.buffer_size)
                print(f"\n[UDP recibido] {data.decode().strip()}")
                print("UDP> ", end="", flush=True)

    def udp_send(self, server_udp_port, msg):
        self.udp_sock.sendto(msg.encode(), (self.server_ip, server_udp_port))
