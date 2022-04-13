
from tkinter import DISABLED, END, WORD, BooleanVar, Button, Checkbutton, Frame, Menu, Tk, filedialog, simpledialog,Toplevel,Label
from tkinter.font import NORMAL
from tkinter.scrolledtext import ScrolledText
from File import get_file
from peertopeerclient import *
from peertopeerserver import *
from socket import getfqdn, gethostbyname_ex,gethostbyname,gethostname

class Window(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.master = master
        self.name = b"you"
        self.sock = None
        self.has_socket = False
        self.is_connected = False
        self.file_queue = SimpleQueue()

        menu = Menu(self.master)
        self.master.configure(menu=menu)

        settingsmenu = Menu(menu,tearoff=0)
        settingsmenu.add_command(label="Exit",command=self.exit)
        menu.add_cascade(label="Client",menu=settingsmenu)

        connectmenu = Menu(menu,tearoff=0)
        connectmenu.add_command(label="host",command=self.host)
        connectmenu.add_command(label="connect",command=self.connect)
        connectmenu.add_command(label="close",command=self.abort_connection)
        connectmenu.add_command(label="username",command=self.get_username)
        menu.add_cascade(label="Connection",menu=connectmenu)

        filemenu = Menu(menu,tearoff=0)
        filemenu.add_command(label="send File",command=self.send_file)
        filemenu.add_command(label="get File",command=self.get_file)
        menu.add_cascade(label="File",menu=filemenu)


        frame1 = Frame(self.master)
        self.text_area = ScrolledText(frame1, wrap=WORD, width=50,height=15)
        self.text_area.grid(column = 0, pady=10, padx=10)
        self.text_area.configure(state = DISABLED)

        self.text_inp = ScrolledText(frame1, wrap=WORD,height=1, width = 50)
        self.text_inp.grid(column=0, row=1, pady=10, padx=20)

        self.text_btn = Button(frame1,height=1, width=10, text="send", command=self.get_text_input)
        self.text_btn.grid(column=0, row=2, pady=10, padx=10)
        frame1.pack()
    

    def get_username(self):    
        var = simpledialog.askstring("Username","Enter Username")
        if var is None: return
        if var == "": return
        self.name = var.encode()

    def send_file(self):
        path = filedialog.askopenfilename()
        if path == "": return
        path = path
        
        if not self.has_socket: self.display(data="Establish a connection before sending a file\n",user="[INFO]");return
        if not self.is_connected: self.display(data="Establish a connection before sending a file\n",user="[INFO]");return
        self.sock.file_send(path.encode())
        self.display(data=f"sending file: {path}\n",user="[INFO]")

    def get_text_input(self):
        text = self.text_inp.get(1.0, END)
        self.display(data=text,user=self.name)
        self.text_inp.delete(1.0,END)
        self.send(text.encode())

    def on_file_receive(self,**kwargs):
        self.file_queue.put({"data":kwargs["data"],"file_extension":kwargs["file_extension"],"file_name":kwargs["file_name"]})
        self.display(data=f"new file received:{kwargs['file_name']}.{kwargs['file_extension']}, {kwargs['file_size']}bytes\n",user="[INFO]")
    
    def get_file(self):
        top= Toplevel(self.master)
        top.geometry("300x250")
        top.title("Child Window")
    
        def close_child():
            top.destroy()

        if self.file_queue.empty(): 
            label = Label(top,text="No files available")
            label.pack()
            button_close = Button(top,text="close",command=close_child)
            button_close.pack()
            return

        files = {}
        while not self.file_queue.empty():
            file = self.file_queue.get()
            files.update({file["file_name"]:file})

        available_files = {}
       
        def get():
            path = filedialog.askdirectory()
            if path == "": put_all_back();return
            top.destroy()
            if not True in available_files.values(): put_all_back();return

            for name,var in available_files.items():
                if var:
                    file = files[name]
                    info = get_file(data=file["data"],file_extension=file["file_extension"],savepath=path,file_name=file["file_name"])
                    self.display(data=f"Datei {file['file_name']} in {info} gespeichert.\n",user="[INFO]")
                else:  
                    self.file_queue.put(files[name])
        
        def put_all_back():
            for file in files.values():
                self.file_queue.put(file)
            top.destroy()
  
        top.protocol("WM_DELETE_WINDOW", put_all_back)
        for file in files.values():
            bvar = BooleanVar()
            f = f'{file["file_name"]}.{file["file_extension"]}'
            Checkbutton(top, text=f,variable = bvar, onvalue=True, offvalue=False,anchor="w").pack(anchor="w")
            available_files.update({file["file_name"]:bvar})
        button = Button(top,text="download",command=get)
        button.pack()      

    def on_connection_close(self):
        self.display(data="connection closed\n",user="[INFO]")
        self.has_socket = False
        self.is_connected = False
       

    def on_connection_open(self):
        self.display(data=f"connection established\n",user="[INFO]")
        self.is_connected = True

       
    def display(self,**kwargs):
        text = kwargs["data"]
        user = kwargs["user"] if type(kwargs["user"]) is str else kwargs["user"].decode()

        mes = f"{user}:{text}"
        self.text_area.configure(state=NORMAL)
        self.text_area.insert(END,mes)
        self.text_area.configure(state=DISABLED)
        self.text_area.see(END)


    def send(self,text):
        if not self.has_socket: self.display(data="You are not currently connected or hosting a connection\n",user="[INFO]"); return
        if not self.is_connected: self.display(data="You are not yet connected\n",user="[INFO]");return
        self.sock.format_send(text,user=self.name)

    def host(self):
        if self.has_socket: self.display(data="can't create a new socket, close the old one first\n",user="[INFO]"); return
        def do():
            self.sock = Server(port=50000,onmessage_callback=self.display,onconnection_close=self.on_connection_close,onconnection_open=self.on_connection_open,onfile_receive=self.on_file_receive)
            self.display(data=f"attemting to host socket on {self.sock.host}:{self.sock.port}\n",user="[INFO]")

            self.has_socket = True

            self.name = self.sock.name if self.name == b"you" else self.name

            self.display(data=f"hosting chat on {self.sock.host}:{self.sock.port}\n",user="[INFO]")
        localThread = Thread(target=do,name="host setup")
        localThread.start()

    

    def connect(self):
        if self.has_socket: self.display(data="can't a new socket, close the old one first\n",user="[INFO]"); return
        ip = simpledialog.askstring("IP Adress","Enter IP Adress").encode()
        def do():
            self.sock = Client(host=ip,port=50000,onmessage_callback=self.display,onconnection_close=self.on_connection_close,onconnection_open=self.on_connection_open,onfile_receive=self.on_file_receive)
            self.display(data=f"attempting to connect to {self.sock.host if type(self.sock.host) is str else self.sock.host.decode()}:{self.sock.port}\n",user="[INFO]")
           
            self.has_socket = True
            self.name = self.sock.name if self.name == b"you" else self.name
        
            self.display(data=f"joining chat on {self.sock.host if type(self.sock.host) is str else self.sock.host.decode()}:{self.sock.port}\n",user="[INFO]")

        localThread = Thread(target=do,name="connect setup")
        localThread.start()

    def abort_connection(self):
        if not self.has_socket: return

        self.sock.close()
        self.display(data="Verbindung wurde geschlossen\n",user="[INFO]")

    def exit(self):
        self.destroy()
        exit()


if __name__ == "__main__":
    root = Tk()
    root.geometry("500x400")
    app = Window(root)
    root.wm_title("Peer-to-Peer Client")
    root.mainloop()