from Servidor import TCPServer
import os
import time

HOST = "127.0.0.1"
PORT = 5000

players = {}
current_session = 1
next_player_slot = 1

# Creo PIPE envio UDP
read_envioUDP, write_envioUDP = os.pipe()

# Creo PIPE recibe UDP e imprime
read_recUDP, write_recUDP = os.pipe()

def register_player(addr):
    global current_session, next_player_slot, players

    key = f"player_{next_player_slot}-{current_session}"
    players[key] = addr
    print("Registrado:", key, "->", addr)

    if next_player_slot == 1:
        next_player_slot = 2
    else:
        next_player_slot = 1
        current_session += 1


def main():
    #Proceso ejemplo escribe
    pid = os.fork()
    if pid == 0:
        i = 0
        os.close(read_recUDP)
        os.close(write_recUDP)
        os.close(read_envioUDP)
        while True:
            mensaje = f"Contador {i}".encode()
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

    while True:
        conn, tcp_addr, udp_addr_cliente = server.acceptConnections()

        register_player(udp_addr_cliente)

        # ---------- HIJO UDP (escucha) ----------
        if os.fork() == 0:
            while True:
                data, udp_addr = server.udp_receive(False)
                if udp_addr is None:
                    continue
                mensaje = f"[UDP] Cliente UDP: {udp_addr}, Mensaje: {data}".encode()
                os.write(write_recUDP, mensaje)
            os._exit(0)

        # ---------- HIJO UDP (envío) ----------
        if os.fork() == 0:
            # COPIA LOCAL del diccionario para evitar inconsistencias
            local_players = list(players.items())  # [(key, addr), ...]

            index = 0
            total = len(local_players)

            while True:
                key, addr = local_players[index]

                data = os.read(read_envioUDP, 1024)

                print("Enviando a:", key, addr)
                server.udp_send(addr, data)

                index = (index + 1) % total
                time.sleep(1)
            os.close(read_envioUDP)
            os._exit(0)

        # ---------- HIJO KeepAlive ----------
        if os.fork() == 0:
            server.keepAlive(conn, tcp_addr)
            os._exit(0)


if __name__ == "__main__":
    main()
