import sys
sys.path.append(r"C:\Users\admin\Documents\Python\nifpga-python")

import time
import numpy as np
import os
import threading

from nifpga import Session
import nifpga

import argparse

def parseArgs():
    parser = argparse.ArgumentParser(description="Forward the RX data to the TX data")
    parser.add_argument('-s', '--packet-size', type=int, required=True, help='Size of PHY packet in bytes')
    parser.add_argument('--rio', type=str, required=True, help='RIO address e.g. RIO0')
    

    args = parser.parse_args()
    return args.rio, args.packet_size

def forwardFunc(stopEvent, txFifo, rxFifo, packetSize, printIt):
    while not stopEvent.isSet():
        try:
            data, remaining = rxFifo.read(packetSize, timeout_ms=200)
            txFifo.write(data)
            if printIt:
                for d in data:
                    try:
                        sys.stdout.write(chr(d))
                        pass
                    except RuntimeError:
                        pass                   
        except nifpga.FifoTimeoutError:
            pass
    print ("Finishing thread")

def writeStringToFifo(line, fifo):
    line = "\n"*2+line+"\n"
    line = line * 3
    data = [ord(c) for c in line]
    fifo.write(data, timeout_ms=200)
    pass


def main(RIO, packetSize):
    bitfilename = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Builds/GFDM FPGA Toplevel for 40MHz USRP.lvbitx'))
    assert os.path.exists(bitfilename), "Bitfile not found as usual position!"

    rxFifoName = 'Needed Resources.grsc\\RX.Data out.T2H'
    txFifoName = 'Needed Resources.grsc\\TX.data in.H2T'

    with Session(bitfilename, RIO) as session:
        txFifo = session.fifos[txFifoName]
        txFifo.configure(10000000)
        txFifo.start()
        rxFifo = session.fifos[rxFifoName]
        rxFifo.configure(10000000)
        rxFifo.start()
            
        stopEvent = threading.Event()
        try:
            T = threading.Thread(target=forwardFunc, args=(stopEvent, txFifo, rxFifo, packetSize, False))
            T.start()
            print ("Forwarding started. Type to send extra commands.\nType X to exit.")
            for l in sys.stdin:
                l = l.strip()
                if l == 'X':
                    break
                writeStringToFifo(l, txFifo)
            pass
        finally:
            stopEvent.set()
            T.join()
            
                    
if __name__ == '__main__':
    main(*parseArgs())
