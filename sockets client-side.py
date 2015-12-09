import socket

s = socket.socket()
host = "KCLCLMCT22"
port = 12346

s.connect((host,port))
while 1:
    data = input("Enter text: ")
    s.send(('~'+data).encode())
    recievedData = ""
    while recievedData.lstrip('#') == "":
        recievedData = s.recv(1024).decode()
        if recievedData == "":
            s.close()
            break #Needs to break both while loops

    recievedData = recievedData.lstrip('#')[1:]
    
    print("Server >>",recievedData)
    
