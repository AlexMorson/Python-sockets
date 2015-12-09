import socket

s = socket.socket()
host = socket.gethostname()
port = 12346
s.bind((host,port))
print("Host:",host,"Port:",port)

def getConnection():
    c,addr = s.accept()
    print("Got connection from",addr)
    c.settimeout(1.0)
    return c,addr

s.listen(5)
c,addr = getConnection()

while 1:
    data = ""
    while data == "":
        try:
            data = c.recv(1024).decode()
        except (socket.timeout,socket.error):
            try:
                uh = c.send("#".encode())
            except socket.error:
                c.close()
                print(addr,"has disconnected.")
                c,addr = getConnection()
    data = data[1:]


    if data[:5] == "eval ":
        try:
            returnValue = data[5:] + " => " + str(eval(data[5:]))
        except Exception as e:
            returnValue = data[5:] + " => " + str(type(e).__name__)
    else:
        returnValue = data
    
    print("Client ("+str(addr)+") >> ",data)
    if data == "quit":
        c.close()
    try:
        c.send(("@"+returnValue).encode())
    except socket.error:
        print(addr,"has disconnected.")
        c,addr = getConnection()
s.close()
