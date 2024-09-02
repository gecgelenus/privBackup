import socket
import threading
import datetime
import sys
import os
import signal
import subprocess
import time
import threading
import serial
from math import radians, degrees, sin, cos, sqrt

from dronekit import connect, VehicleMode, LocationGlobalRelative
import math
from geopy.distance import distance, distance
from geopy.point import Point

HOST = '127.0.0.1'  
PORT = 3350
CHECK_DISTANCE = False
CRITICAL_BATTERY_LEVEL = 10.7
SAFE_DISTANCE = 50
if CHECK_DISTANCE:
    ser = serial.Serial('/dev/ttyACM0', 115200)

anchors = ["0x0A11", "0xCC8A"]
anchors.sort()
holdFlag = [False, False]
currentAnchor = None



def getTime():
    return datetime.datetime.now()

graphProcess = None
mainProcess = None

socketOn = False


armThread = None
takeoffThread = None
gotoDirectionThread = None
taskThread = None


armContinue = False
takeoffContinue = False
gotoDirectionContinue = False
taskContinue = False


hostname = socket.gethostname()
localIp = socket.gethostbyname(hostname)

if len(sys.argv) < 2:
    print("Invalid argument count, atleast one parameter should be given.")
    exit()

groundAddress = sys.argv[1]

graphCmd = "./astar graphFile usedNodeFile"
mainCmd = f"python3 mainDrone.py {groundAddress}"


def sendMessage(sck, msg):
    sck.send(msg.encode('utf-8'))

def read_serial_data():
    arr = []

    while True:
        # Seri porttan bir satır oku
        line = ser.readline().decode('utf-8').strip()
        # Satırı " / " işaretine göre ayır
        data_pairs = line.replace(' ', '').split('/')

        for data in data_pairs:
            if data == None:
                continue
            
            if '=' in data:
                # Adres ve mesafe kısımlarını ayır
                address, distance = data.split('=')

                # Boşlukları temizle ve mesafe kısmındaki fazlalıkları kaldır
                address = address.strip()
                distance = distance.strip().split(' ')[0]  # Mesafe kısmını ayıkla

                

                arr.append((address, int(distance)))
        # İşlem tamamlandıktan sonra arr listesini döndür
        return arr



def batterySafetyCheck():
    while True:
        voltage = vehicle.battery.voltage
        if voltage < CRITICAL_BATTERY_LEVEL:
            print(str(getTime()) +  f": Battery level is under safe level. Landing drone now!\n")

            armContinue = False
            takeoffContinue = False
            gotoDirectionContinue = False
            land()
            


def DistanceSafetyCheck():
    
    while True:
        distArr = read_serial_data()
        
        for (an, dist) in distArr:
            if an == currentAnchor:
                continue

            if dist < SAFE_DISTANCE*10:
                if currentAnchor == None:
                    holdFlag[anchors.index(an)] = True
                elif anchors.index(currentAnchor) > anchors.index(an):
                    holdFlag[anchors.index(an)] = True
                else:
                    holdFlag[anchors.index(an)] = False


            else:
                holdFlag[anchors.index(an)] = False
                






# Dron'un başka bir drone'a ve ya yer istasyonuna göndermek için kullandığı fonksiyon.
# Veri gönderme işini bir fonksiyon içinde yapmamızın nedeni okunabilirliği arttırmak ve
# gönderilen paketlerin yer istasyonunda kaydını tutmak için yazacağımız koda zemin hazırlamak.

# -------------------------- Mesaj Formatı --------------------------------
# Dronlar arasındaki haberleşmeyi soyutlayabildiğim kadar soyutladım.
# Sana düşen istenilen verileri yukarında tanımladığım sendMessage fonksiyonu ile göndermen.
# İlk parametre gönderilecek dronun ile kurulan bağlantının socket değişkeni.
# İkinci parametre göndereceğin mesaj. Gönderilecek mesaj noktalı virgül ile ayrılmalı
# Örneğin GPS koordinatı için iki tane verimiz var. Lattitude ve Longtitude. Bunları "Lattitude;Longtitude" diye göndereceğiz. Yine örnek olarak "49.3324;52.4343" gibi.
# HOST değişkeni ana dron'un adresi.
# Dron değiştiği zaman aşağıdaki changeMain fonksiyonu bu adresi güncelleyeceği için, bu adres güncel olacak.


