import socket

drone1 = "10.15.170.146"
drone2 = "10.15.161.249"



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


input("calibrate gps")

gpsArr = []
alt = ""
try:
    s.connect(("127.0.0.1", 2350))

    msg = f"GETDRONEGPS;{drone1}"
    s.send(msg.encode("utf-8"))

    tempMsg = None
    while not tempMsg: # mesaj gelene kadar bekliyoruz
        tempMsg = s.recv(1024)
        if tempMsg == b'':
            raise Exception("Connection closed by peer. Probably not sending data back.")
    gpsT = tempMsg.decode("utf-8")

    gpsArr = gpsT.split(';')

    
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


try:
    s.connect(("127.0.0.1", 2350))

    msg = f"GETDRONEALT;{drone1}"
    s.send(msg.encode("utf-8"))

    tempMsg = None
    while not tempMsg: # mesaj gelene kadar bekliyoruz
        tempMsg = s.recv(1024)
        if tempMsg == b'':
            raise Exception("Connection closed by peer. Probably not sending data back.")
    alt = tempMsg.decode("utf-8")

    

    
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(("127.0.0.1", 2350))

    msg = f"SETORIJINGPS;{gpsArr[0]};{gpsArr[1]};0"
    s.send(msg.encode("utf-8"))
    
    tempMsg = None
    while not tempMsg: # mesaj gelene kadar bekliyoruz
        tempMsg = s.recv(1024)
        if tempMsg == b'':
            raise Exception("Connection closed by peer. Probably not sending data back.")
    alt = tempMsg.decode("utf-8")

    

    
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()




input("arm")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(("127.0.0.1", 2350))

    msg = f"ARM;{drone1}"

    s.send(msg.encode("utf-8"))
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(("127.0.0.1", 2350))

    msg = f"ARM;{drone2}"

    s.send(msg.encode("utf-8"))
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()

input("takeoff")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(("127.0.0.1", 2350))

    msg = f"TAKEOFF;{drone1};5"

    s.send(msg.encode("utf-8"))
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(("127.0.0.1", 2350))

    msg = f"TAKEOFF;{drone2};5"

    s.send(msg.encode("utf-8"))
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()

input("give task")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(("127.0.0.1", 2350))

    msg = f"TASK;LINE;0;5;5"

    s.send(msg.encode("utf-8"))
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()


input("give task back")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(("127.0.0.1", 2350))

    msg = f"TASK;LINE;0;5;0"

    s.send(msg.encode("utf-8"))
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()

input("land all")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(("127.0.0.1", 2350))

    msg = f"LAND;{drone1}"

    s.send(msg.encode("utf-8"))
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


try:
    s.connect(("127.0.0.1", 2350))

    msg = f"LAND;{drone2}"

    s.send(msg.encode("utf-8"))
except Exception as ex:
    print(f"Exception occured: {ex}")
finally:
    s.close()