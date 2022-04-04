from pyclbr import Function
from File import *
from Message import *
from Header import *
from threading import Thread
from socket import socket,gethostbyname,gethostname,error
from queue import SimpleQueue
from logic import Game, Player,Board,Tile

def debug(txt):
    if DEBUG:
        print(txt)

class Sock:
    """
    Peer-to-Peer Socket operations
    
    """
    def __init__(self,host,port) -> None:
        self.host = gethostbyname(gethostname())
        self.port = port
        self.sock : socket
        self.queue = SimpleQueue()
        self.name = b"unknown"
        self.running = True
        self.connected = False

    def configure(self, onmessage_callback:Function=print,onconnection_close:Function=None,onconnection_open:Function= None,onfile_receive:Function=None):
        self.onmessage_callback = onmessage_callback
        self.onconnection_close = onconnection_close
        self.onconnection_open = onconnection_open
        self.onfile_receive = onfile_receive


    def send(self,message:bytes):
        #universell für client und server
        debug("creating header")
        header = get_header(message)
        debug("sending header")
        self.sock.send(header)
        debug(f"sending {message}")
        self.sock.send(message)

    def close(self):
        self.sock.close()

    def file_send(self,file_path):
        #sending a file
        def do():
            for mes in format_file(file_path=file_path,user=self.name):
                self.send(mes)

        localThread = Thread(target=do,name="filesend")
        localThread.start()
        

    def format_send(self,message_bytes, type_=TEXTID,user=b"unknown"):
        #universell für client und server
        if type(message_bytes) is not bytes: message_bytes = message_bytes.encode()
            
        def do():
            meslist = format_message(message_bytes, type_=type_,user=user)
            for mes in meslist:
                self.send(mes)
            
        localThread = Thread(target=do,name="format_send")
        localThread.start()


    def receive(self):
        self.name = self.sock.getsockname()[0].__str__().encode()
        #receiving the message and calling process_mes 
        def do():
            debuf_dict = {}
            while self.running:
                try:
                    header = self.sock.recv(HEADER)
                    incoming_message_len = decode_header(header)
                    debug(f"header received {incoming_message_len}")
                    if not self.running: return 
                    data = self.sock.recv(incoming_message_len)
                    debug(f"receiving {data}")
                    mes = read_message(data)
                    debug(f"reading {mes}")

                except error as ex: self.close();return 
                
                if not mes["id"] in debuf_dict: 
                    debuf_dict.update({mes["id"]:{}})

                debuf_dict[mes["id"]].update({mes["buffer"]:mes})

                if is_last_buffer(mes["buffer"]):
                    self.process_mes(debuf_dict[mes["id"]])
                
                

        localThread = Thread(target=do,name="receive")
        localThread.start()
        


    def process_mes(self,meslist:dict):
        """
        self.onmessage_callback is the function called when a Textmessage appears
        """
        self.onmessage_callback : Function
        def do():
            debuf_data = b"" 
            
            
            #sorting the dictionary keys
            l = [buf.split(".")[0] for buf in meslist.keys()]
            keys = [f"{i}.{len(l)}" for i in l]

            #putting the data together 
            for key in keys:
                mes = meslist[key]

                message_id = mes["id"]
                message_type = mes["type"]
                message_buffer = mes["buffer"]
                message_file_extension = mes["file_extension"]
                message_file_size = mes["file_size"]
                message_file_name = mes["file_name"]
                message_data = mes["data"]
                message_sender = mes["user"]

                debuf_data += message_data  

            if message_type == TEXTID: self.onmessage_callback(data=debuf_data.decode(),user=message_sender)

            elif message_type == FILEID:
                if len(debuf_data) == message_file_size:
                    self.onfile_receive(data=debuf_data,file_extension=message_file_extension,file_name=message_file_name)
                    #get_file(debuf_data,message_file_extension)
                else:
                    print("File missing data, try sending again")

        localThread = Thread(target=do,name="process_mes")
        localThread.start()
    

    def close(self):
        self.running = False
        self.sock.close()
        self.onconnection_close()
    


