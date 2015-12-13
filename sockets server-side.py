import threading
import socket
import sys
import json

def convert(data):
	data = list(data)
	for char in range(len(data)-1,-1,-1):
		if data[char] == '[':
			data.insert(char,',')
	return "".join(['[']+data[1:]+[']'])

def recieveThread(c,addr):
    #Send initial heartbeat
    c.send(json.dumps(["h","#"]).encode())
    while 1:
        try:
            recievedData = json.loads(convert(c.recv(1024).decode()))
        except (socket.error,socket.timeout):
            c.close()
            print("Closed connection from",addr)
            getNewConnection()
            return
        for data in recievedData:
            if data[0] == "h":
                try:
                    c.send(json.dumps(["h","#"]).encode())
                except socket.error:
                    c.close()
                    print("Closed connection from",addr)
                    getNewConnection()
                    return
            if data[0] == "m":
                with msg_l:
                    inMessages.append(data[1])

def getNewConnection():
    c,addr = s.accept()
    c.settimeout(5.0)
    with con_l:
        connAddr[0],connAddr[1] = c,addr
    print("Got connection from",addr)
    threading.Thread(target=recieveThread,args=(c,addr)).start()

def processData(data):
    if data[:5] == "eval ":
        try:
            returnValue = data[5:] + " => " + str(eval(data[5:]))
        except:
            e = sys.exc_info()[0]
            returnValue = data[5:] + " => " + str(e.__name__)
    else:
        returnValue = data
    
    return returnValue

s = socket.socket()
host = socket.gethostname()
port = 12346
s.bind((host,port))
print("Connection:\nHost -",host,"\nPort -",port)
s.listen(5)

connAddr = [None,None]
inMessages = [] #Per user..
msg_l = threading.Lock()
con_l = threading.Lock()#Only needed when changing
prnt_l = threading.Lock()

getNewConnection()
while 1:
    if inMessages != []:
        while inMessages != []:
            with msg_l:
                returnValue = processData(inMessages.pop())
            returnValue = str(connAddr[1][0]) + " - " + str(connAddr[1][1]) + " >> " + returnValue
            with prnt_l:
                print(returnValue)
            try:
                connAddr[0].send(json.dumps(["m",returnValue]).encode())
            except socket.error:
                continue #Recieve thread will get it, and don't want to risk trying to get 2 connections
