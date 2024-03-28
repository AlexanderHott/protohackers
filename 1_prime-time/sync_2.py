import json
import socket
import threading
from collections import defaultdict

from itertools import count

# TODO: use `select`
from select import select

HOST = "0.0.0.0"
PORT = 9090
ADDR = (HOST, PORT)
SEED = 22801763489
"""One-billionth prime number"""


class PrimeTest:
    def __init__(self):
        self.__P = {}
        self.__gen = self.__primes()
        self.__top = 0

    @staticmethod
    def __primes():
        ps = defaultdict(list)
        for i in count(2):
            if i not in ps:
                yield i
                ps[i ** 2].append(i)
            else:
                for n in ps[i]:
                    ps[i + (n if n == 2 else 2 * n)].append(n)
                del ps[i]

    def __next_prime(self) -> int:
        i = next(self.__gen)

        print(f"Prime found: {i}")
        self.__P[i] = None
        self.__top = max(self.__top, i)
        return i

    def is_prime(self, n: int | float) -> bool:

        # Is it a known prime?
        if n in self.__P:
            return True
        if isinstance(n, float):
            return False
        # Is it a known composite?
        if n <= self.__top and n not in self.__P:
            return False

        # Trial division
        for p in self.__P:
            if p * p > n:
                return True
            if n % p == 0:
                return False

        # Make new primes on the fly until sqrt
        while True:
            p = self.__next_prime()
            if p * p > n:
                return True
            if n % p == 0:
                return False


pt = PrimeTest()


class ThreadedServer(object):
    def __init__(self, addr: tuple[str, int]):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(addr)

    def listen(self):
        self.sock.listen(5)
        print(f"[*] listening on {self.sock.getsockname()}")
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(
                target=self.listen_to_client, args=(client, address)
            ).start()

    def listen_to_client(self, client: socket.socket, address: tuple[str, int]):
        size = 1024 * 1024
        while True:
            try:
                data: bytes = b""
                data = client.recv(size)
                if not data.endswith(b"\n"):
                    raise Exception("Invalid data: no trailing newline")
                if data:
                    for req in data.decode().strip().split("\n"):
                        print(f"req: {req!r}")
                        response = self.generate_response(req)
                        print(f"[+] Sending data: {response!r}")
                        client.send(response)
            except Exception as e:
                print(f"[!] Error: {e}: {data!r}")
                client.send(json.dumps({"error": "error"}).encode() + b"\n")
                client.close()
                return False

    def generate_response(self, data: str) -> bytes:
        parsed_data = json.loads(data)
        try:
            method = parsed_data["method"]
            number = parsed_data["number"]
            if (
                method != "isPrime"
                or not (isinstance(number, int) or isinstance(number, float))
                or isinstance(number, bool)
            ):
                raise KeyError("number is not a number")

            is_prime = pt.is_prime(number)
            resp = json.dumps({"method": "isPrime", "prime": is_prime}).encode() + b"\n"
            return resp
        except Exception as e:
            print(f"[!] Error parsing data: {data}")
            return json.dumps({"error": str(e)}).encode() + b"\n"


if __name__ == "__main__":
    pt.is_prime(SEED)
    ThreadedServer(ADDR).listen()
