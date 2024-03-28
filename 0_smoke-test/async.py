import asyncore
import socket


HOST = "0.0.0.0"
PORT = 9090
ADDR = (HOST, PORT)


class EchoHandler(asyncore.dispatcher):
    def __init__(self, conn):
        asyncore.dispatcher.__init__(self, sock=conn)

    def handle_read(self):
        data = self.recv(200_000)
        if data:
            self.send(data)


class AsyncTcpServer(asyncore.dispatcher):
    def __init__(self, addr: tuple[str, int]):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(addr)
        self.listen(10)

    def handle_accept(self):
        conn, addr = self.accept()
        print(f"[+] New connection {conn.getsockname()} from {addr}")
        EchoHandler(conn)

    def handle_close(self):
        self.close()


if __name__ == "__main__":
    server = AsyncTcpServer(ADDR)
    asyncore.loop()
