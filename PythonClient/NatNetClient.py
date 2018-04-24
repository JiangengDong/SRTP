import socket
import struct
import time
from threading import Thread
from threading import Event


def trace(*args):
    pass # print("".join(map(str, args)))


# Create structs for reading various object types to speed up parsing.
Vector3 = struct.Struct('<fff')
Quaternion = struct.Struct('<ffff')
FloatValue = struct.Struct('<f')
DoubleValue = struct.Struct('<d')


class NatNetClient:
    """
    a client to send and receive package from Motive server.
    It has two threads, three public methods, and two callbacks.

    Two threads are listed  below:
    1. self.__commandThread         a thread to send command to and receive response from server
    2. self.__dataThread            a thread to send request to and receive data from server
    These two threads are control by a varibale, self.__stopThread.
    When this variable is set to 1, the threads will stop.

    Two callbacks are listed below:
    1. rigidBodyListener(id, pos, rot)
    2. newFrameListener(frameNumber, tracedata, latency)

    Three methods are listed below:
    1. run()                        start two threads
    2. stop()                       stop two threads
    3. sendCommand()                send command to server
    """

    def __init__(self, serverIP="192.168.1.100", clientIP="0.0.0.0", multicastIP="239.255.42.99"):

        # Change this value to the IP address of the NatNet server.
        self.__serverIPAddress = serverIP

        # This should match the multicast address listed in Motive's streaming settings.
        self.__multicastAddress = multicastIP

        # This is used to choose which ip on this client should be used
        if clientIP is '0.0.0.0':
            self.__hostAddress = ''
        else:
            self.__hostAddress = clientIP

        # NatNet Command channel
        self.__commandPort = 1510

        # NatNet Data channel
        self.__dataPort = 1511

        # marker set to trace
        self.traceset = None

        # Set this to a callback method of your choice to receive per-rigid-body data at each frame.
        self.rigidBodyListener = None

        # Set this to a callback method of your choice to receive new frame
        self.newFrameListener = None

        # NatNet stream version. This will be updated to the actual version the server is using during initialization.
        self.__natNetStreamVersion = (3, 0, 0, 0)

        # A stop flag for threads
        self.__stopThread = Event()

        # thread object
        self.__commandThread = None
        self.__dataThread = None

    # Client/server message ids
    NAT_PING = 0
    NAT_PINGRESPONSE = 1
    NAT_REQUEST = 2
    NAT_RESPONSE = 3
    NAT_REQUEST_MODELDEF = 4
    NAT_MODELDEF = 5
    NAT_REQUEST_FRAMEOFDATA = 6
    NAT_FRAMEOFDATA = 7
    NAT_MESSAGESTRING = 8
    NAT_DISCONNECT = 9
    NAT_UNRECOGNIZED_REQUEST = 100
    COMMANDS = {'UnitsToMilimeters', 'FrameRate', 'StartRecording', 'StopRecording',
                'LiveMode', 'EditMode', 'CurrentMode', 'TimelinePlay', 'TimelineStop',
                'SetPlaybackTakeName', 'SetRecordTakeName', 'SetCurrentSession',
                'SetPlaybackStartFrame', 'SetPlaybackStopFrame', 'SetPlaybackCurrentFrame',
                'CurrentTakeLength', 'AnalogSamplesPerMocapFrame'}

    # Create a data socket to attach to the NatNet stream
    def __createDataSocket(self, ip, port):
        result = socket.socket(socket.AF_INET,  # Internet
                               socket.SOCK_DGRAM,
                               socket.IPPROTO_UDP)  # UDP
        result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result.bind((ip, port))

        mreq = struct.pack("4sl", socket.inet_aton(self.__multicastAddress), socket.INADDR_ANY)
        result.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        return result

    # Create a command socket to attach to the NatNet stream
    def __createCommandSocket(self, ip):
        result = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        result.bind((ip, 0))
        result.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        return result

    # Unpack a rigid body object from a data packet
    def __unpackRigidBody(self, data):
        offset = 0

        # skip header
        offset += 32
        # # ID (4 bytes)
        # id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        # offset += 4
        # trace("ID:", id)
        #
        # # Position and orientation
        # pos = Vector3.unpack(data[offset:offset + 12])
        # offset += 12
        # trace("\tPosition:", pos[0], ",", pos[1], ",", pos[2])
        # rot = Quaternion.unpack(data[offset:offset + 16])
        # offset += 16
        # trace("\tOrientation:", rot[0], ",", rot[1], ",", rot[2], ",", rot[3])

        # Marker count (4 bytes)
        markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        markerCountRange = range(0, markerCount)
        trace("\tMarker Count:", markerCount)

        # Send information to any listener.
        if self.rigidBodyListener is not None:
            pass  # self.rigidBodyListener( id, pos, rot )

        # skip position of markers
        offset += 12 * markerCount
        # # Marker positions
        # for i in markerCountRange:
        #     pos = Vector3.unpack( data[offset:offset+12] )
        #     offset += 12
        #     trace( "\tMarker", i, ":", pos[0],",", pos[1],",", pos[2] )

        if (self.__natNetStreamVersion[0] >= 2):
            # skip ID, size and error of markers
            offset += 8 * markerCount + 4
            # # Marker ID's
            # for i in markerCountRange:
            #     id = int.from_bytes( data[offset:offset+4], byteorder='little' )
            #     offset += 4
            #     trace( "\tMarker ID", i, ":", id )
            #
            # # Marker sizes
            # for i in markerCountRange:
            #     size = FloatValue.unpack( data[offset:offset+4] )
            #     offset += 4
            #     trace( "\tMarker Size", i, ":", size[0] )
            #
            # markerError, = FloatValue.unpack( data[offset:offset+4] )
            # offset += 4
            # trace( "\tMarker Error:", markerError )

        # Version 2.6 and later
        if (((self.__natNetStreamVersion[0] == 2) and (self.__natNetStreamVersion[1] >= 6)) or
                    self.__natNetStreamVersion[0] > 2 or self.__natNetStreamVersion[0] == 0):
            param, = struct.unpack('h', data[offset:offset + 2])
            trackingValid = (param & 0x01) != 0
            offset += 2
            trace("\tTracking Valid:", 'True' if trackingValid else 'False')

        return offset

    # Unpack a skeleton object from a data packet
    def __unpackSkeleton(self, data):
        offset = 0

        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("ID:", id)

        rigidBodyCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Rigid Body Count:", rigidBodyCount)
        for j in range(0, rigidBodyCount):
            offset += self.__unpackRigidBody(data[offset:])

        return offset

    # Unpack data from a motion capture frame message
    def __unpackMocapData(self, data):
        trace("Begin MoCap Frame\n-----------------\n")

        data = memoryview(data)
        offset = 0
        tracedata = []

        # Frame number (4 bytes)
        frameNumber = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Frame #:", frameNumber)

        # Marker set count (4 bytes)
        markerSetCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Marker Set Count:", markerSetCount)

        for i in range(0, markerSetCount):
            # Model name
            modelName, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(modelName) + 1
            trace("Model Name:", modelName.decode('utf-8'))

            # Marker count (4 bytes)
            markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Marker Count:", markerCount)

            tracedata = [None]*markerCount
            for j in range(0, markerCount):
                pos = Vector3.unpack(data[offset:offset + 12])
                offset += 12
                if True:
                    tracedata[j] = pos
                    trace("\tMarker", j, ":", pos[0],",", pos[1],",", pos[2])

        # Unlabeled markers count (4 bytes)
        unlabeledMarkersCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Unlabeled Markers Count:", unlabeledMarkersCount)

        # skip unlabeled markers
        for i in range( 0, unlabeledMarkersCount ):
            pos = Vector3.unpack(data[offset:offset+12])
            offset += 12
            trace("\tMarker", i, ":", pos[0],",", pos[1],",", pos[2])

        # Rigid body count (4 bytes)
        rigidBodyCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        trace("Rigid Body Count:", rigidBodyCount)

        for i in range(0, rigidBodyCount):
            offset += self.__unpackRigidBody(data[offset:])

        # Version 2.1 and later
        skeletonCount = 0
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] > 0) or self.__natNetStreamVersion[
            0] > 2):
            skeletonCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Skeleton Count:", skeletonCount)
            for i in range(0, skeletonCount):
                offset += self.__unpackSkeleton(data[offset:])

        # Labeled markers (Version 2.3 and later)
        labeledMarkerCount = 0
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] > 3) or self.__natNetStreamVersion[
            0] > 2):
            labeledMarkerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Labeled Marker Count:", labeledMarkerCount)
            for i in range(0, labeledMarkerCount):
                id = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
                pos = Vector3.unpack(data[offset:offset + 12])
                offset += 12
                size = FloatValue.unpack(data[offset:offset + 4])
                offset += 4

                # Version 2.6 and later
                if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 6) or
                            self.__natNetStreamVersion[0] > 2):
                    param, = struct.unpack('h', data[offset:offset + 2])
                    offset += 2
                    occluded = (param & 0x01) != 0
                    pointCloudSolved = (param & 0x02) != 0
                    modelSolved = (param & 0x04) != 0

        # Force Plate data (version 2.9 and later)
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 9) or self.__natNetStreamVersion[
            0] > 2):
            forcePlateCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            trace("Force Plate Count:", forcePlateCount)
            for i in range(0, forcePlateCount):
                # ID
                forcePlateID = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
                trace("Force Plate", i, ":", forcePlateID)

                # Channel Count
                forcePlateChannelCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4

                # Channel Data
                for j in range(0, forcePlateChannelCount):
                    trace("\tChannel", j, ":", forcePlateID)
                    forcePlateChannelFrameCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
                    offset += 4
                    for k in range(0, forcePlateChannelFrameCount):
                        forcePlateChannelVal = int.from_bytes(data[offset:offset + 4], byteorder='little')
                        offset += 4
                        trace("\t\t", forcePlateChannelVal)

        # Latency
        latency, = FloatValue.unpack(data[offset:offset + 4])
        offset += 4

        # Timecode
        timecode = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4
        timecodeSub = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        # Timestamp (increased to double precision in 2.7 and later)
        if ((self.__natNetStreamVersion[0] == 2 and self.__natNetStreamVersion[1] >= 7) or self.__natNetStreamVersion[
            0] > 2):
            timestamp, = DoubleValue.unpack(data[offset:offset + 8])
            offset += 8
        else:
            timestamp, = FloatValue.unpack(data[offset:offset + 4])
            offset += 4

        # Frame parameters
        # param, = struct.unpack('h', data[offset:offset + 2])
        # isRecording = (param & 0x01) != 0
        # trackedModelsChanged = (param & 0x02) != 0
        # offset += 2

        # Send information to any listener.
        if self.newFrameListener is not None:
            self.newFrameListener(frameNumber, tracedata, latency)

    # Unpack a marker set description packet
    def __unpackMarkerSetDescription(self, data):
        offset = 0

        name, separator, remainder = bytes(data[offset:]).partition(b'\0')
        offset += len(name) + 1
        trace("Markerset Name:", name.decode('utf-8'))

        markerCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        for i in range(0, markerCount):
            name, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(name) + 1
            trace("\tMarker Name:", name.decode('utf-8'))

        return offset

    # Unpack a rigid body description packet
    def __unpackRigidBodyDescription(self, data):
        offset = 0

        # Version 2.0 or higher
        if (self.__natNetStreamVersion[0] >= 2):
            name, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(name) + 1
            trace("\tMarker Name:", name.decode('utf-8'))

        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        parentID = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        timestamp = Vector3.unpack(data[offset:offset + 12])
        offset += 12

        return offset

    # Unpack a skeleton description packet
    def __unpackSkeletonDescription(self, data):
        offset = 0

        name, separator, remainder = bytes(data[offset:]).partition(b'\0')
        offset += len(name) + 1
        trace("\tMarker Name:", name.decode('utf-8'))

        id = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        rigidBodyCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        for i in range(0, rigidBodyCount):
            offset += self.__unpackRigidBodyDescription(data[offset:])

        return offset

    # Unpack a data description packet
    def __unpackDataDescriptions(self, data):
        offset = 0
        datasetCount = int.from_bytes(data[offset:offset + 4], byteorder='little')
        offset += 4

        for i in range(0, datasetCount):
            type = int.from_bytes(data[offset:offset + 4], byteorder='little')
            offset += 4
            if (type == 0):
                offset += self.__unpackMarkerSetDescription(data[offset:])
            elif (type == 1):
                offset += self.__unpackRigidBodyDescription(data[offset:])
            elif (type == 2):
                offset += self.__unpackSkeletonDescription(data[offset:])

    def __processMessage(self, data):
        trace("Begin Packet\n------------\n")

        messageID = int.from_bytes(data[0:2], byteorder='little')
        trace("Message ID:", messageID)

        packetSize = int.from_bytes(data[2:4], byteorder='little')
        trace("Packet Size:", packetSize)

        offset = 4
        if (messageID == self.NAT_FRAMEOFDATA):
            self.__unpackMocapData(data[offset:])
        elif (messageID == self.NAT_MODELDEF):
            self.__unpackDataDescriptions(data[offset:])
        elif (messageID == self.NAT_PINGRESPONSE):
            offset += 256  # Skip the sending app's Name field
            offset += 4  # Skip the sending app's Version info
            self.__natNetStreamVersion = struct.unpack('BBBB', data[offset:offset + 4])
            offset += 4
        elif (messageID == self.NAT_RESPONSE):
            if (packetSize == 4):
                commandResponse = int.from_bytes(data[offset:offset + 4], byteorder='little')
                offset += 4
            else:
                message, separator, remainder = bytes(data[offset:]).partition(b'\0')
                offset += len(message) + 1
                trace("Command response:", message.decode('utf-8'))
        elif (messageID == self.NAT_UNRECOGNIZED_REQUEST):
            trace("Received 'Unrecognized request' from server")
        elif (messageID == self.NAT_MESSAGESTRING):
            message, separator, remainder = bytes(data[offset:]).partition(b'\0')
            offset += len(message) + 1
            trace("Received message from server:", message.decode('utf-8'))
        else:
            trace("ERROR: Unrecognized packet type")

        trace("End Packet\n----------\n")

    def sendCommand(self, command, commandStr, socket, address):
        # Compose the message in our known message format
        if (command == self.NAT_REQUEST_MODELDEF or command == self.NAT_REQUEST_FRAMEOFDATA):
            packetSize = 0
            commandStr = ""
        elif (command == self.NAT_REQUEST):
            packetSize = len(commandStr) + 1
        elif (command == self.NAT_PING):
            commandStr = "Ping"
            packetSize = len(commandStr) + 1

        data = command.to_bytes(2, byteorder='little')
        data += packetSize.to_bytes(2, byteorder='little')

        data += commandStr.encode('utf-8')
        data += b'\0'

        socket.sendto(data, address)

    def receiveCommand(self):
        # Block for input
        data = [0]
        while len(data) < 256:
            data, addr = self.__commandSocket.recvfrom(32768)  # 32k byte buffer size
        self.__processMessage(data)

    def initial(self, traceset):
        # Create the data socket
        self.__dataSocket = self.__createDataSocket(self.__hostAddress, self.__dataPort)
        if self.__dataSocket is None:
            print("Could not open data channel")
            exit()

        # Create the command socket
        self.__commandSocket = self.__createCommandSocket(self.__hostAddress)
        if self.__commandSocket is None:
            print("Could not open command channel")
            exit()

        # get stream version and start streaming
        self.sendCommand(self.NAT_PING, "Ping", self.__commandSocket, (self.__serverIPAddress, self.__commandPort))
        self.receiveCommand()
        self.sendCommand(self.NAT_REQUEST_FRAMEOFDATA, "",
                         self.__commandSocket, (self.__serverIPAddress, self.__commandPort))

        self.traceset = traceset

    def receiveData(self):
        # Block for input
        data, addr = self.__dataSocket.recvfrom(32768)  # 32k byte buffer size
        if (len(data) > 0):
            self.__processMessage(data)

    def stop(self):
        # close sockets
        self.__dataSocket.close()
        self.__commandSocket.close()
