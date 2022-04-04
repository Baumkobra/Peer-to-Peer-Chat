HEADER = 1024




def get_header(message : bytes) -> bytes:
    header = f"{len(message):<{HEADER}}".encode()
    return header


def decode_header(header : bytes) -> int: 
    header : str = header.decode()
    header = header.strip(" ")
    header = int(header)
    return header