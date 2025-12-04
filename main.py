from Servidor import TCPServer
import os
import time
import signal
import ast
import fcntl, os

HOST = "127.0.0.1"
PORT = 5000

players = {}
current_session = 1
next_player_slot = 1

# Creo PIPE envio UDP
read_envioUDP, write_envioUDP = os.pipe()

# Creo PIPE recibe UDP e imprime
read_recUDP, write_recUDP = os.pipe()

# Creo PIPE nuevo hijo
read_newChild, write_newChild = os.pipe()

# Creo PIPE players diponibles
read_availablePlayers, write_availablePlayers = os.pipe()

def make_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

def register_player(addr):
    global current_session, next_player_slot, players

    try:
        playersAvailable = os.read(read_availablePlayers, 1024)
    except BlockingIOError:
        playersAvailable = None

    if playersAvailable:
        key = playersAvailable.decode()
    else:
        key = f"player_{next_player_slot}-{current_session}"

        if next_player_slot == 1:
            next_player_slot = 2
        else:
            next_player_slot = 1
            current_session += 1

    players[key] = addr
    print("Registrado:", key, "->", addr)

    mensaje = f"add,{key},{addr}".encode()
    os.write(write_newChild, mensaje)

    return key


def main():
    #Proceso ejemplo escribe
    make_nonblocking(read_newChild)
    make_nonblocking(read_envioUDP)
    make_nonblocking(read_availablePlayers)
    pid = os.fork()
    if pid == 0:
        i = 0
        os.close(read_recUDP)
        os.close(write_recUDP)
        os.close(read_envioUDP)
        while True:
            mensaje = f"player_1-1 Contador {i}".encode()
            os.write(write_envioUDP, mensaje)
            i += 1
            mensaje = f"player_2-1 Contador {i}".encode()
            os.write(write_envioUDP, mensaje)
            i += 1
            mensaje = f"player_1-2 Contador {i}".encode()
            os.write(write_envioUDP, mensaje)
            i += 1
            mensaje = f"player_2-2 Contador {i}".encode()
            os.write(write_envioUDP, mensaje)
            i += 1
            mensaje = f"player_1-3 Contador {i}".encode()
            os.write(write_envioUDP, mensaje)
            i += 1
            time.sleep(1)
        os._exit(0)

    # Proceso ejemplo recibe e imprime
    pid = os.fork()
    if pid == 0:
        i = 0
        os.close(read_envioUDP)
        os.close(write_envioUDP)
        os.close(write_recUDP)
        while True:
            data = os.read(read_recUDP, 1024)
            if data:
                print(data)
        os._exit(0)

    server = TCPServer(
        host=HOST,
        port=PORT,
        buffer_size=1024,
        keepalive_timeout=10
    )

    server.start()

    os.close(write_envioUDP)
    os.close(read_recUDP)

    # ---------- HIJO UDP (escucha) ----------
    pid_escucha = os.fork()
    if pid_escucha == 0:
        while True:
            data, udp_addr = server.udp_receive(False)
            if udp_addr is None:
                continue
            mensaje = f"[UDP] Cliente UDP: {udp_addr}, Mensaje: {data}".encode()
            os.write(write_recUDP, mensaje)
        os._exit(0)

    # ---------- HIJO UDP (envío) ----------
    pid_envio = os.fork()
    if pid_envio == 0:
        # LOCAL del diccionario para evitar inconsistencias
        players = {}

        while True:
            #Actualizo el diccionario de players
            try:
                data = os.read(read_newChild, 1024)
            except BlockingIOError:
                data = None

            if data:
                data = data.decode()
                partes = data.split(",")

                op = partes[0]
                key = partes[1]

                # reconstruyo addr COMPLETO
                addr_str = ",".join(partes[2:])  # ('127.0.0.1', 55516)

                import ast
                addr = ast.literal_eval(addr_str)  # → ('127.0.0.1', 55516)

                print("Hijo registra:", key, addr)

                if op == "add":
                    players[key] = addr
                elif op == "del":
                    players.pop(key, None)

            try:
                data = os.read(read_envioUDP, 1024)
            except BlockingIOError:
                data = None

            if data:
                data = data.decode()
                partes = data.split(" ")

                key = partes[0]
                mensaje = partes[1]

                addr = players.get(key)
                if addr is None:
                    print(f"El player {key} no existe")
                    continue

                #Envio dato recibido por el pipe
                print("Enviando a:", key, addr)
                server.udp_send(addr, mensaje.encode())

        os.close(read_envioUDP)
        os._exit(0)

    os.close(read_newChild)
    while True:
        conn, tcp_addr, udp_addr_cliente = server.acceptConnections()

        playerKey = register_player(udp_addr_cliente)

        # ---------- HIJO KeepAlive ----------
        if os.fork() == 0:
            server.keepAlive(conn, tcp_addr)

            mensaje = f"del,{playerKey},{tcp_addr}".encode()

            os.write(write_newChild, mensaje)

            os.write(write_availablePlayers, playerKey.encode())

            os._exit(0)


if __name__ == "__main__":
    main()