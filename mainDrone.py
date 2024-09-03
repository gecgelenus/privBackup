import socket
import datetime
import sys
import os
import time

def getTime():
    return datetime.datetime.now()

class Formation:
    def __init__(self, x, y, z, droneSayisi, yukseklik, aralarindakiMesafe, formation_type):
        self.home_x = x
        self.home_y = y
        self.home_z = z
        self.droneSayisi = droneSayisi
        self.yukseklik = yukseklik
        self.aralarindakiMesafe = aralarindakiMesafe
        self.formation_type = formation_type
        self.formation = []
        print(f"Formasyon: {self.droneSayisi} drone, yükseklik: {self.yukseklik}, aralarındaki mesafe: {self.aralarindakiMesafe} ve formasyon tipi: {self.formation_type}") 


    def lineFormation(self):
        formation = []
        for i in range(self.droneSayisi):
            formation.append([self.home_x + i * self.aralarindakiMesafe, self.yukseklik, self.home_z])
        return formation

    

    def VFormation(self):
        formation = []
        middle_index = self.droneSayisi // 2  # Ortadaki drone'un indeksi
        for i in range(self.droneSayisi):
            dx = (i - middle_index) * self.aralarindakiMesafe / 2
            dy = abs(i - middle_index) * self.aralarindakiMesafe        
            # Ortaya yakın dronelar merkezde, uçlara doğru ilerliyor
            formation.append([self.home_x + dx, self.home_y - dy, self.yukseklik])
        return formation

    def arrowFormation(self):# HATALI ÇALIŞIYOR!!!
        formation = []
        for i in range(self.droneSayisi):
            formation.append([self.home_x + i * self.aralarindakiMesafe, self.home_y + i * self.aralarindakiMesafe, self.yukseklik])
        return formation

    
    def create_formation(self, formation_type):
        if formation_type == "line":
            self.formation = self.lineFormation()
        elif formation_type == "V":
            self.formation = self.VFormation()
        elif formation_type == "arrow":
            self.formation = self.arrowFormation()
        else:
            raise ValueError(f"Bilinmeyen formasyon türü: {formation_type}")
    
    def get_formation(self):
        return self.formation


socketOn = False
RESOLUTION = 2
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
orijin_lat = sys.argv[2]
orijin_lon = sys.argv[3]
orijin_alt = sys.argv[4]

def triangleFormation(x, y, z):

    inputFile = open("inputFile", "w")

    inputFile.write(f"clear")

    inputFile.close()

    time.sleep(1)


    offset = 1
    size = os.path.getsize("usedNodeFile")

    offset = 1
    print(str(getTime()) +  f"Size of usedNodeFile: {size}\n")
    f = open('usedNodeFile', 'r+')
    f.truncate(0) # need '0' when using r+

    size = os.path.getsize("usedNodeFile")
    
    print(str(getTime()) +  f"Size of usedNodeFile: {size}\n")

   
    for member in members: # havada olan her bir drone'a bağlanacağız
        tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tempSocket.connect((member, 3350)) 

            tempMsg = f"REPORTRELATIONALCOORDINATE;{orijin_lat};{orijin_lon};{orijin_alt}" # XYZ koordinatlarını almak için gönderdiğimiz komut
            tempSocket.send(tempMsg.encode("utf-8"))

            tempMsg = None

            while not tempMsg: # mesaj gelene kadar bekliyoruz
                tempMsg = tempSocket.recv(1024).decode("utf-8")


            tempArr = tempMsg.split(';') # gelen veriyi bölüyoruz

            # gelen her koordinatı, havadaki drone'ların adreslerinin kayıtlı olduğu dizedeki sırayı
            # koruyacak şekilde diziye ekliyoruz
            relativeCoordinates.append((float(tempArr[0]), float(tempArr[1]), float(tempArr[2]))) 

        except Exception as ex:
            print(str(getTime()) +  f": Error while getting relative coordinates: {member}\n")
        finally:
            tempSocket.close()

            startFile = open("startNodes", "w")

        for i in range(0, len(relativeCoordinates)-1):
            startFile.write(f"{relativeCoordinates[i][0]} {relativeCoordinates[i][1]} {relativeCoordinates[i][2]}\n")

        startFile.close()


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
        memberSocket.connect((members[i], 3350))
        msg = f"GOTO;{orijin_lat};{orijin_lon};{orijin_alt};{way}" 

        memberSocket.send(msg.encode("utf-8"))
        

        


