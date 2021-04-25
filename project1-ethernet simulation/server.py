# simple (non-concurrent) TCP server example
from socket import *
import os 


def main():
    serverPort = 12001
    listeningSocket = socket(AF_INET, SOCK_STREAM)
    print(listeningSocket)
    listeningSocket.bind(('', serverPort))
    listeningSocket.listen(1)
    print('Server ready, socket', listeningSocket.fileno(), 'listening on localhost :', serverPort)

    num_hosts = 10
    count = 0

    while 1:
        connectionSocket, addr = listeningSocket.accept()
        pid = os.fork()

        if pid > 0:
            print("i am the parent process.")
            print("process ID: " + str(os.getpid()))
            print()
        
        else:
            print("i am child process.")
            print("process ID: " + str(os.getpid()))
            print()
            listeningSocket.close()
            print("handling incoming request from connected socket")
            os._exit(0)
        

        print("closing connected socket.")
        connectionSocket.close()



main()




        #firstName = connectionSocket.recv(1024)
        #print('Got connection on socket', connectionSocket.fileno(), 'from', addr[0], ':', addr[1])
        #connectionSocket.send(str.encode('Hi ' + bytes.decode(firstName) + '!'))
        #lastName = connectionSocket.recv(1024)
        #connectionSocket.send(str.encode('Hello ' + bytes.decode(firstName) + ' ' + bytes.decode(lastName)+ '!'))
        #print('Closing socket', connectionSocket.fileno())




