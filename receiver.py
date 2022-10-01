import multiprocessing

import time
import sys

import checksum
import constants

from packet import *

class Receiver:
    def __init__(self, name, receiverToChannel, channelToReceiver, endTransmission):
        self.name               = name # Name of the receiver
        self.seqNo              = 0 # Initialized to 0 to be in sync with the sender
        self.packetType         = {'data' : 0, 'ack' : 1} # Dictionary to store the type of the packet
        self.senderList         = dict() # Store all the senders sending to a particular receiver
        self.receiverToChannel  = receiverToChannel # Write head of the pipe from Receiver to the Channel
        self.channelToReceiver  = channelToReceiver # Read head of the pipe from Channel to the Receiver
        self.endTransmission    = endTransmission # Flag to denote whether the transmission is complete or not



    # Function to read the file which contains the data for that receiver
    def outputWriteFile(self, filepath):
        try:
            file = open(filepath, 'a+')
        except IOError:
            sys.exit("FILE NON EXISTANT!")

        return file


   

    # Function to get the sequence number of the packet
    def getSequenceNumber(self, packet):
        return packet.decodeSeqNo()




    # Function to send the acknowledgement
    def sendAcknowledgement(self, sender, seqNo):
        packet = Packet(_type=self.packetType['ack'],seqNo=seqNo,segmentData='Acknowledgement Packet',sender=self.name,dest=sender).makePacket()
        
        self.recentACK = packet # To store the current acknowledgement packet so that it can be sent again if needed
        self.receiverToChannel.send(packet)
    
    
    # Resend the last acknowledgement again
    def resendAcknowledgement(self, sender):
        try:
            self.receiverToChannel.send(self.recentACK)
        except AttributeError:
            new_packet = Packet(_type=self.packetType['ack'], seqNo=self.seqNo, segmentData='Acknowledgement Packet', sender=self.name, dest=sender).makePacket()
            self.receiverToChannel.send(new_packet)


   
  
    def startReceiving(self):
        time.sleep(0.4)
        while True:
            print("[RECEIVER {}: ] Listening......".format(self.name+1))
            packet = self.channelToReceiver.recv()
            print("[RECEIVER {}: ] RECEIVED A PACKET.....".format(self.name+1))


            # check for error
            if packet.checkForError():
                print("[RECEIVER {}: ] CHECKED FOR ERRORS.....".format(self.name+1))


                sender = self.getSenderID(packet)
                seqNo = self.getSequenceNumber(packet)


                if self.seqNo == seqNo:
                    # Check if it is a new sender
                    if sender not in self.senderList.keys():
                        self.senderList[sender] = constants.FILE_PATH + 'OutputFile' + str(sender)
                

                    
                    outFile = self.senderList[sender]
                    
                    #Get handle to the file
                    file = self.outputWriteFile(outFile)
                    data = packet.extractData()

                    file.write(data)
                    file.close()

                    #Sequence number goes as 0,1,2,3,0,1,2,3,....
                    self.seqNo = (self.seqNo+1)%constants.WINDOW_SIZE;

                    self.sendAcknowledgement(sender,self.seqNo)
                    print("[RECEIVER {}: ] ACKNOWLEDGEMENT SENT......".format(self.name+1))

                else:
                    # Here, we need to resend the previous acknowledgement
                    self.resendAcknowledgement(sender)
                    print("[RECEIVER {}: ] ACKNOWLEDGEMENT RESENT.......".format(self.name+1))
            else:
                #Packet is corrupted
                self.discardPacket()
                print("[RECEIVER {}: ] CORRUPTED PACKET RECEIVED.......".format(self.name+1))
            
            if self.endTransmission: break
