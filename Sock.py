
from File import *
from Message import *
from Header import *
from threading import Thread
from socket import socket,gethostbyname,gethostname,error
from queue import SimpleQueue
from logic import Game, Player,Board,Tile
from encrypt import *

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

        
        # rsa keys
        #own public and private key
        self.public_key, self.private_key = create_rsa_keypair()
        # the peer's public key
        self.connection_public_key = None
        # whether the peers public key has been received by the client
        self.self_received_connection_public_key = False
        # the peer received the own public key
        self.connection_received_self_public_key = False
        # the rsa handshake is done
        self.rsa_handshake_complete = False


        #aes keys
        # the peers aes key, used for decrypting
        self.connection_aes_key = None
        # whether the peers aes key has been received by the client
        self.self_received_connection_aes_key = False
        # own aes key, used for encrypting
        self.aes_key = create_aes_key()
        # the peer received the own aes key
        self.connection_received_self_aes_key = False
        # the rsa handshake is done        
        self.aes_handshake_complete = False

        #handshake is done
        self.handshake_complete = False
        
   

    def configure(self, onmessage_callback=print,onconnection_close=None,onconnection_open= None,onfile_receive=None):
        self.onmessage_callback = onmessage_callback
        self.onconnection_close = onconnection_close
        self.onconnection_open = onconnection_open
        self.onfile_receive = onfile_receive


    def send(self,message:bytes):
        #universell für client und server
        # the handshake is done, so aes can be used for encrypting the message
        if self.aes_handshake_complete: message = encrypt_aes(self.aes_key,message)
        # the rsa handshake is done but not the aes handshake so rsa can be used for encrypting the aes key
        elif self.rsa_handshake_complete: message = encrypt_rsa(self.connection_public_key, message)
        # neither rsa or aes handshake is complete, so messages will be sent unencrypted
        else: pass

        debug("creating header")
        header = get_header(message)
        debug("sending header")
        self.sock.send(header)
        debug("sending {message}")
        self.sock.send(message)

    def close(self):
        self.sock.close()

    def file_send(self,file_path):
        #sending a file
        def do():
            for mes in format_file(file_path=file_path,user=self.name):
                self.send(mes)
            debug("file finished sending")

        localThread = Thread(target=do,name="filesend")
        localThread.start()
        

    def format_send(self,message_bytes, type_=TEXTID,user=b"unknown"):
        #universell für client und server
        if type(message_bytes) is not bytes: message_bytes = message_bytes.encode()
        if type(user) is not bytes: user = user.encode()
       
                 
        def do():
            meslist = format_message(message_bytes, type_=type_,user=user)
            for mes in meslist:
                self.send(mes)
            
        localThread = Thread(target=do,name="format_send")
        localThread.start()    

    def handshake(self):
        
        self.format_send(self.public_key,type_=PUBLICKEYID,user="rsa_handshake")      
        debug("sending public key") 

    def aes_handshake(self):
        self.format_send(self.aes_key,type_=AESKEYID,user="aes_handshake")
        debug("sending aes key")





    def receive(self):
        self.name = self.sock.getsockname()[0].__str__().encode()
        #handshake to get the public key
       
        #receiving the message and calling process_mes 
        def do():
            debuf_dict = {}
            self.handshake()
            while self.running:
                try:
                    header = self.sock.recv(HEADER)
                    incoming_message_len = decode_header(header)
                    debug(f"header received {incoming_message_len}")
                    if not self.running: return 
                    data = self.sock.recv(incoming_message_len)

                    debug(f"receiving {data}")

                    # check whether the message is encrypted
                    data_encrypted = is_encrypted(data)

                    # if the message is encrypted using aes, decrypt it
                    if data_encrypted and self.aes_handshake_complete:
                        data = decrypt_aes(self.connection_aes_key,data)
                    
                    # if the message is encrypted using rsa, decrypt it
                    elif data_encrypted and self.rsa_handshake_complete:
                        data = decrypt_rsa(self.private_key,data)

                    # if the message is not encrypted, pass
                    else: pass

                    mes = read_message(data)

                    debug(f"reading {mes}")

                except error as ex: self.close();debug("server error occured");return 
                
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
        self.onmessage_callback 
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

            # receiving the peer's public key, sending a PUBLICKE_RECEIVED message to confirm
            elif message_type == PUBLICKEYID and not self.connection_received_self_public_key:
                # saving the peer's public key
                self.connection_public_key = debuf_data
                # the client has the public key of the peer
                self.self_received_connection_public_key = True
                
                debug(f"received public key  {self.connection_public_key}")
                # sending a message to confirm the public key has been received by the client
                self.format_send(b"confirm publickey received",type_=PUBLICKEY_RECEIVED,user="rsa_handshake_confirm")

            elif message_type == PUBLICKEY_RECEIVED:
                # the peer has the public key of the client
                self.connection_received_self_public_key = True

                debug(f"the connection partner received public key confirmation")

                if self.connection_received_self_public_key and self.self_received_connection_public_key:
                    # the client and the peer have the public key of each other
                    self.rsa_handshake_complete = True
                    debug("rsa handshake complete")
                    self.aes_handshake()

            
            elif message_type == AESKEYID and not self.self_received_connection_aes_key:
                # saving the peer's aes key
                self.connection_aes_key = debuf_data
                # the client has the aes key of the peer
                self.self_received_connection_aes_key = True
                
                debug(f"received aes key {self.connection_aes_key}")
                # sending a message to confirm the aes key has been received by the client
                self.format_send(b"confirm handshake",type_=AES_RECEIVED,user="aes_handshake_received")

            elif message_type == AES_RECEIVED and not self.connection_received_self_aes_key:
                # the peer has the aes key of the client
                self.connection_received_self_aes_key = True

                debug("received aes key confirmation")
                
                if self.connection_received_self_aes_key and self.self_received_connection_aes_key:
                    # the client and the peer have the aes key of each other
                    self.aes_handshake_complete = True
                    debug("aes handshake complete")
                    

            elif message_type == FILEID:
                
                self.onfile_receive(data=debuf_data,file_extension=message_file_extension,file_name=message_file_name,file_size=message_file_size)
                 #get_file(debuf_data,message_file_extension)
          

        localThread = Thread(target=do,name="process_mes")
        localThread.start()
    

    def close(self):
        self.running = False
        self.sock.close()
        self.onconnection_close()
    


