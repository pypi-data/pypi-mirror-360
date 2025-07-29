import numpy as np
import time
import struct
import queue
import ruamel.yaml
import socket
import threading
import cv2
from typing import Callable

class UDP_Manager:
    def __init__(self, callback, isServer = False, ip = '', port = 8083, frequency = 50, inet = 4):
        self.callback = callback
        
        self.isServer = isServer
        self.interval = 1.0 / frequency

        # self.available_addr = socket.getaddrinfo(socket.gethostname(), port)
        # self.hostname = socket.getfqdn(socket.gethostname())
        self.inet = inet
        self.af_inet = None
        self.ip = ip
        self.localIp = None
        self.port = port
        self.addr = (self.ip, self.port)
        self.running = False
    
    def start(self):
        if self.inet == 4:
            self.af_inet = socket.AF_INET  # ipv4
            self.localIp = '127.0.0.1'
        elif self.inet == 6:
            self.af_inet = socket.AF_INET6 # ipv6
            self.localIp = '::1'
        self.sockUDP = socket.socket(self.af_inet, socket.SOCK_DGRAM)

        if self.isServer:
            self.roleName = 'Server'
        else:
            self.port = 0
            self.roleName = 'Client'
        
        self.sockUDP.bind((self.ip, self.port))
        self.sockUDP.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 212992)
        self.addr = self.sockUDP.getsockname()
        self.ip = self.addr[0]
        self.port = self.addr[1]
        print(self.roleName, '(UDP) at:', self.ip, ':', self.port)
        
        self.running = True
        self.thread = threading.Thread(target = self.receive, args=())
        self.thread.setDaemon(True)
        self.thread.start()  #打开收数据的线程
    
    # def ListAddr(self):
    #     for item in self.available_addr:
    #         if item[0] == self.af_inet:
    #             print(item[4])
    
    def receive(self):
        while self.running:
            time.sleep(self.interval)
            while self.running:
                try:
                    recvData, recvAddr = self.sockUDP.recvfrom(65535) #等待接受数据
                except:
                    break
                if not recvData:
                    break
                self.callback(recvData, recvAddr)
    
    def send(self, data, addr):
        self.sockUDP.sendto(data, addr)
    
    def close(self):
        self.running = False
        self.sockUDP.close()

class CallbackThread:
    def __init__(self):
        pass
    
