import multiprocessing
import threading

import random
import time
import sys

import checksum
import constants
from packet import *


class Sender:
    def __init__(self, name, fileName, senderToChannel, channelToSender): 
        self.name               = name # Name of the sender process
        self.fileName           = fileName # File from where packets is to be generated
        self.senderToChannel    = senderToChannel # Write head of the Sender to Channel pipe
        self.channelToSender    = channelToSender # Read of the Channel to Sender pipe
        self.packetType         = {'data' : 0, 'ack' : 1} # Defines the packet type
        self.dest               = self.chooseReceiverNumber() # Receiver node address
        self.seqNo              = 0 # Seqeunce number of the packet to be sent (0,1,0,1....)
        self.timeoutEvent       = threading.Event() # Needed for the timeout implementation
        self.endTransmission    = False # FLag to mark end of transmission
        self.receivedAck        = False # Flag to mark whether acknowledgement is received successfully
        self.packetQueue        = [] # To store the sequence of data frames transmitted



    #Function to choose the receiver for the current sender
    def chooseReceiverNumber(self):
        rec = 0 
        while(1):
            rec=int(input("Select a receiver for Sender {}: ".format(self.name+1)))

            if(rec>constants.TOT_RECEIVER or rec<=0):
                print("RECEIVER DOES NOT EXIST, PLEASE SELECT A VALID RECEIVER")
            else:
                rec = rec - 1
                break
        return rec

        
    
    def checkAcknowledgement(self):
        time.sleep(0.1)
        while True:
            
            #Keep receiving packets till end of transmission is set true
            if not self.endTransmission: 
                packet = self.channelToSender.recv()
            else: 
                break
                
            #Check if it is an acknowledgement packet
            if packet.type == 1:
                if packet.checkForError():
                    if packet.seqNo == self.seqNo:
                        self.timeoutEvent.set()
                        print("[SENDER {}: ] THE LAST PACKET HAS BEEN SUCCESSFULLY RECEIVED AND ACKNOWLEDGED......".format(self.name+1))
                    else: 
                        self.timeoutEvent.clear()
                else:
                    self.timeoutEvent.clear()
            else: 
                self.timeoutEvent.clear()
            



    def sendPackets(self):
        time.sleep(0.1)
        start_time = time.time()
        print("!----------------------------------------------------------------------------------!")
        print("SENDER {} STARTS TRANSMISSION TO RECEIVER {}".format(self.name+1, self.dest+1))
        print("!----------------------------------------------------------------------------------!")
        
        file = self.openFile(self.fileName)
        byte = file.read(constants.DATA_PACK_SIZE)

        self.seqNo = 0
        countPackets = 0
        countTotalPackets = 0

        while len(self.packetQueue) < constants.WINDOW_SIZE:
            packet = Packet(self.packetType['data'], self.seqNo, byte, self.name, self.dest).makePacket()

            self.packetQueue.append(packet)
            self.senderToChannel.send(packet)

            self.seqNo = (self.seqNo + 1) % constants.WINDOW_SIZE

            countPackets += 1
            countTotalPackets += 1
            print("[SENDER {}: ] PACKET {} HAS BEEN SUCCESSFULLY TRANSMITTED.......".format(self.name+1, countPackets))

            byte = file.read(constants.DATA_PACK_SIZE)

            #Check if the last frame is smaller than the standard data packet size
            if len(byte) < constants.DATA_PACK_SIZE: 
                currentLength = len(byte)
                for i in range(constants.DATA_PACK_SIZE - currentLength):
                    byte = byte + '\0'


        while True: 
            time.sleep(0.2)
            self.timeoutEvent.wait(constants.SENDER_TIMEOUT)

            #Check if the entire window needs to be re-sent
            if (not self.timeoutEvent.isSet()) and (len(self.packetQueue) > 0):           
                for i in range (0, len(self.packetQueue)):
                    self.senderToChannel.send(self.packetQueue[i])
                    self.seqNo = (self.seqNo + 1) % constants.WINDOW_SIZE
                    print("[SENDER {}: ] PACKET {} HAS BEEN RE-TRANSMITTED........".format(self.name+1, countPackets - len(self.packetQueue)+ i + 1))
                    countTotalPackets += 1

            #Check if there exists more packets which needs to be transmitted 
            elif len(self.packetQueue) > 0: 
                if byte:
                    packet = Packet(self.packetType['data'], self.seqNo, byte, self.name, self.dest).makePacket()
                    self.packetQueue.append(packet)
                    countPackets += 1
                    countTotalPackets += 1
                    print("[SENDER {}: ] PACKET {} HAS BEEN SUCCESSFULLY TRANSMITTED.......".format(self.name+1, countPackets))
                    self.senderToChannel.send(self.packetQueue[len(self.packetQueue)-1])
                    self.seqNo = (self.seqNo + 1) % constants.WINDOW_SIZE
                    
                self.packetQueue.pop(0)
                time.sleep(0.1)
                self.timeoutEvent.clear()
                byte = file.read(constants.DATA_PACK_SIZE)
                if len(byte) == 0: 
                    continue
                elif len(byte) < constants.DATA_PACK_SIZE: 
                    currentLength = len(byte)
                    for i in range(constants.DATA_PACK_SIZE - currentLength):
                        byte = byte + '\0'
        
            else: 
                break


        #Now mark the end of the transmission as true
        self.endTransmission = True 
        file.close()

        self.timeoutEvent.clear()

        total_time = time.time() - start_time
        averageRoundTime = total_time/countTotalPackets
        print("[SENDER {}: ] THE FINAL PACKET HAS BEEN SUCCESSFULLY RECEIVED AND ACKNOWLEDGED......".format(self.name+1))
        print("!---------------------------------SHOW STATS------------------------------------------!")
        print("\n______________________SENDER {}_________________________".format(self.name+1))
        print("\nTOTAL PACKETS SENT: {}\nTOTAL PACKETS REQUIRED FOR THE ENTIRE TRANSMISSION: {}\nTIME REQUIRED FOR THE ENTIRE TRANSMISSION: {}\nAVERAGE ROUND TRIP TIME FOR A PACKET: {}".format(countPackets, countTotalPackets,total_time,averageRoundTime))
        print("\n!-------------------------------------------------------------------------------------!")


    


