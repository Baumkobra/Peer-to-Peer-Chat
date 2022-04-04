from peertopeerclient import Client
from peertopeerserver import Server




def main():
    while True:
        inp = input("für server 0 für client 1")
        inp = int(inp)

        if inp == 0:
            s = Server()
            break
        elif inp == 1:
            s = Client()
            break
        

    s.format_send(input("enter"))



if __name__ == "__main__":
    main()