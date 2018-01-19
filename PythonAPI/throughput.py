import sys
sys.path.append(r"C:\Users\admin\Documents\Python\nifpga-python")

import time
import numpy as np
import os

from nifpga import Session
import nifpga

import argparse

def parseArgs():
    parser = argparse.ArgumentParser(description="Test the throughput of the GFDM PHY")
    parser.add_argument('-s', '--payload-size', type=int, required=True, help='Payload size[BYTE] from the Data panel.')
    parser.add_argument('--rio', type=str, required=True, help='RIO address e.g. RIO0')
    parser.add_argument('-n', '--num-bytes', type=int, default=int(1e5), required=False, help='Number of bytes per burst. The number will be rounded to integer number of PHY packets')

    args = parser.parse_args()
    return args.rio, args.payload_size, args.num_bytes

def main(RIO, basePacketLength, numBytes):
    bitfilename = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Builds/GFDM FPGA Toplevel for 40MHz USRP.lvbitx'))
    assert os.path.exists(bitfilename), "Bitfile not found as usual position!"

    rxFifoName = 'Needed Resources.grsc\\RX.Data out.T2H'
    txFifoName = 'Needed Resources.grsc\\TX.data in.H2T'

#    basePacketLength = 60
    packetLen = int((numBytes//basePacketLength)*basePacketLength)
    #packetLen = 60*100

    with Session(bitfilename, RIO) as session:
        print (session.fifos.keys())

        txFifo = session.fifos[txFifoName]
        txFifo.configure(10000000)
        txFifo.start()
        rxFifo = session.fifos[rxFifoName]
        rxFifo.configure(10000000)
        rxFifo.start()

        while True:
            txData = (256*np.random.rand(packetLen)).astype(np.uint8)

            try:
                start = time.time()
                txFifo.write(txData)
                rxData = np.array(rxFifo.read(packetLen, timeout_ms=1000)[0])
                end = time.time()
                dur = (end-start + 1e-9)
                rate = 8*packetLen/dur * 1e-6
                errors = np.count_nonzero(txData != rxData)
                print ("Transmit %d bytes in %f seconds: %s errors (%.1f MBit/s)" % (packetLen, dur, errors, rate))
            except nifpga.FifoTimeoutError:
                print ("Timeout!")

            time.sleep(0.1)

if __name__ == '__main__':
    main(*parseArgs())
