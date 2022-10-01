def checkSum(dataSegment):
    totCheck = 0
    info = [dataSegment[i: i+16] for i in range(0, len(dataSegment), 16)]
    for y in info:
        totCheck += int(y,2)
        if totCheck >= 65535:
            totCheck -= 65535
    
    
    check = 65535 - totCheck
    checkBits = '{0:016b}'.format(check)
    return checkBits

def checkError(dataSegment):
    totCheck = 0
    info = [dataSegment[i: i+16] for i in range(0, len(dataSegment), 16)]
    for y in info:
        totCheck += int(y,2)
        if totCheck >= 65535:
            totCheck -= 65535
    if totCheck == 0:
        return 1 
    else:
        return 0
    

