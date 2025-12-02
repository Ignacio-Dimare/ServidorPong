from Servidor import TCPServer
import os
from time import sleep

HOST = "127.0.0.1"
PORT = 5000

players = {}
current_session = 1
next_player_slot = 1

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
    server = TCPServer(
        host=HOST,
        port=PORT,
        buffer_size=1024,
        keepalive_timeout=10
    )

    server.start()

    while True:
        conn, tcp_addr = server.acceptConnections()

        register_player(tcp_addr)

        # ---------- HIJO UDP ----------
        if os.fork() == 0:

            udp_addr = None

            print("[UDP] Esperando primer paquete UDP...")

            # Esperar a que el cliente envíe su primer mensaje UDP
            while udp_addr is None:
                data, udp_addr = server.udp_receive()
                sleep(0.05)

            print("[UDP] Cliente UDP conectado desde:", udp_addr)

            # Loop UDP principal
            while True:
                # Enviar mensaje al cliente
                server.udp_send(udp_addr, b"hola")

                # Recibir mensajes del cliente
                data, addr = server.udp_receive()
                print("[UDP recibido del cliente]:", data.decode())


        # ---------- HIJO KeepAlive ----------
        if os.fork() == 0:
            server.keepAlive(conn, tcp_addr)
            exit(0)


if __name__ == "__main__":
    main()
