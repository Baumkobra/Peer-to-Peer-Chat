
from math import ceil
from typing import Union
from uuid import uuid4




CHUNK = 64
TEXTID: bytes = b"/t"
GAMEID : bytes = b"/g"
INFOID : bytes = b"/i"
FILEID : bytes = b"/f"
PUBLICKEYID : bytes = b"/p"
SEPERATOR: bytes = b"<-|->"
STARTER: bytes = b"<#>"
ENDER: bytes = b">#<"
DEBUG = True

def debug(txt):
    if DEBUG:
        print()
        print(txt)



def read_message(message_bytes:bytes) -> dict[str:bytes]:
    message_split =  message_bytes.split(SEPERATOR,9)

    return {
        "id":message_split[1].decode(),
        "type":message_split[2],
        "buffer":message_split[3].decode(),
        "file_extension":message_split[4].decode(),
        "file_size":int(message_split[5].decode()) if message_split[5] != b" " else 0, 
        "file_name":message_split[6].decode(),
        "data":message_split[7],
        "user":message_split[8].decode()
        }



def format_message(message_bytes, type_ : bytes,user: bytes = b"unkown",buffer:bytes = b" ", file_extension : bytes = b" ", file_name:bytes=b" ",file_size : bytes = b" " ) -> list[bytes]:
    bufferdict = buffer_message(message_bytes)
    messages : list[bytes] = []
    id = uuid4()
    for key, item in bufferdict.items():
        buffer = key + b"." + len(bufferdict).__str__().encode()
        message : bytes = STARTER + SEPERATOR+ id.__str__().encode() + SEPERATOR + type_ + SEPERATOR + buffer + SEPERATOR + file_extension + SEPERATOR + file_size + SEPERATOR +file_name + SEPERATOR + item +SEPERATOR+ user + SEPERATOR+ ENDER
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
    return messagebuffer


def is_last_buffer(buffer:bytes) -> bool:
    buf_split = buffer.split(".")
    if buf_split[0] == buf_split[1]:
    
        return True
    else:
        return False
