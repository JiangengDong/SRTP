import socket
from threading import Thread


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
        if  hostip is '0.0.0.0':
            self.host = socket.gethostname()
        else:
            self.host = hostip
        self.port = port
        self.newFrameListener = None
        self.serverSocket = None
        self.datathread = None
        self.__stopthread = 0

    def __createsocket(self):
        # 创建 socket 对象
        serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定端口
        serversocket.bind((self.host, self.port))
        print("Ready. ")
        return serversocket

    def __datathreadfunction(self, visionsocket):
        while not self.__stopthread:
            data, addr = visionsocket.recvfrom(256)
            # data = data.decode('utf-8')
            if len(data) > 0:
                self.newFrameListener(data, addr)

    def run(self):
        self.serverSocket = self.__createsocket()
        if self.serverSocket is None:
            print("Could not open data channel. ")
            exit()
        self.datathread = Thread(target=self.__datathreadfunction, args=(self.serverSocket,))
        self.datathread.start()

    def stop(self):
        # Stop thread
        self.__stopthread = 1
        self.datathread.join()
        self.__stopthread = 0

        # close socket
        self.serverSocket.close()
