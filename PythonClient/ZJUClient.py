from ZJUVision import UDPServer
import time


def writefile(filename, str):
    f = open(filename, "a")
    try:
        f.write(str)
    finally:
        f.close()


def newframe(data, addr):
    data = data.decode("UTF-8").split(" ")
    num = int(data[1])
    pos = [float(data[3]), float(data[5]), float(data[7])]
    timestamp = float(data[-2])
    print(num, " ",  pos, ' ', timestamp)
    

zjurecv = UDPServer()
zjurecv.newFrameListener = newframe

zjurecv.run()

time.sleep(10)

zjurecv.stop()