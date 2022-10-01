import checksum

class Packet:

    def __init__(self, _type, seqNo, segmentData, sender,dest):
        self.type = _type  # This determines whether the packet is a data packet or acknowledgement 
        self.seqNo = seqNo # Sequence number of the packet
        self.segmentData = segmentData # The data contained in the packet
        self.sender = sender # The sender
        self.dest = dest # The receiver destination

    def decodeLength(self):
        return len(self.segmentData)

    def decodeSeqNo(self):
        seqNo = self.packet[192:200]
        return int(seqNo,2)
        
    def decodeDestAddress(self):
        dest = self.packet[64:128]
        destAddress = int(dest,2)
        return destAddress
    
    def decodeSourceAddress(self):
        source = self.packet[128:192]
        sourceAddress = int(source,2)
        return sourceAddress

    def extractData(self):
        text = ""
        data = self.packet[208:496]
        asciiData = [data[i:i+8] for i in range(0,len(data),8)]
        for letter in asciiData:
            text += chr(int(letter,2))
        return text
    
    
    def checkForError(self):
        return checksum.checkError(self.packet)

    def checkType(self):
        return self.type

    def makePacket(self):
        preamble = '01'*28  # A sequence of alternating 0s and 1s which is 7 bytes long
        sfd = '10101011' # Start frame delimiter
        seqToBits = '{0:08b}'.format(int(self.seqNo))
        destAddress = '{0:064b}'.format(int(self.dest))
        length = len(self.segmentData) 
        lenToBits = '{0:08b}'.format(length)
        sourceAddress = '{0:064b}'.format(int(self.sender))
        data = ""
        
        for i in range(0, len(self.segmentData)):
            character = self.segmentData[i]
            dataByte = '{0:08b}'.format(ord(character))
            data = data + dataByte
        
        packet = preamble + sfd + destAddress + sourceAddress + seqToBits + lenToBits + data    
        ckSum = checksum.checkSum(packet)
        
        packet = packet + ckSum
        
        self.packet = packet
        return self

    def __str__(self):
        return str(self.packet)
    