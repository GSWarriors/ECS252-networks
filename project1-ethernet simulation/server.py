# simple (non-concurrent) TCP server example
from socket import *
import os 
import signal



def new_host(i, listeningSocket):
    pid = os.fork()
  

    if pid > 0:
        print("parent process, returning back to loop")
        return pid
    else:
        print("created new child process with id: " + str(os.getpid()))
        while 1:
            child_connectionsocket, addr = listeningSocket.accept()
            #handle the incoming request
            print("handling incoming request from client with host: " + str(i))

            #close child connection after its handled       
            child_connectionsocket.close()





def main():
    serverPort = 12000
    listeningSocket = socket(AF_INET, SOCK_STREAM)
    print(listeningSocket)
    listeningSocket.bind(('', serverPort))
    listeningSocket.listen(1)
    print('Server ready, socket', listeningSocket.fileno(), 'listening on localhost :', serverPort)

    num_hosts = 30

    #don't need to have parent in while loop, just needs to sleep.
    #the preforked children handle the connections

    for i in range(0, num_hosts):
        new_host(i, listeningSocket)

    signal.pause()



main()




