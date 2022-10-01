import multiprocessing

from sender import *
from channel import *
from receiver import *

import constants


def execute():

    print("!---------------------------------------------------------------------------------------------------------!")
    print("!---------------------------------GO BACK N PROTOCOL IMPLEMENTATION-----------------------------------!")
    print("NETWORK CONFIGURATION:")
    print("TOTAL NUMBER OF SENDERS: {}".format(constants.TOT_SENDER))
    print("TOTAL NUMBER OF RECEIVERS: {}".format(constants.TOT_RECEIVER))
    print("!---------------------------------------------------------------------------------------------------------!")

    #Pipes from sender to the channel
    WHOS2CP = []
    RHOS2CP = []

    #Pipes from channel to the sender
    WHOC2SP = []
    RHOC2SP = []


    #Pipes from channel to the receiver
    WHOC2RP = []
    RHOC2RP = []

    #Pipes from receiver to the channel
    WHOR2CP = []
    RHOR2CP = []

    for i in range(constants.TOT_SENDER):
        readHead, writeHead = multiprocessing.Pipe()
        WHOS2CP.append(writeHead) 
        RHOS2CP.append(readHead) 

        readHead, writeHead = multiprocessing.Pipe()
        WHOC2SP.append(writeHead)
        RHOC2SP.append(readHead)

    for i in range(constants.TOT_RECEIVER):
        readHead, writeHead = multiprocessing.Pipe()
        WHOC2RP.append(writeHead) 
        RHOC2RP.append(readHead) 

        readHead, writeHead = multiprocessing.Pipe()
        WHOR2CP.append(writeHead) 
        RHOR2CP.append(readHead) 


    
    senderList = []
    receiverList = []

    
    
    #Create a list of the receivers
    for i in range(constants.TOT_RECEIVER):
        receiver = Receiver( i, WHOR2CP[i], RHOC2RP[i], False)
        receiverList.append(receiver)
    

    #Create the channel process
    channel = Channel( 0, RHOS2CP, WHOC2SP, RHOR2CP, WHOC2RP)


    #Start of multiprocessing

    senderProcess = []
    receiverProcess = []

    #Creating a list of all the sender processes
    for i in range(len(senderList)):
        p = multiprocessing.Process(target=senderList[i].startSending)
        senderProcess.append(p)
    

    #Creating a list of all the receiver processes
    for i in range(len(receiverList)):
        p = multiprocessing.Process(target=receiverList[i].startReceiving)
        receiverProcess.append(p)
    
    #Store the channel process
    channelProcess = multiprocessing.Process(target= channel.startChannel)


    #Start the processes in the order: SENDER ---> CHANNEL ---> RECEIVER

    for i in senderProcess:
        i.start()
    
    channelProcess.start()

    for i in receiverProcess:
        i.start()

    for i in senderProcess:
        i.join()
    
    channelProcess.join()

    for i in receiverProcess:
        i.join()

