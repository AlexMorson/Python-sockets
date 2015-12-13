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

def recieveThread(c,addr,name,msg_l,inMessages):
    #Send initial heartbeat
    c.send(json.dumps(["h","#"]).encode())
    while 1:
        try:
            recievedData = json.loads(convert(c.recv(1024).decode()))
        except (socket.error,socket.timeout):
            c.close()
            with conn_l:
                conns.remove((c,addr))
            with prnt_l:
                print("Closed connection from",addr)
            for ca in conns:
                try:
                    ca[0].send(json.dumps(["m",name+" left."]).encode())
                except socket.error:
                    continue
            return
        for data in recievedData:
            if data[0] == "h":
                try:
                    c.send(json.dumps(["h","#"]).encode())
                except socket.error:
                    c.close()
                    with conn_l:
                        conns.remove((c,addr))
                    with prnt_l:
                        print("Closed connection from",addr)
                    for ca in conns:
                        try:
                            ca[0].send(json.dumps(["m",name+" left."]).encode())
                        except socket.error:
                            continue #Will close socket later
                    return
            if data[0] == "m":
                with msg_l:
                    inMessages.append(data[1])

def mainThread(c,addr):
    msg_l = threading.Lock()
    inMessages = []

    try:
        name = json.loads(convert(c.recv(1024).decode()))[0][1]
    except (socket.error,socket.timeout):
        c.close()
        with conn_l:
            conns.remove((c,addr))
        with prnt_l:
            print("Closed connection from",addr)
        for ca in conns:
            try:
                ca[0].send(json.dumps(["m",str(addr[0])+" - "+str(addr[1])+" left."]).encode())
            except socket.error:
                continue #Recieve thread will get it

    for ca in conns:
        if ca[0] != c:
            try:
                ca[0].send(json.dumps(["m",name+" has connected."]).encode())
            except socket.error:
                continue #Recieve thread will get it

    with prnt_l:
        print(addr[0],"-",addr[1],"is",name)
    
    threading.Thread(target=recieveThread,args=(c,addr,name,msg_l,inMessages)).start()
    
    while 1:
        if inMessages != []:
            while inMessages != []:
                with msg_l:
                    returnValue = processData(inMessages.pop())
                returnValue = name + " >> " + returnValue
                with prnt_l:
                    print(returnValue)
                for ca in conns:
                    try:
                        ca[0].send(json.dumps(["m",returnValue]).encode())
                    except socket.error:
                        continue #Recieve thread will get it

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
print("Connection:\nHost -",host,"\nPort -",port,"\n")
s.listen(5)

prnt_l = threading.Lock()
conn_l = threading.Lock()
conns = []

while 1:
    c,addr = s.accept()
    c.settimeout(5.0)
    conns.append((c,addr))
    with prnt_l:
        print("Got connection from",addr)
    threading.Thread(target=mainThread,args=(c,addr)).start()
