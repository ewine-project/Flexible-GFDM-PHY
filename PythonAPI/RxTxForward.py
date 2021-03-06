import sys

import time
import numpy as np
import os
import threading

from nifpga import Session
import nifpga

import argparse

from GFDMPhy import GFDMPhy

def parseArgs():
    parser = argparse.ArgumentParser(description="Forward the RX data to the TX data")
    parser.add_argument('-s', '--packet-size', type=int, required=True, help='Size of PHY packet in bytes')
    parser.add_argument('--rio', type=str, required=True, help='RIO address e.g. RIO0')
    

    args = parser.parse_args()
    return args.rio, args.packet_size

def forwardFunc(stopEvent, phy, packetSize, printIt):
    while not stopEvent.isSet():
        try:
            data = phy.read(packetSize)
            phy.write(data)
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

def main(RIO, packetSize):
    with GFDMPhy(RIO) as phy:
        stopEvent = threading.Event()
        try:
            T = threading.Thread(target=forwardFunc, args=(stopEvent,phy,packetSize,True))
            T.start()

            print ("Forwarding started.\nType X to exit.")
            for line in sys.stdin:
                line = line.strip()
                if line == 'X':
                    break
        finally:
            stopEvent.set()
            T.join()
            
                    
if __name__ == '__main__':
    main(*parseArgs())
