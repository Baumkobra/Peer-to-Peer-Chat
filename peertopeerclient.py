import socket
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
from datetime import datetime
from Header import *
from Message import *
from Sock import Sock, debug
from queue import SimpleQueue
from logic import Game, Player,Board,Tile
HOST, PORT = "127.0.0.1", 50000

debug(datetime.now().strftime("%H:%M:%S"))

class Client(Sock):
    def __init__(self,host,port) -> None:
        super().__init__(host,port)
        self.sock:socket
        self.queue : SimpleQueue
        self.host = host
        self.port = port

        localThread =Thread(target=self.connect,name="client_connect")
        localThread.start()

    def connect(self):
       
        self.sock = socket(AF_INET, SOCK_STREAM)
        debug(f"connecting to {self.host}:{self.port}")
        
        try:self.sock.connect((self.host,self.port))
        except Exception as ex: return ex
        debug(f"connected to {self.host}:{self.port}")
        self.onconnection_open()
        self.connected = True
        self.receive()

 

    def output(self,mes):
        print(mes)
    



if __name__ == "__main__":
    s = Client()
    while True:
        inp = input("enter:")
        s.format_send(inp.encode())
        #s.file_send(r"C:\Users\mariu\OneDrive - BG Perchtoldsdorf\Schule\helloworld\socktac\newfile2.jpg")
        


