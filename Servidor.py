import socket
import signal
import os

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

            pid = os.fork()

            if pid == 0:
                while True:
                    print("Itera")

            if os.fork() == 0:
                while True:
                    # Armo el select
                    rlist, _, _ = select.select([conn], [], [], KEEPALIVE_TIMEOUT)

                    if not rlist:
                        # No llegaron datos, salio por timeout
                        print(f"Timeout de keepalive para {addr}. Cerrando conexion...")
                        self.server_socket.close()
                        os.kill(pid, signal.SIGKILL)
                        break

                    try:
                        data = conn.recv(BUFFER_SIZE)

                        if not data:
                            print(f"Cliente {addr} cerro la conexion.")
                            break

                        mensaje = data.decode()
                        print(f"{addr}: {mensaje}")
                        conn.sendall(b"OK")

                    except ConnectionResetError:
                        print(f"Cliente {addr} reseteo la conexion.")
                        self.server_socket.close()
                        os.kill(pid, signal.SIGKILL)
                        break


    def keep_alive(self):


    def stop(self):
        self.server_socket.close()
        print("Servidor detenido.")