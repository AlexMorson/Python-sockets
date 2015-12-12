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
            c,addr = s.accept()
            c.settimeout(5.0)
            print("Got connection from",addr)
            threading.Thread(target=recieveThread,args=(c,addr)).start()
            return
        for data in recievedData:
            if data[0] == "h":
                try:
                    c.send(json.dumps(["h","#"]).encode())
                except socket.error:
                    c.close()
                    print("Closed connection from",addr)
                    c,addr = s.accept()
                    c.settimeout(5.0)
                    print("Got connection from",addr)
                    threading.Thread(target=recieveThread,args=(c,addr)).start()
                    return
            if data[0] == "m":
                with msg_l:
                    inMessages.append(data[1])

        while outMessages != []:
            with out_l:
                try:
                    c.send(outMessages.pop())
                except socket.error:
                    c.close()
                    print("Closed connection from",addr)
                    c,addr = s.accept()
                    c.settimeout(5.0)
                    print("Got connection from",addr)
                    threading.Thread(target=recieveThread,args=(c,addr)).start()
                    return

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

inMessages = [] #Per user..
outMessages = []
msg_l = threading.Lock()
prnt_l = threading.Lock()
out_l = threading.Lock()

c,addr = s.accept()
c.settimeout(5.0)
print("Got connection from",addr)
threading.Thread(target=recieveThread,args=(c,addr)).start()
while 1:
    if inMessages != []:
        while inMessages != []:
            with msg_l:
                returnValue = processData(inMessages.pop())
            with prnt_l:
                print(addr[0],"-",addr[1],">>",returnValue)
            with out_l:
                outMessages.append(json.dumps(["m",addr[0]+" - "+str(addr[1])+" >> "+returnValue]).encode())