def calculate_target_gps(start_latitude, start_longitude, target_distance_meters, direction):
    # Create a starting point object
    start_point = Point(latitude=start_latitude, longitude=start_longitude)

    # Calculate target point using Vincenty's formula
    if direction.lower() == 'north':
        target_point = distance(meters=target_distance_meters).destination(start_point, 0)
    elif direction.lower() == 'south':
        target_point = distance(meters=target_distance_meters).destination(start_point, 180)
    elif direction.lower() == 'east':
        target_point = distance(meters=target_distance_meters).destination(start_point, 90)
    elif direction.lower() == 'west':
        target_point = distance(meters=target_distance_meters).destination(start_point, 270)
    else:
        raise ValueError("Direction must be one of: 'north', 'south', 'east', 'west'.")

    # Extract latitude and longitude from the target point
    target_latitude, target_longitude = target_point.latitude, target_point.longitude

    return target_latitude, target_longitude


EARTH_RADIUS = 6378137  # Earth's radius in meters (mean radius)

def gps_from_xyz(reference_gps, x, y, z):
    """
    Calculate GPS coordinates given an initial GPS coordinate and an x, y, z offset.
    
    Parameters:
    - reference_gps: Tuple of (latitude, longitude, altitude) in degrees and meters.
    - x: X offset in meters (East/West).
    - y: Y offset in meters (Up/Down).
    - z: Z offset in meters (North/South).
    
    Returns:
    - Tuple of (latitude, longitude, altitude) corresponding to the given x, y, z offsets.
    """
    
    # Unpack the reference GPS coordinates
    ref_lat, ref_lon, ref_alt = reference_gps

    print(f"Referance gps: {reference_gps}")
    print(f"Referance xyz: {x}, {y}, {z}")
    
    # Convert latitude and longitude to radians
    ref_lat_rad = radians(ref_lat)
    ref_lon_rad = radians(ref_lon)
    
    # Latitude: Delta in meters is divided by Earth's radius
    delta_lat = z / EARTH_RADIUS
    delta_lon = x / (EARTH_RADIUS * cos(ref_lat_rad))
    
    # Convert back to degrees
    new_lat = ref_lat + degrees(delta_lat)
    new_lon = ref_lon + degrees(delta_lon)
    new_alt = ref_alt + y  # Altitude offset
    
    return LocationGlobalRelative(new_lat, new_lon, new_alt)


def xyz_from_gps(reference_gps, target_gps):
    """
    Calculate x, y, z coordinates given a reference GPS coordinate and a target GPS coordinate.
    
    Parameters:
    - reference_gps: Tuple of (latitude, longitude, altitude) in degrees and meters.
    - target_gps: Tuple of (latitude, longitude, altitude) in degrees and meters.
    
    Returns:
    - Tuple of (x, y, z) corresponding to the given GPS coordinates relative to the reference.
      x: East/West (meters)
      y: Up/Down (meters)
      z: North/South (meters)
    """
    
    
    # Unpack the reference and target GPS coordinates
    ref_lat, ref_lon, ref_alt = reference_gps
    target_lat, target_lon, target_alt = target_gps
    
    # Convert latitude and longitude to radians
    ref_lat_rad = radians(ref_lat)
    ref_lon_rad = radians(ref_lon)
    target_lat_rad = radians(target_lat)
    target_lon_rad = radians(target_lon)
    
    # Calculate the differences in latitude and longitude
    delta_lat = target_lat_rad - ref_lat_rad
    delta_lon = target_lon_rad - ref_lon_rad
    
    # Calculate x, y, z
    x = delta_lon * EARTH_RADIUS * cos(ref_lat_rad)  # East/West
    y = target_alt - ref_alt                        # Up/Down
    z = delta_lat * EARTH_RADIUS                    # North/South
    
    return (x, y, z)




