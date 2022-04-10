import socket
from socket import socket, AF_INET, SOCK_STREAM,gethostname,gethostbyname
from time import sleep
from datetime import datetime
from Header import * 
from Message import *
from threading import Thread
from Sock import Sock, debug

hostname = gethostname()
ip_address = gethostbyname(hostname)

HOST, PORT = ip_address, 50000

debug(datetime.now().strftime("%H:%M:%S"))


class Server(Sock):
    def __init__(self,port,onmessage_callback=print,onconnection_close=None,onconnection_open= None,onfile_receive=None) -> None:
        hostname = gethostname()
        ip_address = gethostbyname(hostname)
        host = ip_address
        super().__init__(host,port,onmessage_callback=onmessage_callback,onconnection_close=onconnection_close,onconnection_open=onconnection_open,onfile_receive=onfile_receive)
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
        except OSError: print("OSERROR");return False
        debug(f"new connection to{self.addr}")
        self.onconnection_open()
        self.connected = True
        self.receive()

    def close(self):
        if self.connected: self.sock.close()
        self.socket.close()
        self.onconnection_close()


if __name__ == "__main__":
    s = Server("127.0.0.1",50000)

    while True:
        inp = input("enter:")
        s.format_send(inp.encode())




