import sys
import os
import numpy as np
import threading

from nifpga import Session
import nifpga

class GFDMPhy(object):
    def __init__(self, rio):
        self._rio = rio

        self._bitfilename = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Builds/GFDM FPGA Toplevel for 40MHz USRP.lvbitx'))
        assert os.path.exists(self._bitfilename), "Bitfile not found as usual position!"

        self._rxFifoName = 'Needed Resources.grsc\\RX.Data out.T2H'
        self._txFifoName = 'Needed Resources.grsc\\TX.data in.H2T'

    def __enter__(self):
        self._session = Session(self._bitfilename, self._rio)        
        self._session.__enter__()

        self._txFifo = self._session.fifos[self._txFifoName]
        self._txFifo.configure(10000000)
        self._txFifo.start()
        self._rxFifo = self._session.fifos[self._rxFifoName]
        self._rxFifo.configure(10000000)
        self._rxFifo.start()
                
        return self

    def __exit__(self, exception_type, exception_val, trace):
        self._session.__exit__(exception_type, exception_val, trace)

    def read(self, numBytes, timeout_ms=200):
        return np.array(self._rxFifo.read(numBytes, timeout_ms)[0], dtype=np.uint8)

    def write(self, data, timeout_ms=200):
        self._txFifo.write(data, timeout_ms=timeout_ms)
        

class LineBufferedGFDMPhy(GFDMPhy):
    def __init__(self, rio, packetSize):
        super().__init__(rio)
        self._buffer = ""
        self._packetSize = packetSize
        self._callbacks = []

    def addCallback(self, callback):
        self._callbacks.append(callback)
        
    def run(self, stopEvent=None):
        if stopEvent is None:
            stopEvent = threading.Event()
        while not stopEvent.isSet():
            try:
                data = self.read(self._packetSize)
                for d in data:
                    self._buffer += chr(d)                    
                    if d == 13:
                        for callback in self._callbacks:
                            callback(self, self._buffer)
                        self._buffer = ""

                        
            except nifpga.FifoTimeoutError:
                pass

            
def writeStringToPhy(line, phy):
    line = "\n"*2+line+"\n"
    line = line * 3
    data = [ord(c) for c in line]
    phy.write(data)
    pass