# Function to calculate distance in meters between two GPS coordinates
def get_distance_metres(location1, location2):
    dlat = location2.lat - location1.lat
    dlong = location2.lon - location1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def get_distance_metres2(location1, location2):
    dlat = location2[0] - location1.lat
    dlong = location2[1] - location1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def arm():
    global armContinue
    print("Motorlara güç veriliyor")
    while not vehicle.is_armable:
        if not armContinue:
            print(str(getTime()) +  f": Arm canceled.\n")

            return 
        print(" Aracın başlatılması bekleniyor (is_armable=false)...")
        print(f" GPS: {vehicle.gps_0}, Batarya: {vehicle.battery}, Mod: {vehicle.mode}")
        time.sleep(0.5)

    print("Motorlara güç aktarımı bekleniyor")
    vehicle.mode = VehicleMode("GUIDED")
    while vehicle.mode != "GUIDED":
        if not armContinue:
            print(str(getTime()) +  f": Arm canceled.\n")
            return 
        print(" GUIDED moduna geçiş bekleniyor...")
        vehicle.mode = VehicleMode("GUIDED")
        time.sleep(0.5)

    vehicle.armed = True

    while not vehicle.armed:
        if not armContinue:
            print(str(getTime()) +  f": Arm canceled.\n")
            vehicle.armed = False
            return 
        print(" Güç aktarımı bekleniyor (armed=false)...")
        vehicle.armed = True
        time.sleep(0.5)

    print(str(getTime()) +  f": Arm success!\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((groundAddress, 2350))
    socketOn = True
    msg = "ARMSUCCESS"
    sock.send(msg.encode("utf-8"))
    sock.close()
    socketOn = False
    armContinue = False
    

def takeoff(target_altitude):
    global takeoffContinue
    print(f"Kalkış emri alındı: {target_altitude} metre")
    vehicle.simple_takeoff(target_altitude) 

    while True:
        if not takeoffContinue:
            print(str(getTime()) +  f": Take off canceled.\n")

            vehicle.mode = VehicleMode("LAND")
            return
        print(" İrtifa: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= float(target_altitude) * 0.95:
            print("Hedef irtifaya ulaşıldı")
            break
        time.sleep(0.5)
    
    print(str(getTime()) +  f": Takeoff success!\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((groundAddress, 2350))
    socketOn = True
    msg = "TAKEOFFSUCCESS"
    sock.send(msg.encode("utf-8"))
    sock.close()
    socketOn = False
    takeoffContinue = False

def move_in_direction(direction, distance):
   
    current_location = vehicle.location.global_relative_frame
    target_lat = current_location.lat + (distance * cos(radians(direction)) / 1.113195e5)
    target_lon = current_location.lon + (distance * sin(radians(direction)) / 1.113195e5)
    target_location = LocationGlobalRelative(target_lat, target_lon, current_location.alt)
    vehicle.simple_goto(target_location)

    while True:
        remaining_distance = get_distance_metres(vehicle.location.global_relative_frame, target_location)
        print(f"Distance remaining: {remaining_distance:.2f} meter")

       

        if remaining_distance <= 0.352:
            print("Location reached.")
            break
        time.sleep(1)


def holdTask():
    print(str(getTime()) + f"Close proximity detected, holding current task\n")

    
    current_location = vehicle.location.global_relative_frame

    


    vehicle.simple_goto(current_location)

    while True:
        breakLoop = True
        for flag in holdFlag:
            if flag:
                breakLoop = False
        if breakLoop:
            break

    print(str(getTime()) + f"Continuing current task\n")
    


def land():
    global armContinue
    global takeoffContinue
    global gotoDirectionContinue


    armContinue = False
    takeoffContinue = False
    gotoDirectionContinue = False



    while vehicle.mode != "LAND":
        print("Waiting for LAND mode...")
        vehicle.mode = VehicleMode("LAND")
        time.sleep(0.5)


def goto_position(vehicle, latitude, longitude, altitude):
    global gotoDirectionContinue
    target_location = LocationGlobalRelative(latitude, longitude, altitude)
    vehicle.simple_goto(target_location)
    while True:
        if not gotoDirectionContinue:
            print(str(getTime()) +  f": Directional task canceled.\n")

            return
        current_location = vehicle.location.global_relative_frame
        distance = get_distance_metres(current_location, target_location)
        print(distance)

        if distance < 1.5:
            print("Reached target position.")
            break
        time.sleep(1)



# GPS koordinatlarını gönderecek fonksiyon. 
def reportGPS(sock):
    current_location = vehicle.location.global_relative_frame
    msg = f"{current_location.lat};{current_location.lon}"
    sock.send(msg.encode("utf-8"))
    return


# Yüksekliği gönderecek fonksiyon
def reportAltitude(socket):
    current_location = vehicle.location.global_relative_frame
    msg = f"{current_location.alt}"
    sock.send(msg.encode("utf-8"))
    return

def reportRelationalCoordinate(sock, orijinLat, orijinLon, orijinAlt):
    
    try:
        current_location = vehicle.location.global_relative_frame


        (x, y, z) = xyz_from_gps((orijinLat, orijinLon, orijinAlt), (current_location.lat, current_location.lon, current_location.alt))

        msg = f"{x};{y};{z}"
        print(msg)

        sock.send(msg.encode("utf-8"))
    except:
        print(str(getTime()) +  f": Error ocurred while reporting relational coordinate.\n")
    finally:
        sock.close()
    return  


# Bu dron'u ana dron olarak tayin eden fonksiyon. Ben dolduracağım
def InitMainDrone(socket):
    

    graphProcess = subprocess.Popen(graphCmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid)
    mainProcess = subprocess.Popen(mainCmd, stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid)

    return

# Yeni ana dron'un IP adresini kaydeden fonksiyon. Yapılacak bir şey yok.
def changeMain(socket, addr):
    HOST = addr[0]
    if HOST != localIp:
        os.killpg(os.getpgid(graphProcess.pid), signal.SIGTERM)
        os.killpg(os.getpgid(mainProcess.pid), signal.SIGTERM)

    return

# Ana dron'dan, gidilecek rotayı alan ve rota üzerinde yol almayı sağlayacak fonksiyon. Daha sonra yapılacak.
def recieveTask(sock, lat, lon, alt,  wayList):
    print(str(getTime()) +  f": Parsing task\n")

    try:
        wayLines = wayList.split('\n')
        wayPoints = []
        for line in wayLines:
            if '0' in line:
                print(f"--> {line}")
                wayPoints.append(line.split(' '))

    except Exception as ex:
        print(str(getTime()) +  f": Exception while parsing task: {ex}\n")
        
    wayPoints.reverse()
    del wayPoints[0]
    print(wayPoints)

    goto(float(lat), float(lon), float(alt), wayPoints)



    return


def goto(ref_lat, ref_lon, ref_alt, coordArr):
    global taskContinue

    # coordArr[0] = (x,y,z)
    wayPointCount = 0   
    
    for x, y, z in coordArr:
        if not taskContinue:
            print(str(getTime()) +  f": Aborting task.\n")
            return
            


        targetGPS = gps_from_xyz((ref_lat, ref_lon, ref_alt), float(x), float(y), float(z))
        
        print(targetGPS)
        while True:
            remaining_distance = get_distance_metres(vehicle.location.global_relative_frame, targetGPS)
            print(f"Distance remaining: {remaining_distance:.2f} meter for waypoint {wayPointCount}")
            vehicle.simple_goto(targetGPS)

            if not taskContinue:
                print(str(getTime()) +  f": Aborting task.\n")
                return
        
            for flag in holdFlag:
                if flag:
                    holdTask()
        

            if remaining_distance <= 1:
                print("Location reached.")
                break
            time.sleep(0.5)

        wayPointCount = wayPointCount + 1


    taskContinue = False
    return

def goto_direction(sock, distance, direction):
    sock.close()
    socketOn = False

    move_in_direction(direction, distance)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((groundAddress, 2350))
    socketOn = True
    msg = "GOTOTASKSUCCESS"
    sock.send(msg.encode("utf-8"))
    sock.close()
    socketOn = False




    return





# Aracınıza bağlanın )
print("Araca bağlanılıyor...")
vehicle = connect('127.0.0.1:14550', wait_ready=True)

batteryCheckThread = threading.Thread(target=batterySafetyCheck)
batteryCheckThread.start()


if CHECK_DISTANCE:
    distanceCheckThread = threading.Thread(target=DistanceSafetyCheck)
    distanceCheckThread.start()



tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tempSocket.connect((groundAddress, 2350))

tempMsg = f"NEWMEMBER"

tempSocket.send(tempMsg.encode("utf-8"))

tempSocket.close()




s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', PORT))
s.listen()


while True:
    

    sock, addr = s.accept()

    print(str(getTime()) +  f": New connection established with {sock.getpeername()}\n")


    try:
        message = sock.recv(1024).decode('utf-8')

        if not message:
            continue
        
        msgArray = message.split(';')

        print(str(getTime()) +  f": Recieved message from {sock.getpeername()}: {message}\n")

        if msgArray[0] == "REPORTGPS":
            print(str(getTime()) +  f": GPS report request from {sock.getpeername()}\n")
            reportGPS(sock)
        elif msgArray[0] == "REPORTALTITUDE":
            print(str(getTime()) +  f": Altitude report request from {sock.getpeername()}\n")
            reportAltitude(sock)
        elif msgArray[0] == "REPORTRELATIONALCOORDINATE":
            print(str(getTime()) +  f": Relational coordinate report request from {sock.getpeername()}\n")
            reportRelationalCoordinate(sock, float(msgArray[1]), float(msgArray[2]), float(msgArray[3]))

        elif msgArray[0] == "BECOMEMAIN":
            print(str(getTime()) +  f": Main drone change request from {sock.getpeername()}\n")
            InitMainDrone(sock)
        elif msgArray[0] == "NEWMAIN":
            print(str(getTime()) +  f": New main drone information recieved from {sock.getpeername()}\n")
            changeMain(sock, addr)         
        elif msgArray[0] == "GOTO":
            print(str(getTime()) +  f": New task route recieved from {sock.getpeername()}\n")
            if taskContinue == True:
                print(str(getTime()) +  f": Task request recieved but another task request is already running!\n")
                raise
            taskContinue = True
            gotoDirectionThread = threading.Thread(target=recieveTask, args=(sock, msgArray[1], msgArray[2], msgArray[3], msgArray[4],))
            gotoDirectionThread.start()
            
        elif msgArray[0] == "GOTODIRECTION":
            print(str(getTime()) +  f": New task route recieved from {sock.getpeername()} on {msgArray[2]} for {msgArray[1]} m\n")
            
            if gotoDirectionThread != None:
                print(str(getTime()) +  f": Directional task recieved but another task is already running!\n")
                raise
            
            goto_direction(sock, float(msgArray[1]), float(msgArray[2]))
            gotoDirectionThread = threading.Thread(target=goto_direction, args=(sock,msgArray[1],msgArray[2],))
            gotoDirectionThread.start()
        elif msgArray[0] == "STOPTASKDIRECTIONAL":
            print(str(getTime()) +  f": Directional task stop request recieved from {sock.getpeername()}\n")
            gotoDirectionContinue = False
        elif msgArray[0] == "ARM":
            print(str(getTime()) +  f": Arm request recieved from {sock.getpeername()}\n")
            if armContinue == True:
                print(str(getTime()) +  f": Arm request recieved but another arm request is already running!\n")
                raise
            armContinue = True

            armThread = threading.Thread(target=arm)
            armThread.start()
        elif msgArray[0] == "STOPARM":
            print(str(getTime()) +  f": Arm stop request recieved from {sock.getpeername()}\n")
            armContinue = False
        elif msgArray[0] == "STOPTASK":
            print(str(getTime()) +  f": Task stop request recieved from {sock.getpeername()}\n")
            taskContinue = False
        elif msgArray[0] == "TAKEOFF":
            print(str(getTime()) +  f": Takeoff request recieved from {sock.getpeername()} for altitude {msgArray[1]} m\n")
            if takeoffContinue == True:
                print(str(getTime()) +  f": Takeoff recieved but another takeoff task is already running!\n")
                raise
            takeoffContinue = True
            
            takeoffThread = threading.Thread(target=takeoff, args=(msgArray[1],))
            takeoffThread.start()
        elif msgArray[0] == "REPORTVOLTAGE":
            print(str(getTime()) +  f": Voltage level request recieved from {sock.getpeername()}\n")
            voltageLevel = vehicle.battery.voltage
            sock.send(str(voltageLevel).encode("utf-8"))
        elif msgArray[0] == "STOPTAKEOFF":
            print(str(getTime()) +  f": Take off stop request recieved from {sock.getpeername()}\n")
            takeoffContinue = False
        elif msgArray[0] == "LAND":
            print(str(getTime()) +  f": Landing requested from {sock.getpeername()}\n")
            land()
        elif msgArray[0] == "HOLDTASK":
            print(str(getTime()) +  f": Holding task requested from {sock.getpeername()}\n")
            holdFlag[0] = True
        elif msgArray[0] == "RESUMETASK":
            print(str(getTime()) +  f": Resuming task requested from {sock.getpeername()}\n")
            holdFlag[0] = False
        elif msgArray[0] == "CONNECTIONTEST":
            print(str(getTime()) +  f": Connection test requested from {sock.getpeername()}\n")
        else:
            print(str(getTime()) +  f": Unable to interpret message from {sock.getpeername()}: {message}\n")

                



        
    except Exception as ex:
        print(str(getTime()) +  f": Connection error with: {sock.getpeername()}: {ex}\n")
    finally:
        if socketOn:
            print(str(getTime()) +  f": Connection closed from {sock.getpeername()}\n")

            sock.close()
            socketOn = False
    
    


