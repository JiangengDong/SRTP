from NatNetClient import NatNetClient
from UDPServer import UDPServer
from threading import (Thread, Event)
from multiprocessing import Process
from GUI import app
import time


class WriteFile:
    def __init__(self, filename, mode='w'):
        self.__f = open(filename, mode)

    def write(self, str):
        self.__f.write(str)

    def __del__(self):
        self.__f.close()


def natnet_proc(stop_signal, server_ip, multicast_ip):
    """
    a process that get data from NatNet continuously

    :param Event stop_signal: used for process synchronization
    :param Str server_ip:
    :param Str multicast_ip:
    :return:
    """
    def natnet_data(frameNumber, tracedata, latency):
        s = str(frameNumber)+' '+str(tracedata)+str(latency)+'\n'
        print(s)

    natnet = NatNetClient(serverIP=server_ip,
                          clientIP="0.0.0.0",
                          multicastIP=multicast_ip)
    natnet.newFrameListener = natnet_data
    natnet.initial('Rigid Body 1')
    print("start NatNet process, connecting to %s")
    while stop_signal.is_set():
        natnet.receiveData()
    natnet.stop()


def zju_proc(stop_signal):
    """
    a process that get data from ZJUVision continuously

    :param Event stop_signal: used for process synchronization
    :return:
    """
    def ZJUdata(data, addr):
        s = str(data.decode('utf-8')) + '\n'
        print(s)

    zju = UDPServer(hostip='192.168.1.100', port=2008)
    zju.newFrameListener = ZJUdata
    zju.initial()
    while stop_signal.is_set():
        zju.run()
    zju.stop()


def main():
    stop_signal = Event()
    stop_signal.set()

    natnet = Thread(target=natnet_proc, args=(stop_signal,))
    zju_vision = Thread(target=zju_proc, args=(stop_signal,))
    zju_vision.start()
    natnet.start()

    time.sleep(10)
    stop_signal.clear()
    zju_vision.join()
    natnet.join()


def backend():
    time.sleep(5)
    print(app.get_ip())
    app.write_info("1")


if __name__ == '__main__':

    b = Process(target=backend)
    b.start()

    app.mainloop()