import os
from sys import getsizeof
from Message import *
CHUNK = 4086

def format_file(file_path,user:bytes = b"unknown"):
    if type(file_path) is bytes:
        temp = file_path.rsplit(b'/',maxsplit=1)[-1]   
        file_extension = temp.split(b".",maxsplit=1)[-1]
        file_name = temp.split(b".",maxsplit=1)[0]
    elif type(file_path) is str:
        temp = file_path.rsplit('/',maxsplit=1)[-1]
        file_extension = temp.split(".",maxsplit=1)[-1].encode()
        file_name = temp.split(".",maxsplit=1)[0].encode()
    with open(file_path,"rb") as file:
        data = file.read()
    data_len = len(data).__str__().encode()
    return format_message(data,FILEID,file_extension=file_extension,file_size=data_len,file_name=file_name,user=user)


def get_file(data:bytes, file_extension, savepath = os.getcwd(),file_name="newfile"):
    path = f"{savepath}/{file_name}.{file_extension}"
   
    with open(path, "wb") as file:
        file.write(data)
    return path
    
        


if __name__ == "__main__":
    format_file(r"C:\Users\mariu\OneDrive - BG Perchtoldsdorf\Schule\helloworld\socktac\newfile2.jpg")
    