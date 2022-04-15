import os
from sys import getsizeof
from Message import *


def format_file(file_path, user: bytes = b"unknown"):
    if type(file_path) is bytes:
        temp = file_path.rsplit(b"/", maxsplit=1)[-1]
        file_extension = temp.split(b".", maxsplit=1)[-1]
        file_name = temp.split(b".", maxsplit=1)[0]
    elif type(file_path) is str:
        temp = file_path.rsplit("/", maxsplit=1)[-1]
        file_extension = temp.split(".", maxsplit=1)[-1].encode()
        file_name = temp.split(".", maxsplit=1)[0].encode()
    with open(file_path, "rb") as file:
        data = file.read()
    data_len = len(data).__str__().encode()
    return format_message(
        data,
        FILEID,
        file_extension=file_extension,
        file_size=data_len,
        file_name=file_name,
        user=user,
    )


def get_file(data: bytes, file_extension, savepath=os.getcwd(), file_name="newfile"):
    path = f"{savepath}/{file_name}.{file_extension}"

    with open(path, "wb") as file:
        file.write(data)
    return path


def smart_file_send(file_path, user: bytes = b"unknown", func=print):
    if type(file_path) is bytes:
        temp = file_path.rsplit(b"/", maxsplit=1)[-1]
        file_extension = temp.split(b".", maxsplit=1)[-1]
        file_name = temp.split(b".", maxsplit=1)[0]
    elif type(file_path) is str:
        temp = file_path.rsplit("/", maxsplit=1)[-1]
        file_extension = temp.split(".", maxsplit=1)[-1].encode()
        file_name = temp.split(".", maxsplit=1)[0].encode()

    # open a file and read the bytes in FILECHUNK chunks and pass them to the send function
    with open(file_path, "rb") as file:
        # print the bytes of the file

        file_size = file.seek(0, os.SEEK_END)

        amount_of_buffers = ceil(file_size / CHUNK)

        file.seek(0)

        data = file.read(CHUNK)
        id = uuid4().__str__().encode()
        buffer = 1
        while data:
            formatted_data = single_format_message(
                data,
                id,
                FILEID,
                user=user,
                file_extension=file_extension,
                file_name=file_name,
                file_size=file_size.__str__().encode(),
                amount_of_buffers=amount_of_buffers.__str__().encode(),
                buffer=buffer.__str__().encode(),
            )
            func(formatted_data)
            data = file.read(CHUNK)
            buffer += 1


if __name__ == "__main__":
    smart_file_send(
        r"C:\Users\mariu\Downloads\R55VD6TM2JDDXF77FVMR5MSNS4.jpg",
        func=print,
    )
