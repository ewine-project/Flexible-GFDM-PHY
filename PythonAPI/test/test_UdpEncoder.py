import numpy as np
import numpy.testing as nt

from UdpEncoderDecoder import UdpEncoder

def test_numberOfPackets():
    enc = UdpEncoder(udpsize=1316, physize=61)
    phy_packets = enc.encode(np.zeros(1316))

    # 7 overhead for counters
    assert len(phy_packets) == (1316//(61-7)) + 1

def test_addsFrameCounterToBeginningMidAndEnd():
    enc = UdpEncoder(udpsize=1316, physize=61)
    phy_packets = enc.encode(np.zeros(1316))
    
    for i, p in enumerate(phy_packets):
        C = enc._encodeCounter(frameNumber=0, blockNumber=i)
        nt.assert_array_equal(p[:2], C)
        nt.assert_array_equal(p[30:32], C)
        nt.assert_array_equal(p[58:60], C)

def test_increasesFrameCounter():
    enc = UdpEncoder(udpsize=1316, physize=61)
    for i in range(5):
        dummy = enc.encode(np.zeros(1316))  # 5 dummy packet

    phy_packets = enc.encode(np.zeros(1316))    # 6th packet
    nt.assert_array_equal(phy_packets[0][:2],
                          enc._encodeCounter(frameNumber=5, blockNumber=0))

def test_correctlyPutsData():
    enc = UdpEncoder(udpsize=1316, physize=61)
    data = np.arange(1316) % 256
    phy_packets = enc.encode(data)

    payloads = []
    for p in phy_packets:
        payloads.append(p[2:30])
        payloads.append(p[32:58])
    P = np.hstack(payloads)
    nt.assert_array_equal(data, P[:len(data)])
    nt.assert_array_equal(P[len(data):], np.zeros(len(P) - len(data)))


def test_encodeCounter():
    enc = UdpEncoder(udpsize=1316, physize=61)

    nt.assert_array_equal(enc._encodeCounter(frameNumber=0,blockNumber=0),
                          np.zeros(2))

    nt.assert_array_equal(enc._encodeCounter(frameNumber=0,blockNumber=1),
                          np.array([192,0]))    

    nt.assert_array_equal(enc._encodeCounter(frameNumber=2,blockNumber=5),
                          np.array([204,12]))    

    nt.assert_array_equal(enc._encodeCounter(frameNumber=6,blockNumber=18),
                          np.array([60,195]))    

    nt.assert_array_equal(enc._encodeCounter(frameNumber=9,blockNumber=18),
                          np.array([3,195]))    

    nt.assert_array_equal(enc._encodeCounter(frameNumber=9,blockNumber=62),
                          np.array([3,255]))    
    
