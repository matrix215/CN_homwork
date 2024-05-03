import sys, os
import socket
from socket import *
import hashlib, base64


class Server():
    def __init__(self,serverPort):
        self.serverPort = serverPort

    def create_socket(self):
        server = socket(AF_INET, SOCK_DGRAM)
        server.bind(('', self.serverPort))
        print('The server is ready to receive from the port.', self.serverPort)
        while True:
            try:
                command, clientAddress = server.recvfrom(1024)
            except:
                continue
            if (command.decode('utf-8')) == 'get':
                fileName, clientAddress = server.recvfrom(1024)
                self.sendToClient(server, fileName.decode('utf-8'), clientAddress)
            elif (command.decode('utf-8')) == 'put':
                fileName, clientAddress = server.recvfrom(1024)
                self.getFromClient(server, fileName.decode('utf-8'), clientAddress)
            elif (command.decode('utf-8')) == 'msg':
                data, clientAddress = server.recvfrom(1024)
                
                if data != "":
                    print("Received message"  + ":" + str(data.decode("utf-8")))
            elif (command.decode('utf-8')) == 'list':
                self.sendListOfFiles(server, clientAddress)
            elif (command.decode('utf-8')) == 'exit':
                self.exit(server, clientAddress)
            else:
                server.sendto(command + b"- It's an unknown command.", clientAddress)

    def sendToClient(self, server, fileName, clientAddress):
        server.settimeout(1) 
        if os.path.isfile(fileName):
            #서버 내부에서 해당 파일 존재하고 클라이언트 전송한다는 메세지가 서버에 표시
            #해당 파일 존재하고 다운로드가 시작된다고 클라이언트에게 메세지 전송
            #os.path.getsize명령어를 통해서 파일 사이즈를 클라이언트에게 전송
            with open(fileName, 'rb') as f:
                bytesToSend = f.read(1024) # 파일 읽음 
                ackMessage = b"ACK"     #udp임으로 그냥 파일 보냄
                while bytesToSend and ackMessage: 
                    #제공된 hash 함수를 이용하여 암호화
                    #base64.b64encode 이용하여 파일을 인코딩하고 헤시된 내용을 //로 결합하여 클라이언트에게 전송 예(encoded data+'//'+hashed)
                    #
                    try:
                        ackMessage, clientAddress = server.recvfrom(1024)
                        bytesToSend = f.read(1024)
                    except: 
                        continue
            print("전송 완료!")
            #클라이언트에게 다운로든 완료함이라는 메세지 전송
        else:
            print("File {} not found!".format(fileName))
            #요청한 파일이 없다고 클라이언트에게 메세지 전송

    def getFromClient(self, server, fileName, clientAddress):
        fileExistence = self.recvMsgAndPrintToConsole(server) # 파일 존재 여부를 파악
        if 'not' not in fileExistence:
            fileSize, clientAddress = server.recvfrom(1024)
            hashList = []  # a list to keep track of arrived packets
            with open("Received_" + fileName, 'wb') as f:
                totalRecv = 0
                #클라이언트 getFile함수와 유사
                
                #완성하세요
                
                
                
                
                
                
                
                
                    print("{0:.2f}% Done".format((totalRecv) / float(fileSize) * 100))
            

    

    def sendListOfFiles(self, server, clientAddress):
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        server.sendto(bytes(str(len(files)), encoding='utf-8'), clientAddress)
        for file in files:
            server.sendto(bytes(file, encoding='utf-8'), clientAddress)

    def exit(self, server, clientAddress):
        server.sendto(b"Server closed successfuly", clientAddress)
        server.close()
        print("Server closed successfully")
        sys.exit()

    def getHashedData(self, data):
        m = hashlib.sha256()
        m.update(data)
        return m.digest()

    def recvMsgAndPrintToConsole(self, socket):
        message, clientAddress = socket.recvfrom(1500)
        print(message.decode('utf-8'))
        return message.decode('utf-8')

if __name__=='__main__':
    host = input("Host: ")
    port = int(input("Port: "))
    
    if int(port) > 5000:
        server=Server(port)
        server.create_socket()
    else:
        print("Invalid port number. Port number must be selected at least 5000")
