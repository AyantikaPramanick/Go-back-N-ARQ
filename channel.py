import multiprocessing
import threading

import checksum
from packet import *
import constants

import time
import random

class Channel:
    def __init__(self, name, senderToChannel, channelToSender, receiverToChannel, channelToReceiver): 
        
        self.name               = name  # Name of the channel (0 by default)
        self.senderToChannel    = senderToChannel # Read head of the Sender to Channel pipe
        self.channelToSender    = channelToSender # Write head of the Channel to Sender pipe
        self.receiverToChannel  = receiverToChannel # Read head of the Receiver to Channel pipe
        self.channelToReceiver  = channelToReceiver # Write head of the Channel to Receiver pipe

    # Add random number of errors in random positions
    def injectError(self, packet):

        numError = random.randint(0, 50)
        charList = list(packet.packet)
        length = packet.decodeLength()

        for i in range(numError):
            position = random.randint(0, length-1)

            if charList[position] == '1': 
                charList[position] = '0'
            else: 
                charList[position] = '1'
            
        packet.packet = ''.join(charList)

    # Channelize the packet from the sender to the receiver
    def channelS2R(self,sender):
        time.sleep(0.5)
        while True:    
            print("[CHANNEL: ] The channel is listening.....................")
            packet = self.senderToChannel[sender].recv() #Here sender variable stores which sender (0,1,2,...)
            receiver = packet.decodeDestAddress()

            #Drop the packet based on a probability
            if random.random() <= constants.DROPOUT_PROBABILITY:
                print("[CHANNEL: ] OH NO! THE PACKET IS DROPPED........")
                self.dropPacket()
            else:

                #Add errors based on a probability
                if random.random() <= constants.ERROR_PROBABILITY:
                    print("[CHANNEL: ] ERROR IS BEING INJECTED........")
                    self.injectError(packet)

                #Introduce delay based on a probability
                if random.random() <= constants.DELAY_PROBABILITY:
                    print("[CHANNEL: ] DELAY IS BEING INTRODUCED......")                        
                    time.sleep(constants.DELAY_DURATION)
                    
                self.channelToReceiver[receiver].send(packet)

    # Channelize the acknowledgement packet from the receiver to the sender
    def channelR2S(self, receiver): 
        time.sleep(0.5)
        while True:
            print("[CHANNEL: ] The channel is listening.....................")
            ack = self.receiverToChannel[receiver].recv() #Here receiver variable stores which receiver (0,1,2,....)
            sender = ack.decodeDestAddress()

            #Drop the packet based on a probability
            if random.random() <= constants.DROPOUT_PROBABILITY:
                print("[CHANNEL: ] OH NO! THE ACKNOWLEDGEMENT PACKET IS DROPPED........")
                self.dropPacket()
            
            else:
                #Add errors based on a probability
                if random.random() <= constants.ERROR_PROBABILITY:
                    print("[CHANNEL: ] ERROR IS BEING INJECTED IN THE ACKNOWLEDGEMENT........")
                    self.injectError(ack)

                #Introduce delay based on a probability
                if random.random() <= constants.DELAY_PROBABILITY:
                    print("[CHANNEL: ] DELAY IS BEING INTRODUCED IN THE ACKNOWLEDGEMENT......")                        
                    time.sleep(constants.DELAY_DURATION)
    
                self.channelToSender[sender].send(ack)

    def startChannel(self):

        #Lists to store threads from sender to receiver and vice versa
        S2RTList = []
        R2STList = []

        s_count = 0 #To store the sequence of the sender
        r_count = 0 #To store the sequence of the receiver

        for i in range(constants.TOT_SENDER):
            t = threading.Thread(name= 'PacketThread'+str(s_count+1), target=self.channelS2R, args=(s_count,))
            S2RTList.append(t)
            s_count += 1
            
        for i in range(constants.TOT_RECEIVER):
            t = threading.Thread(name= 'AcknowledgementThread'+str(r_count+1), target=self.channelR2S, args=(r_count,))
            R2STList.append(t)
            r_count += 1

        
        #Start all the threads
        for thread in S2RTList:
            thread.start()
            
        for thread in R2STList:
            thread.start()

    
        for thread in S2RTList:
            thread.join()
            
        for thread in R2STList:
            thread.join()


    def dropPacket(self):
        return 0;


            

