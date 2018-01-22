import sys
sys.path.append(r"C:\Users\admin\Documents\Python\nifpga-python")

import time
import numpy as np
import os

from nifpga import Session
import nifpga

import argparse

def parseArgs():
    parser = argparse.ArgumentParser(description="Forward the RX data to the TX data")
    parser.add_argument('-s', '--packet-size', type=int, required=True, help='Size of PHY packet in bytes')
    parser.add_argument('--rio', type=str, required=True, help='RIO address e.g. RIO0')
    

    args = parser.parse_args()
    return args.rio, args.packet_size


    

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

            while True:
                try:
                    data, remaining = rxFifo.read(packetSize, timeout_ms=200)
                    for d in data:
                        try:
                            sys.stdout.write(chr(d))
                        except RuntimeError:
                            pass
                    
                    txFifo.write(data)
                except nifpga.FifoTimeoutError:
                    pass
                    
if __name__ == '__main__':
    main(*parseArgs())
