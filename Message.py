
from math import ceil
from typing import Union
from uuid import uuid4




CHUNK = 800
TEXTID: bytes = b"/t"
GAMEID : bytes = b"/g"
INFOID : bytes = b"/i"
FILEID : bytes = b"/f"
PUBLICKEYID : bytes = b"/p"
AESKEYID : bytes = b"/a"
SEPERATOR: bytes = b"|0&-&0|"
STARTER: bytes = b"<<"
ENDER: bytes = b">>"
AES_RECEIVED : bytes = b"/ar"
PUBLICKEY_RECEIVED : bytes = b"/pr"
DEBUG = False	

def debug(txt):
    if DEBUG:
        print()
        print(txt)



def read_message(message_bytes:bytes) -> dict[str:bytes]:
    message_split =  message_bytes.split(SEPERATOR,10)
    if len(message_bytes.split(SEPERATOR)) > 11: debug("seperator error")
    
    return {
        "id":message_split[1].decode(),
        "type":message_split[2],
        "buffer":int(message_split[3].decode()),
        "amount_of_buffers":int(message_split[4].decode()),
        "file_extension":message_split[5].decode(),
        "file_size":int(message_split[6].decode()) if message_split[5] != b" " else 0, 
        "file_name":message_split[7].decode(),
        "data":message_split[8],
        "user":message_split[9].decode()
        }



def format_message(message_bytes, type_ : bytes,user: bytes = b"unkown",buffer:bytes = b" ", amount_of_buffers:bytes = b" ", file_extension : bytes = b" ", file_name:bytes=b" ",file_size : bytes = b" " ) -> list[bytes]:
    bufferdict,amount_of_buffers = buffer_message(message_bytes)
    messages : list[bytes] = []
    id = uuid4()

    for key, item in bufferdict.items():
      
       
        currentbuffer = key
        amount_of_buffers = amount_of_buffers.__str__().encode() if type(amount_of_buffers) is int else amount_of_buffers
      
        message : bytes = STARTER + SEPERATOR+ id.__str__().encode() + SEPERATOR + type_ + SEPERATOR + currentbuffer + SEPERATOR + amount_of_buffers + SEPERATOR + file_extension + SEPERATOR + file_size + SEPERATOR +file_name + SEPERATOR + item +SEPERATOR+ user + SEPERATOR+ ENDER
        messages.append(message)
    return messages


def is_encrypted(message_bytes):
    if (STARTER and SEPERATOR and ENDER in message_bytes): debug("is not encrypted");return False
    debug("is encrypted");return True


def buffer_message(message_bytes) -> dict[bytes]:
    buffers = ceil(len(message_bytes) / CHUNK)
    mes_len = len(message_bytes)
    
    lastbuffer = 0
    messagebuffer: dict = {}
    for buffero in range(1,buffers+1):
        buffer = buffero * CHUNK
        
        if mes_len<buffer:
            mes = message_bytes[lastbuffer:]
        else:
            mes = message_bytes[lastbuffer:buffer]
        lastbuffer = buffer
        messagebuffer.update({buffero.__str__().encode():mes})
    
    debug(f"buffering in {buffers} buffers")
    # returning the buffer dict and the amount of buffers
    return messagebuffer,str(buffers).encode()


def is_last_buffer(buffer:bytes,amount_of_buffers:bytes) -> bool:
    if buffer == amount_of_buffers: return True
    return False


def is_complete_message(bufferdict, amount_of_buffers:bytes,list_of_buffers:list) -> bool:
  
    keys = bufferdict.keys()   
    for num in list_of_buffers:
        if num not in keys: debug("incomplete message"); return False
    debug("complete message")
    return True    