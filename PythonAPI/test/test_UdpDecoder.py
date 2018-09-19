import sys

import numpy as np
import numpy.testing as nt

from UdpEncoderDecoder import UdpEncoder, UdpDecoder

def _getPacketsAndDecoder():
    enc = UdpEncoder(udpsize=1316, physize=61)
    data = np.arange(1316, dtype=np.uint8) % 251
    phy_packets = enc.encode(data)

    dec = UdpDecoder(udpsize=1316, physize=61)

    return data, phy_packets, dec

def test_extractsCorrectData_noErrors():
    data, phy_packets, dec = _getPacketsAndDecoder()
    for p in phy_packets[:-1]:
        assert dec.decode(p) is None

    nt.assert_array_equal(dec.decode(phy_packets[-1]), data)

def test_decodesErroneousCounters():
    data, phy_packets, dec = _getPacketsAndDecoder()
    for p in phy_packets[:-1]:
        p[:2] = np.zeros(2)
        assert dec.decode(p) is None

    nt.assert_array_equal(dec.decode(phy_packets[-1]), data)

def test_putsZerosInMissedPackets():
    data, phy_packets, dec = _getPacketsAndDecoder()

    del phy_packets[5]
    payload = [dec.decode(p) for p in phy_packets][-1]
    assert len(payload) == 1316
    nt.assert_array_equal(payload[:100], np.arange(100))
    nt.assert_array_equal(payload[5*(61-7)+np.arange(61-7)], np.zeros(61-7))

def test_startsNewPacketOnNewFrameCounter():
    enc = UdpEncoder(udpsize=1316, physize=61)
    data = np.arange(1316, dtype=np.uint8) % 251
    phy_packets1 = enc.encode(data)
    phy_packets2 = enc.encode(data)

    dec = UdpDecoder(udpsize=1316, physize=61)

    phy_packets1_h = phy_packets1[:10]
    phy_packets2_h = phy_packets2[:10]

    for p in phy_packets1_h:
        assert dec.decode(p) is None
    assert len(dec.decode(phy_packets2_h[0])) == 1316

def _test_packetEncodeDecode_variableSizes(udpsize, physize):
    enc = UdpEncoder(udpsize=udpsize, physize=physize)
    dec = UdpDecoder(udpsize=udpsize, physize=physize)
    txdata = []
    packets = []
    for i in range(32):
        d = np.random.randint(256, size=udpsize).astype(np.uint8)
        packets.extend(enc.encode(d))
        txdata.append(d)

    rxdata = []
    for p in packets:
        rx = dec.decode(p)
        if rx is not None:
            rxdata.append(rx)

    for t, r in zip(txdata, rxdata):
        nt.assert_array_equal(t, r)

def test_packetEncodeDecode_1316_61bytePacket():
    _test_packetEncodeDecode_variableSizes(1316, 61)


def test_packetEncodeDecode_1318_61bytePacket():
    _test_packetEncodeDecode_variableSizes(1318, 61)


def test_packetEncodeDecode_1319_61bytePacket():
    _test_packetEncodeDecode_variableSizes(1319, 61)

def test_packetEncodeDecode_1520_61bytePacket():
    _test_packetEncodeDecode_variableSizes(1520, 61)

def test_packetEncodeDecode_10_61bytePacket():
    _test_packetEncodeDecode_variableSizes(10, 61)
