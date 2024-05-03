import os, sys
import hashlib, base64
from socket import *


class Client():
    def __init__(self,serverName,serverPort):
        self.serverName = serverName
        self.serverPort = serverPort
        self.list=[]
      
        
    def create_socket(self):
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        while True:
            try:
                userInput = input("\n명령어 종류:\n\n- get [파일 이름]\n- put [파일 이름]\n- msg [전송할 메세지]\n- list\n- clist\n- exit\n\n입력하시오:").split()
                cmd = userInput[0]
                
                clientSocket.sendto(bytes(cmd, encoding='utf-8'), (self.serverName, self.serverPort))
                if cmd == 'get':
                    try:
                        fileName = userInput[1]
                        self.getFile(fileName, clientSocket)
                    except IndexError:
                        print("올바른 양식이 아님")
                elif cmd == 'msg':
                    try:
                        newlist=userInput[1:]
                        newvalue=" ".join(newlist)
                        clientSocket.sendto(bytes(newvalue, encoding='utf-8'),(self.serverName,self.serverPort))
                    except IndexError:
                        print("올바른 양식이 아님")        
                elif cmd == 'put':
                    try:
                        fileName = userInput[1]
                        self.putFile(fileName, clientSocket)
                    except IndexError:
                        print("올바른 양식이 아님")
                elif cmd == 'list':
                    if len(userInput)==1:               
                        self.listFiles(clientSocket)
                    else:
                        print("올바른 양식이 아님")
                elif cmd == 'clist':
                    if len(userInput)==1:               
                        files = os.listdir()
                        print("Files in current directory:")
                        for file in files:
                            print(file)  
                    else:
                        print("올바른 양식이 아님")
                elif cmd == 'exit':
                    if len(userInput)==1:               #indicates only the command name 'exit' is given
                        self.exit()
                    else:
                        print("올바른 양식이 아님")
                else:
                    msg = self.recvMsgAndPrintToConsole(clientSocket)
            except KeyboardInterrupt:
                clientSocket.close()
                sys.exit()

    def getFile(self, fileName, clientSocket):
        #파일이름을 서버에게 전송
        fileExistence = self.recvMsgAndPrintToConsole(clientSocket) 
        if 'not' not in fileExistence:
            #서버로 부터 파일 사이즈를 받음
            #서버로 부터 받은 파일 사이즈를 클라이언트창에 출력
            hashList = []       
            with open("Received_" + fileName, 'wb') as f:
                totalRecv = 0
                while #totalRecv가 파일 사이즈가 될 때 까지
                    try:
                        encodedData, serverAddress = clientSocket.recvfrom(1500)
                    except:
                        continue
                    data = base64.b64decode(encodedData.split(b"//")[0])
                    recvHashedData = encodedData.split(b"//")[1]
                    if #헤시리스트를 보고 없으면 중복되지 않은 데이터
                        #리스트에 추가
                        dupFlag = 0         
                    else: #리스트에 이미 있음
                        dupFlag = 1         
                        
                    generatedHashedData = self.getHashedData(data)
                    
                    if #중복되지 않고 recvHashedData와 generatedHashedData 동일
                        #데이터 write
                        #데이터 길이 측정
                        #ack 전송
                    elif #중복되고 recvHashedData와 generatedHashedData 동일
                        #ACK가 분실되어 중복 패킷이 수신되었으므로 데이터를 작성하지 않고 ACK를 다시 전송
                    
                    print("{0:.2f}% Done".format((totalRecv)/float(fileSize) * 100))
            

    def putFile(self, fileName, clientSocket):
        clientSocket.settimeout(1) #타임 아웃 시간
        clientSocket.sendto(bytes(fileName, encoding='utf-8'), (self.serverName, self.serverPort)) # 파일 이름 전송
        if os.path.isfile(fileName): #파일 존재
            #서버의 sendToClient함수와 유사
            print('d')
            
            
            #완성해주세요
            
            
            
            
            
        
            
        else:
            print("File {} not found!".format(fileName))    
            clientSocket.sendto(b"Requested file not found!", (self.serverName, self.serverPort))

    

    def listFiles(self, clientSocket):
        print("\n현재 서버 파일 리스트 :\n")
        data, serverAddress = clientSocket.recvfrom(1024)
        numberOfFiles = int(data.decode('utf-8'))
        while numberOfFiles > 0:
            fileName, serverAddress = clientSocket.recvfrom(1024)
            print(fileName.decode('utf-8'))
            numberOfFiles -= 1

    def exit(self):
        print("서버 종료 명령어 전송 중")

    def getHashedData(self, data):
        m = hashlib.sha256()
        m.update(data)
        return m.digest()

    def recvMsgAndPrintToConsole(self, socket):
        message, serverAddress = socket.recvfrom(1500)
        return message.decode('utf-8')

if __name__=='__main__':
    host = input("Host: ")
    port = int(input("Port: "))
               
    client = Client(host, port)
    client.create_socket()