def lineFormation(x, y, z):
    inputFile = open("inputFile", "w")

    inputFile.write(f"clear")

    inputFile.close()

    time.sleep(1)


    offset = 1
    size = os.path.getsize("usedNodeFile")

    offset = 1
    print(str(getTime()) +  f"Size of usedNodeFile: {size}\n")
    f = open('usedNodeFile', 'r+')
    f.truncate(0) # need '0' when using r+

    size = os.path.getsize("usedNodeFile")
    
    print(str(getTime()) +  f"Size of usedNodeFile: {size}\n")

   
    for member in members: # havada olan her bir drone'a bağlanacağız
        tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tempSocket.connect((member, 3350)) 

            tempMsg = f"REPORTRELATIONALCOORDINATE;{orijin_lat};{orijin_lon};{orijin_alt}" # XYZ koordinatlarını almak için gönderdiğimiz komut
            tempSocket.send(tempMsg.encode("utf-8"))

            tempMsg = None

            while not tempMsg: # mesaj gelene kadar bekliyoruz
                tempMsg = tempSocket.recv(1024).decode("utf-8")


            tempArr = tempMsg.split(';') # gelen veriyi bölüyoruz

            # gelen her koordinatı, havadaki drone'ların adreslerinin kayıtlı olduğu dizedeki sırayı
            # koruyacak şekilde diziye ekliyoruz
            relativeCoordinates.append((float(tempArr[0]), float(tempArr[1]), float(tempArr[2]))) 

        except Exception as ex:
            print(str(getTime()) +  f": Error while getting relative coordinates: {member}\n")
        finally:
            tempSocket.close()

    startFile = open("startNodes", "w")

    for i in range(0, len(relativeCoordinates)-1):
        print(str(getTime()) +  f": Writing start nodes. {i}\n")
        startFile.write(f"{relativeCoordinates[i][0]} {relativeCoordinates[i][1]} {relativeCoordinates[i][2]}\n")

    startFile.close()



    formationObj = Formation(x, y, z, len(members), y, 10 ,"line")
    
    formation = formationObj.lineFormation()

    
        

    for i in range(0, len(members)-1):
        print(i)
        print(str(getTime()) +  f": Current coordinates of {members[i]}:  X -> {relativeCoordinates[i][0]}, Y -> {relativeCoordinates[i][1]}, Z -> {relativeCoordinates[i][2]}\n")
        print(str(getTime()) +  f": Rounded coordinates of {members[i]}:  X -> {roundTo(relativeCoordinates[i][0], RESOLUTION)}, Y -> {roundTo(relativeCoordinates[i][1], RESOLUTION)}, Z -> {roundTo(relativeCoordinates[i][2], RESOLUTION)}\n")
        
        print(str(getTime()) +  f": Target coordinates of {members[i]}:  X -> {formation[i][0]}, Y -> {formation[i][1]}, Z -> {formation[i][2]}\n")
        open("waySave", "w").close() # kullanılacak yol dosyası temizleniyor. Önceden içinde bir şey olmadığından
        # emin oluyoruz.

        inputFile = open("inputFile", "w")

        inputFile.write(f"{roundTo(relativeCoordinates[i][0], RESOLUTION)} {roundTo(relativeCoordinates[i][1], RESOLUTION)} {roundTo(relativeCoordinates[i][2], RESOLUTION)} {formation[i][0]} {formation[i][1]} {formation[i][2]} 1")
        # dron'un şuanki koordinatını ve gideceği yerin koordinatlarını, yol bulan programa veriyoruz. Sondaki 1, bulunan yolun, sonrasında bulucank yollar ile çakışmaması için kenara kaydetmesini söylüyor.

        inputFile.close()
    
        wayFile = open("waySave", "r")
        
        


        while os.path.getsize("inputFile"):
            continue

        way = wayFile.read() # bulunan yolu dosyadan okuyoruz

        wayFile.close()

        print(str(getTime()) +  f": Found way for {members[i]}\n")
        memberSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        memberSocket.connect((members[i], 3350))
        msg = f"GOTO;{orijin_lat};{orijin_lon};{orijin_alt};{way}" 

        memberSocket.send(msg.encode("utf-8"))
        


