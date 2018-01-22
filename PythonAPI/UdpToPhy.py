import sys
import os
sys.path.append(r"C:\Users\admin\Documents\Python\nifpga-python")

import numpy as np
import threading
import time

from socket import *

from UdpEncoderDecoder import UdpEncoder, UdpDecoder

from nifpga import Session
import nifpga


def txThread(txFifo, RX_PORT):
    rxSocket = socket(AF_INET, SOCK_DGRAM)
    rxSocket.bind(("localhost", RX_PORT))

    enc = UdpEncoder(udpsize=1316, physize=61)
    while True:
        data, addr = rxSocket.recvfrom(2048)
        payload = np.fromstring(data, dtype=np.uint8)
        packets = enc.encode(payload)
#        print ("Sending %d bytes in %d packets..." % (len(payload), len(packets)))

        X = np.hstack(packets).astype(np.uint8)
#        print(X.shape)
        p = (np.random.rand(len(X)) * 256).astype(np.uint8)
        txFifo.write(X)
#        txFifo.write(np.hstack(packets))
#        for p in packets:
#            txFifo.write(p)
#            time.sleep(0.01)

def rxThread(rxFifo, TX_PORT):
    txSocket = socket(AF_INET, SOCK_DGRAM)
    dec = UdpDecoder(udpsize=1316, physize=61)

    while True:
        try:
            data = rxFifo.read(61, timeout_ms=500)[0]
            packet = dec.decode(np.array(data, dtype=np.uint8))
            if packet is not None:
                print ("TX sck")
                txSocket.sendto(packet, ("127.0.0.1", TX_PORT))
        except nifpga.FifoTimeoutError:
            dec.reset()
            pass

def main(RIO, RX_PORT, TX_PORT):
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

        TX = threading.Thread(target=txThread, args=(txFifo, RX_PORT))
        TX.daemon = True
        TX.start()
        RX = threading.Thread(target=rxThread, args=(rxFifo, TX_PORT))        
        RX.daemon = True
        RX.start()
        
        while True:
            time.sleep(0.1)

if __name__ == '__main__':
    main("RIO0", RX_PORT=50000, TX_PORT=60000)
    
