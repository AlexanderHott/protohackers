import socket
import threading

HOST = "0.0.0.0"
PORT = 9090
ADDR = (HOST, PORT)


def handle_connection(conn: socket.socket, addr: tuple[str, int]):
    print(f"[+] Connection established with {addr}")
    with conn:
        data = conn.recv(200000, socket.MSG_WAITALL)

        if data:
            print(data)
            print(f"[!] Sending data: {data}")
            conn.send(data)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(ADDR)

        print(f"[*] Starting server on {ADDR} | {sock.getsockname()}")

        threads = []
        sock.listen(10)
        while True:
            print("[-] waiting for connection...")
            conn, addr = sock.accept()

            t = threading.Thread(target=handle_connection, args=(conn, addr))
            t.start()
            threads.append(t)


if __name__ == "__main__":
    main()