def testTask(x, y, z):
    inputFile = open("inputFile", "w")

    inputFile.write(f"clear")

    inputFile.close()

    time.sleep(1)

    size = os.path.getsize("usedNodeFile")

    offset = 1
    print(str(getTime()) +  f"Size of usedNodeFile: {size}\n")
    f = open('usedNodeFile', 'r+')
    f.truncate(0) # need '0' when using r+

    size = os.path.getsize("usedNodeFile")
    
    print(str(getTime()) +  f"Size of usedNodeFile: {size}\n")


    tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    member = members[0]

    try:
        tempSocket.connect((member, 3350)) 

        tempMsg = f"REPORTRELATIONALCOORDINATE;{orijin_lat};{orijin_lon};{orijin_alt}" # XYZ koordinatlarını almak için gönderdiğimiz komut
        tempSocket.send(tempMsg.encode("utf-8"))

        tempMsg = None

        while not tempMsg: # mesaj gelene kadar bekliyoruz
            tempMsg = tempSocket.recv(1024).decode("utf-8")


        print(tempMsg)
        tempArr = tempMsg.split(';') # gelen veriyi bölüyoruz

        # gelen her koordinatı, havadaki drone'ların adreslerinin kayıtlı olduğu dizedeki sırayı
        # koruyacak şekilde diziye ekliyoruz
        relativeCoordinates.append((float(tempArr[0]), float(tempArr[1]), float(tempArr[2]))) 

    except:
        print(str(getTime()) +  f": Error while getting relative coordinates: {member}\n")
    finally:
        tempSocket.close()

    startFile = open("startNodes", "w")

    startFile.write(f"{relativeCoordinates[0][0]} {relativeCoordinates[0][1]} {relativeCoordinates[0][2]}\n")

    startFile.close()




    print(str(getTime()) +  f": Current coordinates of {members[0]}:  X -> {relativeCoordinates[0][0]}, Y -> {relativeCoordinates[0][1]}, Z -> {relativeCoordinates[0][2]}\n")
    print(str(getTime()) +  f": Rounded coordinates of {members[0]}:  X -> {roundTo(relativeCoordinates[0][0], RESOLUTION)}, Y -> {roundTo(relativeCoordinates[0][1], RESOLUTION)}, Z -> {roundTo(relativeCoordinates[0][2], RESOLUTION)}\n")
    
    print(str(getTime()) +  f": Target coordinates of {members[0]}:  X -> {x}, Y -> {y}, Z -> {z}\n")
    open("waySave", "w").close() # kullanılacak yol dosyası temizleniyor. Önceden içinde bir şey olmadığından
    # emin oluyoruz.

    inputFile = open("inputFile", "w")

    inputFile.write(f"{roundTo(relativeCoordinates[0][0], RESOLUTION)} {roundTo(relativeCoordinates[0][1], RESOLUTION)} {roundTo(relativeCoordinates[0][2], RESOLUTION)} {x} {y} {z} 1")
    # dron'un şuanki koordinatını ve gideceği yerin koordinatlarını, yol bulan programa veriyoruz. Sondaki 1, bulunan yolun, sonrasında bulucank yollar ile çakışmaması için kenara kaydetmesini söylüyor.

    inputFile.close()

    wayFile = open("waySave", "r")


    while os.path.getsize("inputFile"):
        continue

    way = wayFile.read() # bulunan yolu dosyadan okuyoruz

    wayFile.close()

    print(str(getTime()) +  f": Found way for {members[0]}\n")
    memberSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        memberSocket.connect((members[0], 3350))
        msg = f"GOTO;{orijin_lat};{orijin_lon};{orijin_alt};{way}" 

        memberSocket.send(msg.encode("utf-8"))
    except Exception as ex:
        print(str(getTime()) +  f": Exception occured while sending task to drone: {ex}\n")
    finally:
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
            print(str(getTime()) +  f": New task request recieved\n")
            print(str(getTime()) +  f": {msg}\n")

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
                members.append(member)

            if taskType == "TRIANGLE":
                triangleFormation(float(x),float(y),float(z))
            elif taskType == "TEST":
                testTask(float(x),float(y),float(z))
            elif taskType == "LINE":
                lineFormation(float(x),float(y),float(z))
                


        
    
    except Exception as ex:
        print(str(getTime()) +  f": {ex}\n")
        
        continue
    finally:
        if socketOn:
            print(str(getTime()) +  f": Connection closed from: {sock.getpeername()}\n")
            sock.close()
