import socket
import datetime
import sys
import os
import time

def getTime():
    return datetime.datetime.now()

socketOn = False
RESOLUTION = 5
members = []
relativeCoordinates = []
targetCoordinates = []

hostname = socket.gethostname()
localIp = socket.gethostbyname(hostname)

if len(sys.argv) < 2:
    print("Invalid argument count, atleast one parameter should be given.")
    exit()

def roundTo(num, base):
    return num - (num % base)

groundAddress = sys.argv[1]

def triangleFormation(x, y, z):

    inputFile = open("inputFile", "w")

    inputFile.write(f"clear")

    inputFile.close()

    time.sleep(1)


    offset = 1
    print(str(getTime()) +  f"Size of usedNodeFile: {os.path.getsize("usedNodeFile")}\n")
    f = open('usedNodeFile', 'r+')
    f.truncate(0) # need '0' when using r+

    
    print(str(getTime()) +  f"Size of usedNodeFile: {os.path.getsize("usedNodeFile")}\n")

    startFile = open("startNodes", "w")

    for i in range(0, len(relativeCoordinates)-1):
        startFile.write(f"{relativeCoordinates[i][0]} {relativeCoordinates[i][1]} {relativeCoordinates[i][2]}\n")

    startFile.close()

    for member in members: # havada olan her bir drone'a bağlanacağız
        tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tempSocket.connect(member) 

            tempMsg = "REPORTRELATIONALCOORDINATE" # XYZ koordinatlarını almak için gönderdiğimiz komut
            tempSocket.send(tempMsg.encode("utf-8"))

            tempMsg = None

            while not tempMsg: # mesaj gelene kadar bekliyoruz
                tempMsg = tempSocket.recv(1024).decode("utf-8")


            tempArr = tempMsg.split(';') # gelen veriyi bölüyoruz

            # gelen her koordinatı, havadaki drone'ların adreslerinin kayıtlı olduğu dizedeki sırayı
            # koruyacak şekilde diziye ekliyoruz
            relativeCoordinates.append((float(tempArr[0]), float(tempArr[1]), float(tempArr[2]))) 

        except:
            print(str(getTime()) +  f": Error while getting relative coordinates: {member}\n")
        finally:
            tempSocket.close()

        # Geçiçi kod, buraya asıl gidilecek hedef koordinatları hesaplamak için algoritma yazılacak
        if member == localIp:
            targetCoordinates.append((float(x),float(y),float(z)))
        else:
            targetCoordinates.append((float(x)-3,float(y),float(z)-2*offset))
            offset = offset * -1

    

    
        

    for i in range(0, len(members)-1):
        print(i)
        print(str(getTime()) +  f": Current coordinates of {members[i]}:  X -> {relativeCoordinates[i][0]}, Y -> {relativeCoordinates[i][1]}, Z -> {relativeCoordinates[i][2]}\n")
        print(str(getTime()) +  f": Rounded coordinates of {members[i]}:  X -> {roundTo(relativeCoordinates[i][0], RESOLUTION)}, Y -> {roundTo(relativeCoordinates[i][1], RESOLUTION)}, Z -> {roundTo(relativeCoordinates[i][2], RESOLUTION)}\n")
        
        print(str(getTime()) +  f": Target coordinates of {members[i]}:  X -> {targetCoordinates[i][0]}, Y -> {targetCoordinates[i][1]}, Z -> {targetCoordinates[i][2]}\n")
        open("waySave", "w").close() # kullanılacak yol dosyası temizleniyor. Önceden içinde bir şey olmadığından
        # emin oluyoruz.

        inputFile = open("inputFile", "w")

        inputFile.write(f"{roundTo(relativeCoordinates[i][0], RESOLUTION)} {roundTo(relativeCoordinates[i][1], RESOLUTION)} {roundTo(relativeCoordinates[i][2], RESOLUTION)} {targetCoordinates[i][0]} {targetCoordinates[i][1]} {targetCoordinates[i][2]} 1")
        # dron'un şuanki koordinatını ve gideceği yerin koordinatlarını, yol bulan programa veriyoruz. Sondaki 1, bulunan yolun, sonrasında bulucank yollar ile çakışmaması için kenara kaydetmesini söylüyor.

        inputFile.close()
    
        wayFile = open("waySave", "r")
        
        


        while os.path.getsize("inputFile"):
            continue

        way = wayFile.read() # bulunan yolu dosyadan okuyoruz

        wayFile.close()

        print(str(getTime()) +  f": Found way for {members[i]}\n")
        memberSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mSocket = False
        
        try:
            memberSocket.connect(member)
            mSocket = True
            msg = f"GOTO;{way}" 

            memberSocket.send(msg.encode("utf-8"))
        except:
            print(str(getTime()) +  f": Error occured while transmiting task to: {member}\n")
        finally:
            if mSocket:
                memberSocket.close()

        






s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 4350))
s.listen()


while True:
    sock, addr = s.accept()
    socketOn = True

    print(str(getTime()) +  f": New connection recieved from: {sock.getpeername()}\n")

    try:
        


        msg = sock.recv(1024).decode("utf-8")
        msgArray = msg.split(';')

        if msgArray[0] == "TASK": # havada olan dron listesine gelen adresteki dronu ekliyoruz
            print(str(getTime()) +  f": New task request recieved from {sock.getpeername()}\n")
            taskType = msgArray[1]
            x = msgArray[2]
            y = msgArray[3]
            z = msgArray[4]
            print(str(getTime()) +  f": Task Details: Type -> {taskType}\n")
            print(str(getTime()) +  f": Task Details: X -> {x}, Y -> {y}, Z -> {z} \n")
            sock.close()
            socketOn = False
            groundSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            groundSocket.connect((groundAddress, 2350))
            tempMsg = "LISTMEMBERS"
            groundSocket.send(tempMsg.encode("utf-8"))

            tempMsg = None

            while not tempMsg:
                tempMsg = groundSocket.recv(1024).decode("utf-8")
        
            groundSocket.close()
            tempList = tempMsg.split(';')

            members.clear()

            for member in tempList:
                t = member.split('-')
                members.append((t[0], int(t[1])))

            if taskType == "TRIANGLE":
                triangleFormation(float(x),float(y),float(z))
                


        
    
    except:
        print(str(getTime()) +  f": Connection error from: {sock.getpeername()}\n")
        
        continue
    finally:
        if socketOn:
            print(str(getTime()) +  f": Connection closed from: {sock.getpeername()}\n")
            sock.close()
