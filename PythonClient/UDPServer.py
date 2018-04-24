import socket
from threading import Thread
from threading import Event


class UDPServer:
    """
    a server that can only receive data. It has two public methods, one thread and one callback.

    Two public methods are listed below:
    1. run()                    start thread and receive data
    2. stop()                   stop thread

    One callback:
    1. newFrameListener(data, addr)
    """

    def __init__(self, hostip='0.0.0.0', port=2008):
        if hostip is '0.0.0.0':
            self.__host = socket.gethostname()
        else:
            self.__host = hostip
        self.__port = port
        self.newFrameListener = None
        self.__serverSocket = None

    def __createsocket(self):
        # 创建 socket 对象
        serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定端口
        serversocket.bind((self.__host, self.__port))
        print("Ready. ")
        return serversocket

    def run(self):
        data, addr = self.__serverSocket.recvfrom(256)
        if len(data) > 0:
            self.newFrameListener(data, addr)

    def initial(self):
        self.__serverSocket = self.__createsocket()
        if self.__serverSocket is None:
            print("Could not open data channel. ")
            exit()

    def stop(self):
        self.__serverSocket.close()
