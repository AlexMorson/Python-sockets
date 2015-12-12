import threading
import socket
import json
import sys
import msvcrt

def convert(data):
	data = list(data)
	for char in range(len(data)-1,-1,-1):
		if data[char] == '[':
			data.insert(char,',')
	return "".join(['[']+data[1:]+[']'])

def recieveThread(s):
    while 1:
        try:
            recievedData = json.loads(convert(s.recv(1024).decode()))
        except socket.error:
            s.close()
            with prnt_l:
                print("You were disconnected.")
            running = False
            return
        except socket.timeout:
            s.close()
            with prnt_l:
                print("Lost connection to server.")
            running = False
            return
        for data in recievedData:
            if data[0] == "h":
                try:
                    s.send(json.dumps(["h","#"]).encode())
                except socket.error:
                    s.close()
                    with prnt_l:
                        print("You were disconnected.")
                    running = False
                    return
            if data[0] == "m":
                with msg_l:
                    inMessages.append(data[1])

s = socket.socket()
host = socket.gethostname()
port = 12346
s.connect((host,port))
s.settimeout(5.0)
print("Connection:\nHost -",host,"\nPort -",port,"\n")

t = threading.Thread(target=recieveThread,args=(s,)).start()

inMessages = []
msg_l = threading.Lock()
prnt_l = threading.Lock()

userText = []
youText = "You >> "
print(youText,end=" \r")

running = True
while running:
    if inMessages != []:
        while inMessages != []:
            with msg_l:
                data = inMessages.pop()
            with prnt_l:
                print(str(data)+" "*len(youText))
                message = youText+"".join(userText)
                print(message,end=" \r")
                

    while msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b'\x08':#Backspace
            userText = userText[:-1]
        elif key == b'\r':#Return
            try:
                s.send(json.dumps(["m","".join(userText)]).encode())
            except socket.error:
                s.close()
                running = False
            userText = []
        else:
            try:
                userText.append(key.decode())
            except UnicodeDecodeError:
                continue
        
        message = youText+"".join(userText)
        with prnt_l:
                print(message,end=" \r")
