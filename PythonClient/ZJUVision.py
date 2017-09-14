import socket
from threading import Thread


class ZJUVisionServer:
    def __init__(self, port=2008):
        self.host = socket.gethostname()
        self.port = port
        self.newFrameListener = None
        self.serverSocket = None
        self.datathread = None

    def __createsocket(self):
        # 创建 socket 对象
        serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定端口
        serversocket.bind((self.host, self.port))
        print("Ready. ")
        return serversocket

    def __datathreadfunction(self, visionsocket):
        while True:
            data, addr = visionsocket.recvfrom(256)
            if len(data) > 0:
                self.newFrameListener(data, addr)

    def run(self):
        self.serverSocket = self.__createsocket()
        if self.serverSocket is None:
            print("Could not open data channel. ")
            exit()
        self.datathread = Thread(target=self.__datathreadfunction, args=(self.serverSocket,))
        self.datathread.start()