class Sensor:
    def __init__(self,
                 recvCallback:Callable[[dict, any], None] = None,
                 port:int = 9988,
                 maxQSize:int = 5,
                 callbackParam:any = None):
        '''
        Parameters
        ----------
        recvCallback: Callable[[dict, any], None]
            The callback function `recvCallback(frame, param)` will be automatically
            called once after each data frame is received from Tac3D main program.
            The parameters of the callback function are:
                frame: dict
                    A dictionary containing tactile data. Please refer to the 
                    documentation of Sensor.getFrame() for details about the data
                    structure of 'frame'.
                param: any
                    The `callbackParam` parameter passed in when initializing the
                    sensor.
        port: int
            The UDP port for receiving data. Note that this port should match the
            data receiving port configured in the Tac3D main program.
        maxQSize: int
            Maximum receive queue length. This specifies the maximum length of the
            data frame buffer queue when using Sensor.getFrame() to obtain tactile
            data frames. (Note: This parameter does not affect the recvCallback method
            for acquiring tactile data frames.)
        '''
        self._UDP = UDP_Manager(self._recvCallback_UDP, isServer = True, port = port)
        self._recvBuffer = {}
        self._frameBuffer = {}
        self._maxQSize = maxQSize
        self._recvCallback = recvCallback
        self._callbackParam = callbackParam
        self._count = 0
        self._yaml = ruamel.yaml.YAML()
        self._startTime = time.time()
        self._UDP.start()
        self._fromAddrMap = {}
        self.frame = None
    
    def _addFrameToBuffer(self, frame, name):
        recvQueue = self._frameBuffer.get(name)
        if recvQueue is None:
            recvQueue = queue.Queue()
            self._frameBuffer[frame['SN']] = recvQueue
        
        recvQueue.put(frame)
        if recvQueue.qsize() > self._maxQSize: 
            recvQueue.get()
        
    def _recvCallback_UDP(self, data, addr):
        serialNum, pktNum, pktCount = struct.unpack('=IHH', data[0:8])
        currBuffer = self._recvBuffer.get(serialNum)
        if currBuffer is None:
            currBuffer = [0.0, pktNum, 0, [None]*(pktNum+1)]
            self._recvBuffer[serialNum] = currBuffer
        currBuffer[0] = time.time()
        currBuffer[2] += 1
        currBuffer[3][pktCount] = data[8:]
        
        if currBuffer[2] == currBuffer[1]+1:
            try:
                frame = self._decodeFrame(currBuffer[3][0], b''.join(currBuffer[3][1:]))
                initializeProgress = frame.get('InitializeProgress')
                if initializeProgress != None:
                    if initializeProgress != 100:
                        return
            except:
                print('err')
                return
            self.frame = frame
            self._fromAddrMap[frame['SN']] = addr

            self._addFrameToBuffer(frame, frame['SN'])
            self._addFrameToBuffer(frame, 'any')

            if not self._recvCallback is None:
                self._recvCallback(frame, self._callbackParam)
            del self._recvBuffer[serialNum]
        
        self._count += 1
        if self._count > 2000:
            self._cleanBuffer()
            self._count = 0
        
    def _decodeFrame(self, headBytes, dataBytes):
        head = self._yaml.load(headBytes.decode('ascii'))
        frame = {}
        frame['index'] = head['index']
        frame['SN'] = head['SN']
        frame['sendTimestamp'] = head['timestamp']
        frame['recvTimestamp'] = time.time() - self._startTime
        
        message = head.get('msg')
        if not message is None:  # 兼容3.3.0之前的版本
            if message != '':
                print('[{}] {}'.format(frame['SN'], message))
        else:
            message = ''
        frame['message'] = message
        
        for item in head['data']:
            dataType = item['type']
            if dataType == 'mat':
                dtype = item['dtype']
                if dtype == 'f64':
                    width = item['width']
                    height = item['height']
                    offset = item['offset']
                    length = item['length']
                    frame[item['name']] = np.frombuffer(dataBytes[offset:offset+length], dtype=np.float64).reshape([height, width])
            elif dataType == 'f64':
                offset = item['offset']
                length = item['length']
                frame[item['name']] = struct.unpack('d', dataBytes[offset:offset+length])[0]
            elif dataType == 'i32':
                offset = item['offset']
                length = item['length']
                frame[item['name']] = struct.unpack('i', dataBytes[offset:offset+length])[0]
            elif dataType == 'img':
                offset = item['offset']
                length = item['length']
                frame[item['name']] = cv2.imdecode(np.frombuffer(dataBytes[offset:offset+length], np.uint8), cv2.IMREAD_ANYCOLOR)
        return frame
        
    def _cleanBuffer(self, timeout = 1.0):
        currTime = time.time()
        delList = []
        for item in self._recvBuffer.items():
            if currTime - item[1][0] > timeout:
                delList.append(item[0])
        for item in delList:
            del self._recvBuffer[item]
        
    def getFrame(self, SN:str='any'):
        '''
        Retrieve a frame from the data frame cache queue

        Parameters:
        ----------
        SN (optional): str
            The SN of the sensor intended as the data source. if SN=='any', the data
            source will not be filtered.

        Return
        ----------
        frame: dict or None
            Returns the frontmost frame in the queue when the buffered data frame
            queue is not empty. Returns None when the queue is empty.
            The data type of 'frame' is a dictionary. The initial data includes 
            the following:
            {
                "SN": (str) SN of the Sensor - identifies the tactile sensor that
                    generated this data frame,
                "index": (int) Frame sequence number - counts from 0 when each sensor
                    starts. Each sensor counts independently. Due to initial calibration
                    sampling, the actual received frames don't start from 0.
                "sendTimestamp": (float) Transmission timestamp - time since Tac3D 
                    main program startup. (calculated by Tac3D main program).
                "recvTimestamp": (float) Reception timestamp - time since PyTac3D.Sensor
                    instance initialization (calculated by PyTac3D.Sensor),
                "3D_Positions": (numpy.array) 3D positions of each sensing point.
                    - 400x3 array (rows=point index, columns=x/y/z coordinates),
                "3D_Displacements": (numpy.array) 3D displacements of each sensing
                    point. - 400x3 array (rows=point index, columns=x/y/z components),
                "3D_Normals": (numpy.array) Surface normal directions at each sensing
                    point. - 400x3 array (rows=point index, columns=x/y/z components),
                "3D_Forces": (numpy.array) 3D local forces at each sensing point.
                    - 400x3 array (rows=point index, columns=x/y/z components),
                "3D_ResultantForce": (numpy.array) The resultant contact force.
                    - 1x3 array (columns=x/y/z components),
                "3D_ResultantMoment":  (numpy.array) The resultant contact moment.
                    - 1x3 array (columns=x/y/z components),
            }
        '''
        recvQueue = self._frameBuffer.get(SN)
        if recvQueue is None:
            return None
        if not recvQueue.empty():
            return recvQueue.get()
        else:
            return None
    
    def waitForFrame(self, SN:str='any'):
        '''
        Blocks and waits to receive a data frame until the first frame is received.
        Note that this function is typically used to wait for Tac3D main program
        to start the sensor, rather than waiting for the next frame after receiving
        one. If data frame has already been successfully received before calling this
        function, no blocking wait will occur during its execution.

        Parameters:
        ----------
        SN (optional): str
            The SN of the sensor to wait for. if SN=='any', this function will return
            upon receiving any frame
        '''
        print('Waiting for Tac3D sensor ({})...'.format(SN))
        
        dt = 0.1
        waitTime = 0.0
        warningFlag = True
        recvQueue = self._frameBuffer.get(SN)
        while recvQueue is None:
            time.sleep(dt)
            waitTime += dt
            if warningFlag and waitTime > 3.0:
                print('[Warning] Please confirm if the core program of the Tac3D sensor ({}) is running, and check whether the SDK receiving port is set to {}. Still waiting for Tac3D sensor ({}) ...'.format(SN, self._UDP.port, SN))
                warningFlag = False
            recvQueue = self._frameBuffer.get(SN)

        print('Tac3D sensor ({}) connected. '.format(SN))


    def calibrate(self, SN:str):
        '''
        Sends a calibration signal to main program to reset the zero-point. This
        is equivalent to clicking the "Calibration" button in Tac3D-Desktop.

        Parameters:
        ----------
        SN: str
            The SN of the sensor to calibrate.
        '''
        addr = self._fromAddrMap.get(SN)
        if addr != None:
            print('Calibrate signal send to %s.' % SN)
            self._UDP.send(b'$C', addr)
        else:
            print("Calibtation failed! (sensor %s is not connected)" % SN)
