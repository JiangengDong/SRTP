from NatNetClient import NatNetClient
from ZJUVision import ZJUVisionServer


# This is a callback function that gets connected to the NatNet client and called once per mocap frame.
def receiveNewFrame(frameNumber, tracedata, latency, isRecording):
    print("Received frame", frameNumber)


# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receiveRigidBodyFrame(id, position, rotation):
    print("Received frame for rigid body", id)


# This will create a new NatNet client
serverIP = input("the IP address of server: ")
multicastIP = input("the multicast IP address: ")
target = input("the model you want to trace: ")
streamingClient = NatNetClient(serverIP, multicastIP, target)

# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streamingClient.newFrameListener = receiveNewFrame
streamingClient.rigidBodyListener = receiveRigidBodyFrame

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()
