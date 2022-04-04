import socket
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from datetime import datetime
from Header import * 
from Message import *
from threading import Thread
from Sock import Sock, debug
from logic import Game, Player,Board,Tile
HOST, PORT = "127.0.0.1", 50000

debug(datetime.now().strftime("%H:%M:%S"))


class Server(Sock):
    def __init__(self,host,port) -> None:
        super().__init__(host,port)
        self.sock : socket

        localThread = Thread(target=self.listen,name="server_listen")
        localThread.start()
        

    def listen(self):
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.socket.bind((self.host,self.port))
        self.socket.listen()
        debug(f"listening on {self.host}:{self.port}")
        self.accept()

    def accept(self):
        debug(f"accepting on {self.host}:{self.port}")
        try:self.sock, self.addr = self.socket.accept()
        except OSError: return False
        debug(f"new connection to{self.addr}")
        self.onconnection_open()
        self.connected = True
        self.receive()

    def close(self):
        if self.connected: self.sock.close()
        self.socket.close()
        self.onconnection_close()


if __name__ == "__main__":
    s = Server()

    while True:
        inp = input("enter:")
        s.format_send(inp.encode())




