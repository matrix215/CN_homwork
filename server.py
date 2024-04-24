import argparse
import sys, os
import socket
from socket import *
import hashlib, base64, binascii


class Server():
    def __init__(self,serverPort):
        self.serverPort = serverPort

    def create_socket(self):
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(('', self.serverPort))
        print('The server is ready to receive at port', self.serverPort)
        while True:
            try:
                cmd, clientAddress = serverSocket.recvfrom(1024)
            except:
                continue
            if (cmd.decode('utf-8')) == 'get':
                fileName, clientAddress = serverSocket.recvfrom(1024)
                self.sendFileToClient(serverSocket, fileName.decode('utf-8'), clientAddress)
            elif (cmd.decode('utf-8')) == 'put':
                fileName, clientAddress = serverSocket.recvfrom(1024)
                self.getFileFromClient(serverSocket, fileName.decode('utf-8'), clientAddress)
            elif (cmd.decode('utf-8')) == 'msg':
                data, clientAddress = serverSocket.recvfrom(1024)
                if data != "":
                    print("message"  + ":" + str(data.decode("utf-8")))
                
                #self.getFileFromClient(serverSocket, fileName.decode('utf-8'), clientAddress)
            
            elif (cmd.decode('utf-8')) == 'rename':
                try:
                    fileName, clientAddress = serverSocket.recvfrom(1024)
                    newFileName, clientAddress = serverSocket.recvfrom(1024)
                except:
                    continue
                self.renameFile(serverSocket, fileName.decode('utf-8'), newFileName.decode('utf-8'))
            elif (cmd.decode('utf-8')) == 'list':
                self.sendListOfFiles(serverSocket, clientAddress)
            elif (cmd.decode('utf-8')) == 'exit':
                self.exit(serverSocket, clientAddress)
            else:
                serverSocket.sendto(cmd + b"- Unknown command. Not understood by the server!", clientAddress)

    def sendFileToClient(self, serverSocket, fileName, clientAddress):
        serverSocket.settimeout(1)
        if os.path.isfile(fileName):
            print("File {} exists! Sending to the client...".format(fileName)) #서버 내부에서 파일 존재 확인
            serverSocket.sendto(b"Requested file found! Starting download...", clientAddress) # 클라이언트에게 파일 다운로드 알림
            serverSocket.sendto(bytes(str(os.path.getsize(fileName)), encoding='utf-8'),clientAddress) #파일 사이즈 전송
            with open(fileName, 'rb') as f:
                bytesToSend = f.read(1024) # 파일 읽음 
                ackMessage = b"ACK"     #udp임으로 그냥 파일 보냄
                while bytesToSend and ackMessage:
                    hashedData = self.getHashedData(bytesToSend) # 암호화
                    serverSocket.sendto(base64.b64encode(bytesToSend) + b"||||" + hashedData, clientAddress)
                    #joining encoded data and its hashed content by "||||", to send the combined data together
                    try:## 클라이언트에게 ack 메세지 기다림
                        ackMessage, clientAddress = serverSocket.recvfrom(1024)
                        bytesToSend = f.read(1024)
                    except: 
                        #ack 못받음
                        continue
            print("전송 완료!")
            serverSocket.sendto(b"Download complete!", clientAddress)
        else:
            print("File {} not found!".format(fileName))
            serverSocket.sendto(b"Requested file not found!", clientAddress)

    def getFileFromClient(self, serverSocket, fileName, clientAddress):
        fileExistence = self.recvMsgAndPrintToConsole(serverSocket) # 파일 존재 여부를 파악
        if 'not' not in fileExistence:
            fileSize, clientAddress = serverSocket.recvfrom(1024)
            hashList = []  # a list to keep track of arrived packets
            with open("Received_" + fileName, 'wb') as f:
                totalRecv = 0
                while totalRecv < int(fileSize.decode('utf-8')):
                    try:
                        encodedData, clientAddress = serverSocket.recvfrom(1500)
                    except:
                        continue
                    data = base64.b64decode(encodedData.split(b"||||")[0])
                    recvHashedData = encodedData.split(b"||||")[1]
                    if recvHashedData not in hashList:
                        hashList.append(recvHashedData)
                        dupFlag = 0         #Not a duplicate packet, hence appended to the list
                    else:
                        dupFlag = 1         #flag for keeping track of a duplicate packet
                    generatedHashedData = self.getHashedData(data)
                    if recvHashedData == generatedHashedData and dupFlag == 0:
                        f.write(data)
                        totalRecv += len(data)
                        serverSocket.sendto(b"ACK", clientAddress)
                    elif recvHashedData == generatedHashedData and dupFlag == 1:
                        #a duplicate packet was received because ACK was lost, so we need not write the data, but send ACK again
                        serverSocket.sendto(b"ACK", clientAddress)
                    print("{0:.2f}% Done".format((totalRecv) / float(fileSize) * 100))
            downloadMessage = self.recvMsgAndPrintToConsole(serverSocket)

    

    def sendListOfFiles(self, serverSocket, clientAddress):
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        serverSocket.sendto(bytes(str(len(files)), encoding='utf-8'), clientAddress)
        for file in files:
            serverSocket.sendto(bytes(file, encoding='utf-8'), clientAddress)

    def exit(self, serverSocket, clientAddress):
        serverSocket.sendto(b"Server closed successfuly", clientAddress)
        serverSocket.close()
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
        print("Incorrect port number. You should select port numbers > 5000")
