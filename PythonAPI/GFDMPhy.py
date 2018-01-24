import sys
import os
import numpy as np

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
        
