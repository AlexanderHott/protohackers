################################
################################ BAD, USE sync_2.py
################################
import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 9090
ADDR = (HOST, PORT)

MALFORMATTED = json.dumps({"error": "malformed"}).encode() + b"\n"


def is_prime(x: int | float) -> bool:
    if isinstance(x, float):
        return False

    if x < 2:
        return False

    for i in range(2, x):
        if x % i == 0:
            return False

    return True


def handle_connection(conn: socket.socket, addr: tuple[str, int]):
    print(f"[+] Connection established with {addr}")
    with conn:
        data = conn.recv(200000)
        print(data)

        if data:
            try:
                parsed_data = json.loads(data.decode())
            except json.JSONDecodeError:
                print(f"[!] Error parsing data: {data}")
                conn.send(MALFORMATTED)
                return

            try:
                method = parsed_data["method"]
                number = parsed_data["number"]
                if method == "isPrime":
                    result = is_prime(number)
                    resp = (
                        json.dumps({"method": "isPrime", "prime": result}).encode()
                        + b"\n"
                    )
                    conn.send(resp)
                    return
                else:
                    print(f"[!] Invalid JSON values: {data}")
                    conn.send(MALFORMATTED)
                    return
            except KeyError:
                print(f"[!] Invalid JSON keys: {data}")
                conn.send(MALFORMATTED)
                return


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(ADDR)

        print(f"[*] Starting server on {sock.getsockname()}")

        threads = []
        sock.listen(100)
        while True:
            print("[-] waiting for connection...")
            conn, addr = sock.accept()

            t = threading.Thread(target=handle_connection, args=(conn, addr))
            t.start()
            threads.append(t)


if __name__ == "__main__":
    main()
