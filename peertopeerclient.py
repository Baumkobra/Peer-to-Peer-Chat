import socket
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
from datetime import datetime
from Header import *
from Message import *
from Sock import Sock, debug
from queue import SimpleQueue

# HOST, PORT = "127.0.0.1", 50000

debug(datetime.now().strftime("%H:%M:%S"))


class Client(Sock):
    def __init__(
        self,
        host,
        port,
        onmessage_callback=print,
        onconnection_close=None,
        onconnection_open=None,
        onfile_receive=None,
    ) -> None:
        super().__init__(
            host,
            port,
            onmessage_callback=onmessage_callback,
            onconnection_close=onconnection_close,
            onconnection_open=onconnection_open,
            onfile_receive=onfile_receive,
        )
        self.sock: socket
        self.queue: SimpleQueue
        self.host = host
        self.port = port

        localThread = Thread(target=self.connect, name="client_connect")
        localThread.start()

    def connect(self):

        self.sock = socket(AF_INET, SOCK_STREAM)
        debug(f"connecting to {self.host}:{self.port}")

        try:
            self.sock.connect((self.host, self.port))
        except Exception as ex:
            self.onmessage_callback(data="invalid IP-Adress\n", user="[INFO]")
            self.close()
            return
        debug(f"connected to {self.host}:{self.port}")
        self.connected = True
        self.receive()


if __name__ == "__main__":
    s = Client("127.0.0.1", 50000)
    s.connect()
    while True:
        inp = input("enter:")
        s.format_send(inp.encode())
