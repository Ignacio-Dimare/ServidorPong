from Cliente import Client
import os
import fcntl
import time

HOST = "127.0.0.1"
PORT = 5000

# Creo PIPE envio UDP
read_envioUDP, write_envioUDP = os.pipe()

# Creo PIPE recibe UDP
read_recUDP, write_recUDP = os.pipe()

def make_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

def main():
    make_nonblocking(read_envioUDP)
    make_nonblocking(read_recUDP)

    client = Client(HOST, PORT)

    server_udp_port = client.connectTCP()

    # Proceso ejemplo escribe
    pid = os.fork()
    if pid == 0:
        i = 0
        os.close(read_recUDP)
        os.close(write_recUDP)
        os.close(read_envioUDP)
        while True:
            mensaje = f"Hola {i}".encode()
            os.write(write_envioUDP, mensaje)
            i += 1
            time.sleep(1)
        os._exit(0)

    # Proceso ejemplo recibe e imprime
    pid = os.fork()
    if pid == 0:
        i = 0
        os.close(write_recUDP)
        os.close(read_envioUDP)
        os.close(write_envioUDP)
        while True:
            try:
                data = os.read(read_recUDP, 1024)
            except BlockingIOError:
                data = None

            if data is None:
                continue

            data = data.decode()
            if data:
                print(f"\n[UDP recibido] {data.strip()}")
        os._exit(0)

    # ----- Hijo KEEPALIVE -----
    pid_keep = os.fork()
    if pid_keep == 0:
        client.send_keepalive()
        os._exit(0)

    # ----- Hijo receptor UDP -----
    pid_udp = os.fork()
    if pid_udp == 0:
        while True:
            data, addr = client.udp_listen()
            if addr is None:
                continue
            mensaje = f"[UDP] Cliente UDP: {addr}, Mensaje: {data}".encode()
            os.write(write_recUDP, mensaje)
        os._exit(0)

    # ----- Padre: enviar mensajes UDP -----
    while True:
        try:
            data = os.read(read_envioUDP, 1024)
        except BlockingIOError:
            data = None

        if data:
            data = data.decode()

            # Envio dato recibido por el pipe
            client.udp_send(server_udp_port, data)

    print("Cerrando cliente...")
    os.kill(pid_keep, 9)
    os.kill(pid_udp, 9)


if __name__ == "__main__":
    main()
