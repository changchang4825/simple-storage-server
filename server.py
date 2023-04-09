from socket import *
import os
from datetime import datetime
from _thread import *
import time

def run(connectionSocket):
    id = ""
    startTime = ""

    try:
        msg = 'HTTP/1.0 200 OK\r\n'
        sentence = b''
        while True:
            part = connectionSocket.recv(1024)
            sentence += part
            if len(part) < 1024:
                break

        if b'/favicon.ico' in sentence:
            connectionSocket.close()
            return

        if b'Content-Disposition:' in sentence:
            if b'Cookie:' not in sentence:
                msg = 'HTTP/1.0 403 Forbbiden\r\n\r\n' + open('./403.html', 'r').read()
                connectionSocket.send(msg.encode())
                connectionSocket.close()
                return

            id = sentence.split(b'Cookie: id=')[1].split(b';')[0].decode()
            fileName = sentence.split(b'filename="')[1].split(b'"')[0].decode()
            bytes = sentence.split(b'Content-Type:')[2].split(b'\r\n\r\n')[1].split(b'\r\n------WebKitFormBoundary')[0]
            submittedFile = open(id + '/' + fileName, 'wb')
            submittedFile.write(bytes)

            file = open('storage.html', 'r')
            html = file.read().replace("user1", id)
            fileList = os.listdir(id)
            idx = html.find("<ul>\n")
            li = ""
            for userFile in fileList:
                li += "<li>" + userFile + '''\n<a href="''' + id + "/" + userFile + '''" download><button>Download</button></a><a href="" ping="''' + id + "/" + userFile + '''">\n<button>Delete</button></a></li>\n'''
            html = html[:idx + 5] + li + html[idx + 5:]
            msg += '\r\n' + html
            # print(sentence)
            print("File is uploaded")

        else:
            sentence = sentence.decode()

            if not sentence:
                connectionSocket.close()
                return

            print(sentence)
            sentenceList = sentence.split("\r\n")
            fileName = sentenceList[0].split(" ")[1]
            
            if 'PING' in sentenceList[-1]:
                isThereCookie = False
                for x in sentenceList:
                    if 'Cookie:' in x:
                        isThereCookie = True
                        break

                if isThereCookie == False:
                    msg = 'HTTP/1.0 403 Forbbiden\r\n\r\n'
                    connectionSocket.send(msg.encode())
                    connectionSocket.close()
                    return

                os.remove('.' + fileName)
                connectionSocket.close()
                return

            if fileName == '/index.html':
                file = open('.' + fileName, 'r')
                msg += '\r\n' + file.read()

            elif fileName == '/cookie.html':
                file = open('.' + fileName, 'r')
                isThereCookie = False
                for x in sentenceList:
                    if 'Cookie:' in x:
                        id, startTime = x.split(';')
                        id = id.split(' ')[1].split('=')[1]
                        startTime = startTime.split('=')[1]
                        isThereCookie = True
                        break

                if isThereCookie == False:
                    msg = 'HTTP/1.0 403 Forbbiden\r\n\r\n' + open('./403.html', 'r').read()

                else:
                    html = file.read().replace("user1", id)
                    seconds = (datetime.now() - datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S.%f')).seconds
                    html = html.replace("120", str(120 - seconds))
                    msg += '\r\n' + html

            elif fileName == '/storage.html':
                file = open('.' + fileName, 'r')
                if 'id=' in sentenceList[-1]:
                    id = sentenceList[-1].split('&')[0].split('=')[1]
                    startTime = datetime.now()
                    os.makedirs(id, exist_ok = True)
                    msg += "Set-Cookie: id=" + id + "; Max-Age=120\r\n"
                    msg += "Set-Cookie: start_time=" + str(datetime.now()) + "; Max-Age=120\r\n\r\n"

                else:
                    isThereCookie = False
                    for x in sentenceList:
                        if 'Cookie:' in x:
                            id = x.split(';')[0].split(' ')[1].split('=')[1]
                            isThereCookie = True
                            break
                    
                    if isThereCookie == False:
                        msg = 'HTTP/1.0 403 Forbbiden\r\n\r\n' + open('./403.html', 'r').read()
                        connectionSocket.send(msg.encode())
                        connectionSocket.close()
                        return

                html = file.read().replace("user1", id)
                fileList = os.listdir(id)
                idx = html.find("<ul>\n")
                li = ""
                for userFile in fileList:
                    li += "<li>" + userFile + '''\n<a href="''' + id + "/" + userFile + '''" download><button>Download</button></a><a href="" ping="''' + id + "/" + userFile + '''">\n<button type="submit">Delete</button></a></li>\n'''

                html = html[:idx + 5] + li + html[idx + 5:]
                msg += '\r\n' + html

            else:
                isVaild = False
                for x in sentenceList:
                    if 'Cookie:' in x:
                        if x.split(';')[0].split(' ')[1].split('=')[1] == fileName.split('/')[1]:
                            isVaild = True
                            break
                
                if isVaild == False:
                    msg = 'HTTP/1.0 403 Forbbiden\r\n\r\n' + open('./403.html', 'r').read()
                    connectionSocket.send(msg.encode())
                    connectionSocket.close()
                    return

                file = open('.' + fileName, 'rb')
                msg += '\r\n'
                msg = msg.encode() + file.read()
                connectionSocket.send(msg)
                connectionSocket.close()
                return

        connectionSocket.send(msg.encode())

    except Exception as e:
        print(e)

    connectionSocket.close()

serverPort = 10090
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')

while True:
    connectionSocket, addr = serverSocket.accept()
    time.sleep(.25)
    start_new_thread(run, (connectionSocket, ))
    
serverSocket.close()