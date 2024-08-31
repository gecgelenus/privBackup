import socket
import time





while True:
    tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:

        msg = input("->")
        

        tempSocket.connect(("10.15.162.8", 14550))

        tempSocket.send(msg.encode("utf-8"))
        tempMsg = None
        while not tempMsg: # mesaj gelene kadar bekliyoruz
            tempMsg = tempSocket.recv(1024)
            if tempMsg == b'':
                raise Exception("Connection closed by peer. Probably not sending data back.")
        print(tempMsg.decode("utf-8"))
    except Exception as e:
        print(e)
    finally:
        tempSocket.close()


