from NatNetClient import NatNetClient
from ZJUVision import ZJUVisionServer
import time


# This is a callback function that gets connected to the NatNet client and called once per mocap frame.
def receiveNewFrame(frameNumber, tracedata, latency, isRecording):
    # print("Received frame from Motive", frameNumber)
    f = open('Motive', 'w')
    try:
        f.write(frameNumber, "from Motive: ", tracedata, " Latency: ", latency)
    finally:
        f.close()

# This will create a new NatNet client
serverIP = input("the IP address of server: ")
multicastIP = input("the multicast IP address: ")
target = input("the model you want to trace: ")
streamingClient = NatNetClient(serverIP, multicastIP, target)

# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streamingClient.newFrameListener = receiveNewFrame


# This is a callback function that gets connected to the ZJUVisionServer. It is called once per frame.
def receiveZJU(data, addr):
    f = open('ZJUVision', 'w')
    try:
        f.write("Receive: ", data, " from: ", addr)
    finally:
        f.close()

# Create a new ZJUVision client
zjuvisionserver=ZJUVisionServer()

# Configure the Server
zjuvisionserver.newFrameListener=receiveZJU

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()
zjuvisionserver.run()

time.sleep(10)

streamingClient.stop()
zjuvisionserver.stop()
