import numpy as np
import os
import threading

class DataRecorder:
    def __init__(self, SN: str):
        '''
        Create a DataRecorder to record tactile data frames.

        Parameters
        ----------
        SN: str
            Sensor SN. Subsequent frames recorded using the analyzer must have the
            same SN.
        '''
        self.SN = SN
        self._fieldNames = ['sendTimestamp',
                            'recvTimestamp',
                            'index',
                            '3D_Positions',
                            '3D_Displacements',
                            '3D_Normals',
                            '3D_Forces',
                            '3D_ResultantForce',
                            '3D_ResultantMoment',
                            ]
        self._lock = threading.Lock()
        self.clear()

    def clear(self):
        '''
        Clear the recorded frames in cache.
        '''
        self._lock.acquire()
        self._data = {}
        for name in self._fieldNames:
                self._data[name] = []
        self._lock.release()
    
    def put(self, frame):
        '''
        Add a frame to be recorded into the cache.

        Parameters
        ----------
        frame: dict
            A tactile data frame.
        '''
        if frame['SN'] != self.SN:
            print('[Warning] The input frame does not match the DataRecorder. (DataRecorder: {}  frame: {})'.format(self.SN, frame['SN']))
            return
        self._lock.acquire()
        for name in self._fieldNames:
            field = frame.get(name)
            if not field is None:
                self._data[name].append(field)
        self._lock.release()

    def getSize(self):
        '''
        Get the number of cached frames.
        
        Return
        ----------
        size: int
            The number of cached frames.
        '''
        return len(self._data['index'])
    
    def save(self, path: str):
        '''
        Save the cached frames to the specified disk path.
        
        Parameters
        ----------
        path: str
            The path to save the data, which will be automatically created if it
            does not exist.
        '''
        if not os.path.isdir(os.path.join(path, self.SN)):
            os.makedirs(os.path.join(path, self.SN))
            
        self._lock.acquire()
        for name in self._fieldNames:
            fieldData = self._data.get(name)
            if len(fieldData) != 0:
                np.save(os.path.join(path, self.SN, name+'.npy'), np.array(fieldData))
        print('[Info] Data saved: {}. (DataRecorder: {})'.format(path, self.SN))
        self._lock.release()

class DataLoader:
    def __init__(self, path:str, SN:str, skip=0):
        '''
        Create a DataLoader for loading saved data.  

        Parameters
        ----------
        SN: str
            Sensor SN of the data.
        path: str
            The path of the data folder.
        skip (optional): int
            Number of initial frames to skip.
        '''
        self.SN = SN
        self._skip = skip
        self._fieldNames = ['sendTimestamp',
                            'recvTimestamp',
                            'index',
                            '3D_Positions',
                            '3D_Displacements',
                            '3D_Normals',
                            '3D_Forces',
                            '3D_ResultantForce',
                            '3D_ResultantMoment',
                            ]
        self._data = {}
        self._lock = threading.Lock()
        print('Load data from {}'.format(os.path.join(path, self.SN)))
        for name in self._fieldNames:
            try:
                self._data[name] = np.load(os.path.join(path, self.SN, name + ".npy"))
            except:
                print('[Warning] cannot load data "{}". (DataLoader: {})'.format(name, self.SN))
        
        idx = self._data.get('index')
        if idx is None:
            raise FileNotFoundError('[Error] cannot load data from "{}".  (DataLoader: {})'.format(os.path.join(path, self.SN), self.SN))
        
        self.frameNum = len(idx)
        self._current = 0
        self._startTime = self._data['sendTimestamp'][self._skip]
        self.reset(self._skip)
        
    def get(self):
        '''
        Get the next frame.  
        '''
        self._lock.acquire()

        frame = {'SN': self.SN}
        for name in self._data.keys():
            frame[name] = self._data[name][self._current]
        frameTime = frame['sendTimestamp'] - self._startTime
        
        if self._current + 1 < self.frameNum:
            self._current += 1
            endFlag = False
        else:
            endFlag = True
            
        self._lock.release()
        return frame, frameTime, endFlag
    
    def reset(self, pos=None):
        '''
        Return to the start. If `pos` is specified, jump to the pos-th frame.
        
        Parameters
        ----------
        pos (optional): int
            Jump to the pos-th frame.
        '''
        if pos is None:
            pos = self._skip

        if pos >=0 and pos < self.frameNum:
            
            self._lock.acquire()
            self._current = pos
            self._lock.release()
            return True
        else:
            print('[Warning] pos {} is out of range. (DataLoader:{})'.format(pos, self.SN))
            return False
    