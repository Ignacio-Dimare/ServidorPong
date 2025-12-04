from Cliente import Client
import os

def main():
    client = TCPClient("127.0.0.1", 5001)

    server_udp_port = client.connectTCP()

    # ----- Hijo KEEPALIVE -----
    pid_keep = os.fork()
    if pid_keep == 0:
        client.send_keepalive()
        os._exit(0)

    # ----- Hijo receptor UDP -----
    pid_udp = os.fork()
    if pid_udp == 0:
        client.udp_listen()
        os._exit(0)

    # ----- Padre: enviar mensajes UDP -----
    while True:
        msg = input("UDP> ")
        if msg.lower() == "exit":
            break

        client.udp_send(server_udp_port, msg)

    print("Cerrando cliente...")
    os.kill(pid_keep, 9)
    os.kill(pid_udp, 9)


if __name__ == "__main__":
    main()
