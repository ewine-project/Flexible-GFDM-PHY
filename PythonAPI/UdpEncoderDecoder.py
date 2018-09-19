import sys
import numpy as np

def _int2bin(N, L):
    result = []
    for i in range(L):
        result.append((N & 2**i) != 0)
    return np.array(result, dtype=np.uint8)

def _bin2int(C):
    result = 0
    for i, b in enumerate(C):
        assert b in (0,1)
        result += b * 2**i
    return result

class UdpEncoder(object):
    def __init__(self, udpsize, physize):
        self._physize = physize
        self._udpsize = udpsize
        self._splitAt = physize // 2

        self._overhead = 7

        self._numPhyPackets = int(np.ceil((udpsize / (physize-self._overhead))))
        self._frameNumber = 0

    def encode(self, data):
        assert len(data) == self._udpsize

        result = []
        dataIndex = 0
        for i in range(self._numPhyPackets):
            block = np.zeros(self._physize, dtype=np.uint8)
            C = self._encodeCounter(frameNumber=self._frameNumber, blockNumber=i)
            block[:2] = C
            block[self._splitAt+np.arange(2)] = C
            block[-3:-1] = C

            L1 = min(self._splitAt - 2, len(data))
            D = data[:L1]; data = data[L1:]
            block[2+np.arange(L1)] = D

            L2 = min(self._physize - 3 - self._splitAt - 2, len(data))
            D = data[:L2]; data = data[L2:]            
            block[self._splitAt+2+np.arange(L2)] = D

            result.append(block)

        self._frameNumber = (self._frameNumber + 1) % 8
        return result

    def _encodeCounter(self, frameNumber, blockNumber):
        frameBits = _int2bin(frameNumber, 3)
        blockBits = _int2bin(blockNumber, 5)

        joined = np.hstack([frameBits, blockBits])
        double = np.vstack([joined, joined]).flatten(order='F')

        return np.array([_bin2int(double[:8]), _bin2int(double[8:])])

class UdpDecoder(object):
    def __init__(self, udpsize, physize):
        self._physize = physize
        self._udpsize = udpsize
        self._splitAt = physize // 2
        self._overhead = 7

        self._numPhyPackets = int(np.ceil((udpsize / (physize-self._overhead))))
        self.reset()

    def reset(self):
        self._lastFrameNumber = 0
        self._lastBlockNumber = 0

        self._payloads = [np.zeros(self._physize - self._overhead, dtype=np.uint8) for i in range(self._numPhyPackets)]        

    def decode(self, phypacket):
        currFrame, currBlock = self._decodeCounter(phypacket)
        if 0 <= currBlock < len(self._payloads):
            self._payloads[currBlock] = self._extractPayload(phypacket)
        else:
            pass

        needsReset = False
#        print ("Current block", currBlock, currFrame)
        if currBlock + 1 == self._numPhyPackets:
            print ("Correct reset!")
            needsReset = True
        elif (self._lastFrameNumber != currFrame and
              self._lastBlockNumber > currBlock):
            print ("Erroneous reset", self._lastFrameNumber, currFrame, self._lastBlockNumber, currBlock)
            needsReset = True

        self._lastFrameNumber = currFrame
        self._lastBlockNumber = currBlock

        if needsReset:
            payload = np.hstack(self._payloads)[:self._udpsize]
            self.reset()
            return payload
        else:
            return None

    def _extractPayload(self, packet):
        part1 = packet[2:self._splitAt]
        part2 = packet[self._splitAt+2:-3]
        return np.hstack([part1, part2])            

    def _decodeCounter(self, phypacket):
#        counter1 = phypacket[:2]
#        counter2 = phypacket[self._splitAt+np.arange(2)]
        counter3 = phypacket[-3:-1]

#        dec1 = self._decodeSingleCounter(counter1)
#        dec2 = self._decodeSingleCounter(counter2)
        dec3 = self._decodeSingleCounter(counter3)

#        dec = ((dec1 + dec2 + dec3) / 6) > 0.5
        dec = (dec3 / 2) > 0.5
        decFrame = dec[:3]
        decBlock = dec[3:]

        return _bin2int(decFrame), _bin2int(decBlock)

    def _decodeSingleCounter(self, bytes):
        byte1 = bytes[0]; bits1 = _int2bin(byte1, 8)
        byte2 = bytes[1]; bits2 = _int2bin(byte2, 8)

        bits = np.hstack([bits1, bits2])
        bitsR = bits.reshape((8,2))
        return bitsR.sum(axis=1)

        
            

            

        
