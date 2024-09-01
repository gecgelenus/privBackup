import socket
import datetime
import sys





def getTime():
    return datetime.datetime.now()

members = []

mainDrone = "127.0.0.1"


if len(sys.argv) < 4:
    print("Invalid argument count, should give: Latitude Longtitude Altitude")
    exit()

orijin_lat = sys.argv[1]
orijin_lon = sys.argv[2]
orijin_alt = sys.argv[3]


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 2350))
s.listen()



while True:
    sock, addr = s.accept()

    print(str(getTime()) +  f": New connection recieved from: {sock.getpeername()}\n")

    try:
        


        msg = sock.recv(1024).decode("utf-8")
        msgArray = msg.split(';')

        if msgArray[0] == "NEWMEMBER": # havada olan dron listesine gelen adresteki dronu ekliyoruz
            print(str(getTime()) +  f": New member drone information recieved from {sock.getpeername()}\n")
            
            if addr[0] not in members:
                members.append(addr[0])
            else:
                print(str(getTime()) +  f": This drone is already in list, but send NEWMEMBER message: {sock.getpeername()}\n")
        elif msgArray[0] == "LISTMEMBERS": 
            # Var olan listedeki dronları test ediyoruz ve hala ulaşılabilir mi diye test ediyoruz.
            # Eğer ulaşılabilir değil ise adresi listeden çıkarıyoruz ve kalan adresleri geri döndürüyoruz.
            print(str(getTime()) +  f": List of member drones information requested from {sock.getpeername()}\n")
            print(len(members))
            memberListMsg = ""
            for member in members:
                memberSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(str(getTime()) +  f": Trying to connect: {member}\n")

                try:
                    memberSocket.connect((member, 3350))
                    tempMsg = "CONNECTIONTEST"
                    memberSocket.send(tempMsg.encode("utf-8"))
                    print(str(getTime()) +  f": Member is up: {member}\n")
                    memberListMsg += member + ";"
                except:
                    print(str(getTime()) +  f": Connection couldn't established with: {member}\n")
                    members.remove(member)

                finally:
                    memberSocket.close()


            if memberListMsg == "": # eğer hiç bir dron bulunamadıysa boş döndür.
                tempMsg = "N/A"
                sock.send(tempMsg.encode("utf-8"))
            else:
                sock.send(memberListMsg.encode("utf-8"))


            

        elif msgArray[0] == "TASK": 
            # Yeni görev emri. Bu emri ana dron'a iletiyoruz.
            print(str(getTime()) +  f": New task request recieved from {sock.getpeername()}\n")
            
            taskType = msgArray[1]
            x = msgArray[2]
            y = msgArray[3]
            z = msgArray[4]
            print(str(getTime()) +  f": Task Details: Type -> {taskType}\n")
            print(str(getTime()) +  f": Task Details: X -> {x}, Y -> {y}, Z -> {z} \n")

            mainDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            mainDroneSocket.connect((mainDrone, 4350))

            tempMsg = f"TASK;{taskType};{x};{y};{z}"
            
            mainDroneSocket.send(tempMsg.encode("utf-8"))
            mainDroneSocket.close()

        elif msgArray[0] == "GETDRONELOC": # istenilen dron'un konumunu sorgula
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Drone location is requested but given address is invalid: {droneAdress}\n")
                raise

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = f"REPORTRELATIONALCOORDINATE;{orijin_lat};{orijin_lon};{orijin_alt}"

                memberDroneSocket.send(tempMsg.encode("utf-8"))

                tempMsg = None

                while not tempMsg:
                    tempMsg = memberDroneSocket.recv(1024).decode("utf-8")

                tempLoc = tempMsg.split(';')
                

                if len(tempLoc) != 3:
                    print(str(getTime()) +  f": Invalid data recieved: {tempMsg}\n")
                    raise
                print(str(getTime()) +  f": Location of: {droneAdress} X -> {tempLoc[0]}, Y -> {tempLoc[1]}, Z -> {tempLoc[2]}\n")
                sock.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()

        elif msgArray[0] == "GETDRONEALT": # istenilen dron'un yüksekliğini sorgula
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Drone altitude is requested but given address is invalid: {droneAdress}\n")
                raise

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "REPORTALTITUDE"

                memberDroneSocket.send(tempMsg.encode("utf-8"))

                tempMsg = None

                while not tempMsg:
                    tempMsg = memberDroneSocket.recv(1024).decode("utf-8")
                

                print(str(getTime()) +  f": Altitude of: {droneAdress} -> {tempMsg}\n")
                sock.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "GETDRONEVOLTAGE": # istenilen dron'un yüksekliğini sorgula
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Drone voltage is requested but given address is invalid: {droneAdress}\n")
                raise

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "REPORTVOLTAGE"

                memberDroneSocket.send(tempMsg.encode("utf-8"))

                tempMsg = None

                while not tempMsg:
                    tempMsg = memberDroneSocket.recv(1024).decode("utf-8")
                

                sock.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "GETDRONEGPS": # istenilen dron'un GPS verilerini sorgula
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Drone GPS is requested but given address is invalid: {droneAdress}\n")
                raise

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "REPORTGPS"

                memberDroneSocket.send(tempMsg.encode("utf-8"))

                tempMsg = None

                while not tempMsg:
                    tempMsg = memberDroneSocket.recv(1024).decode("utf-8")
                
                tempGPS = tempMsg.split(';')

                print(str(getTime()) +  f": GPS of: {droneAdress} -> Long: {tempGPS[0]}, Lat: {tempGPS[1]}\n")
                sock.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()

        elif msgArray[0] == "MAKEMAIN": # istenilen dron'u yeni ana dron olarak ata
            mainDrone = msgArray[1]
            print(str(getTime()) +  f": New main drone request recieved from {sock.getpeername()} -> for {mainDrone}\n")
            
            mainDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                mainDroneSocket.connect((mainDrone, 3350))
                
                tempMsg = "BECOMEMAIN"

                mainDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error connection with {mainDroneSocket.getpeername()}\n")
            finally:
                print(str(getTime()) +  f": Closing connection with {mainDroneSocket.getpeername()}\n")
                mainDroneSocket.close()
        elif msgArray[0] == "ARM":
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Drone arm is requested but given address is invalid: {droneAdress}\n")
                raise Exception("Invalid drone address")

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "ARM"

                memberDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "STOPARM":
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Drone arm is requested but given address is invalid: {droneAdress}\n")
                raise Exception("Invalid drone address")

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "STOPARM"

                memberDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "STOPTASK":
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Drone task stop is requested but given address is invalid: {droneAdress}\n")
                raise Exception("Invalid drone address")

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "STOPTASK"

                memberDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "STOPTAKEOFF":
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Drone arm is requested but given address is invalid: {droneAdress}\n")
                raise Exception("Invalid drone address")

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "STOPTAKEOFF"

                memberDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "TAKEOFF":
            droneAdress = msgArray[1]
            if droneAdress not in members:
                print(str(getTime()) +  f": Drone takeoff is requested but given address is invalid: {droneAdress}\n")
                raise Exception("Invalid drone address")

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = f"TAKEOFF;{msgArray[2]}"

                memberDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "LAND":
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Drone land is requested but given address is invalid: {droneAdress}\n")
                raise Exception("Invalid drone address")

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "LAND"

                memberDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "HOLDTASK":
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Holding task is requested but given address is invalid: {droneAdress}\n")
                raise Exception("Invalid drone address")

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "HOLDTASK"

                memberDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "RESUMETASK":
            droneAdress = msgArray[1]

            if droneAdress not in members:
                print(str(getTime()) +  f": Holding task is requested but given address is invalid: {droneAdress}\n")
                raise Exception("Invalid drone address")

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = "RESUMETASK"

                memberDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "GOTODIRECTION":
            droneAdress = msgArray[1]
            distance = msgArray[2]
            direction = msgArray[3]
            speed = msgArray[4]
            if droneAdress not in members:
                print(str(getTime()) +  f": Drone specific task is requested but given address is invalid: {droneAdress}\n")
                raise Exception("Invalid drone address")

            memberDroneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                memberDroneSocket.connect((droneAdress, 3350))

                tempMsg = f"GOTODIRECTION;{distance};{direction};{speed}"

                memberDroneSocket.send(tempMsg.encode("utf-8"))
            except:
                print(str(getTime()) +  f": Error occured on connection with: {droneAdress}\n")
            finally:
                print(str(getTime()) +  f": Connection closing: {droneAdress}\n")
                memberDroneSocket.close()
        elif msgArray[0] == "GETMAIN":
            print(str(getTime()) +  f": Main drone address requested from {mainDroneSocket.getpeername()}\n")
            sock.send(mainDrone.encode("utf-8"))
        elif msgArray[0] == "TAKEOFFSUCCESS":
            print(str(getTime()) +  f": Take off is success on drone {sock.getpeername()}\n")
        elif msgArray[0] == "ARMSUCCESS":
            print(str(getTime()) +  f": Arm is success on drone {sock.getpeername()}\n")
        elif msgArray[0] == "GOTOTASKSUCCESS":
            print(str(getTime()) +  f": Go to direction task is success on drone {sock.getpeername()}\n")
        else:     
            raise Exception(f"Unknown command recieved: {msg}")
       
    except Exception as ex:
        print(str(getTime()) +  f": Connection error from: {sock.getpeername()}: {ex}\n")
        
        continue
    finally:
        print(str(getTime()) +  f": Connection closed from: {sock.getpeername()}\n")
        sock.close()
