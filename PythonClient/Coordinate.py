from NatNetClient import NatNetClient
from UDPServer import UDPServer
import time
import csv

try:
    natnetFile = open('natnetData.csv', 'w')
    natnetCSV = csv.writer(natnetFile)
    natnetCSV.writerows(['No.', 'points', 'latency'])
    ZJUVisionFile = open('ZJUVision.csv', 'w')
    ZJUVisionCSV = csv.writer(ZJUVisionFile)
    ZJUVisionCSV.writerows(['No.', 'points', 'latency'])

    def natnetdata(frameNumber, tracedata, latency):
        # s = str(frameNumber)+' '+str(tracedata)+str(latency)+'\n'
        # print(s)
        natnetCSV.writerows([frameNumber, tracedata, latency])


    natnet = NatNetClient('192.168.1.100', '192.168.1.100')
    natnet.newFrameListener = natnetdata


    def ZJUdata(data, addr):
        # s = str(data.decode('utf-8')) + '\n'
        # print(s)
        s = str(data.decode('utf-8')).split(' ')
        tracedata = [int(s[1]), float(s[3]), float(s[5]), float(s[7])]
        ZJUVisionCSV.writerows(tracedata)


    ZJU = UDPServer('192.168.1.100')
    ZJU.newFrameListener = ZJUdata

    natnet.run()
    ZJU.run()
    while True:
        pass
finally:
    natnetFile.close()
    ZJUVisionFile.close()