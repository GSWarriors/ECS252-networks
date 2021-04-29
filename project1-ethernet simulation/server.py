
from socket import *
import os 
import signal
import simpy
import random


class G:
    RANDOM_SEED = 33
    SIM_TIME = 100000
    MU = 1
    LONG_SLEEP_TIMER = 1000000000



class Server_Process(object):
    def __init__(self, env, called_before):
       

        if not called_before:
            self.env = env
            self.queue = []     #the buffer 
            self.server_busy = False 
            self.processes = []

            for i in range(0, 10):
                self.action = env.process(self.new_host(i))
                self.processes.append(self.action)
            
            print("processes list: " + str(self.processes))

        self.called_before = True 



    def new_host(self, i):
        while 1:
            try: 
                print("yielding process: " + str(i))
                print()
                yield self.env.timeout(G.LONG_SLEEP_TIMER)

            except simpy.Interrupt:
                print("process " + str(i) + " has been interrupted by packet")
                print("servicing packet")
                


class Arrival_Process(object): 
    def __init__(self, env, arrival_rate, server_process):
        
        self.env = env
        self.arrival_rate = arrival_rate
        self.server_process = server_process
        self.action = env.process(self.run())
    
    def run(self):
        #count = 10
        for i in range(0, 10):
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            self.server_process.processes[i].interrupt()


        """while True:
             # Infinite loop for generating packets
            yield self.env.timeout(random.expovariate(self.arrival_rate))

            if self.server_process.server_busy == False:
                #self.server_process.server_busy = True
                self.server_process.action.interrupt()

                print("new client arriving")
                print()"""
            






def main():
 
    num_hosts = 30
    called_before = False 

    for arrival_rate in [0.5]:
        env = simpy.Environment()
        server_process = Server_Process(env, called_before)
        arrival = Arrival_Process(env, arrival_rate, server_process)
        env.run(until=G.SIM_TIME)

        
        #arrival = Arrival_Process(env, arrival_rate, server, action)
    signal.pause()



main()







"""class Arrival_Process(object): 
    def __init__(self, env, arrival_rate, server_process):
        
        self.env = env
        self.arrival_rate = arrival_rate
        self.server_process = server_process
        self.action = env.process(self.run())
    
    def run(self):
        while True:
             # Infinite loop for generating packets
            yield self.env.timeout(random.expovariate(self.arrival_rate))

            if self.server_process.server_busy == False:
                self.server_process.server_busy = True
                self.server_process.action.interrupt()

                print("new client arriving")
                print()

                serverName = 'localhost'
                serverPort = 12010
                clientSocket = socket(AF_INET, SOCK_STREAM)
                clientSocket.connect((serverName, serverPort))
                clientSocket.close()"""



