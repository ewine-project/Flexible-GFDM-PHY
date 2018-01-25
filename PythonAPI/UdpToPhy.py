import sys
import os

import numpy as np
import threading
from threading import Thread
import time

from socket import *

from UdpEncoderDecoder import UdpEncoder, UdpDecoder

from nifpga import Session
import nifpga

import cProfile
import pstats

def enable_thread_profiling():
  '''Monkey-patch Thread.run to enable global profiling.
  
Each thread creates a local profiler; statistics are pooled
to the global stats object on run completion.'''
  Thread.stats = None
  thread_run = Thread.run
  
  def profile_run(self):
    self._prof = cProfile.Profile()
    self._prof.enable()
    thread_run(self)
    self._prof.disable()
    
    if Thread.stats is None:
      Thread.stats = pstats.Stats(self._prof)
    else:
      Thread.stats.add(self._prof)
  
  Thread.run = profile_run
  
def get_thread_stats():
  stats = getattr(Thread, 'stats', None)
  if stats is None:
    raise ValueError('Thread profiling was not enabled,'
                      'or no threads finished running.')
  return stats

def txThread(stopEvent, txFifo, RX_PORT):
    rxSocket = socket(AF_INET, SOCK_DGRAM)
    rxSocket.bind(("localhost", RX_PORT))
    rxSocket.settimeout(0.1)

    enc = UdpEncoder(udpsize=1316, physize=61)
    while not stopEvent.isSet():
        try:
            data, addr = rxSocket.recvfrom(2048)
            payload = np.fromstring(data, dtype=np.uint8)
            packets = enc.encode(payload)
            #            print ("Sending %d bytes in %d packets..." % (len(payload), len(packets)))

            X = np.hstack(packets).astype(np.uint8)
            #        print(X.shape)
            p = (np.random.rand(len(X)) * 256).astype(np.uint8)
            txFifo.write(X)
        except OSError as e:
            pass
        #        txFifo.write(np.hstack(packets))
#        for p in packets:
#            txFifo.write(p)
#            time.sleep(0.01)

def rxThread(stopEvent, rxFifo, TX_PORT):
    txSocket = socket(AF_INET, SOCK_DGRAM)
    dec = UdpDecoder(udpsize=1316, physize=61)
    count = 0
    while not stopEvent.isSet():
        try:
            data, rem = rxFifo.read(61, timeout_ms=500)
            count = count + 1
            if count % 10 == 0:
                print ("Remaining:", rem)
            packet = dec.decode(np.array(data, dtype=np.uint8))
            if packet is not None:
                #                print ("TX sck")
                txSocket.sendto(packet, ("127.0.0.1", TX_PORT))
        except nifpga.FifoTimeoutError:
            dec.reset()
            pass

def main(RIO, RX_PORT, TX_PORT):
    profiling = False
    if profiling:
        enable_thread_profiling()
    
    bitfilename = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Builds/GFDM FPGA Toplevel for 40MHz USRP.lvbitx'))
    assert os.path.exists(bitfilename), "Bitfile not found as usual position!"

    rxFifoName = 'Needed Resources.grsc\\RX.Data out.T2H'
    txFifoName = 'Needed Resources.grsc\\TX.data in.H2T'

    with Session(bitfilename, RIO) as session:
        try:
            txFifo = session.fifos[txFifoName]
            txFifo.configure(10000000)
            txFifo.start()
            rxFifo = session.fifos[rxFifoName]
            rxFifo.configure(10000000)
            rxFifo.start()

            stopEvent = threading.Event()            
            TX = threading.Thread(target=txThread, args=(stopEvent, txFifo, RX_PORT))
            TX.start()
            RX = threading.Thread(target=rxThread, args=(stopEvent, rxFifo, TX_PORT))        
            RX.start()

            while True:
                time.sleep(0.1)
        finally:
            stopEvent.set()
            TX.join()
            RX.join()
            if profiling:
                get_thread_stats().dump_stats(filename='profile2.prof')


if __name__ == '__main__':
    main("RIO0", RX_PORT=50000, TX_PORT=60000)
    
