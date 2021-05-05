
from socket import *
import os
import signal
import simpy
import random
import time 
import math


class G:
    RANDOM_SEED = 33
    SIM_TIME = 50
    MU = 1
    LONG_SLEEP_TIMER = 1000000000




class Server_Process(object):
    def __init__(self, env, called_before):

        if not called_before:
            self.env = env
            self.queue_dict = {}
            self.server_busy = False 
            
            for i in range(0, 30):
                self.queue_dict[i] = []

            self.called_before = True
            #run the server here 
            self.action = env.process(self.run())



    def run(self):

        while 1:

            print("yielding server")
            print()

            yield self.env.timeout(1)

            #except simpy.Interrupt:
            print("servicing packet")
            print("current time: " + str(self.env.now))

            for key, val in self.queue_dict.items():
                print("process: " + str(key))
                for i in range(0, len(val)):
                    print("packet: " + str(val[i].arrival_time))
                
                print()



            #queue for current process
            """while len(queue) > 0:

                packet = queue.pop(0)
                print("the packet number: " + str(packet.identifier))
                print("the arrival time: " + str(packet.arrival_time))
                print()
                
                yield self.env.timeout(random.expovariate(G.MU))

            #we have emptied the queue for this process
            server_busy = False
            print("queue emptied for process: " + str(i))"""


            self.server_busy = False 
                


class Arrival_Process(object):
    def __init__(self, env, arrival_rate, server_process, called_before):

        if not called_before:
            self.env = env
            self.arrival_rate = arrival_rate
            self.server_process = server_process
            self.packet_number = 0
            #self.arrival_count = [0]*30
            #self.arrival_dict = {}


            for i in range(0, 30):
                self.action = env.process(self.run(i))

        self.called_before = True



    def run(self, i):

        while True:
            yield self.env.timeout(random.expovariate(self.arrival_rate))

            #create and enqueue new packet
            self.packet_number += 1
            arrival_time = self.env.now
            new_packet = Packet(self.packet_number,arrival_time)
            
            if not self.server_process.queue_dict[i]:
                self.server_process.queue_dict[i] = [new_packet]
            else:
                self.server_process.queue_dict[i].append(new_packet)

            print("the queue size for process " + str(i) + " is now: " + str(len(self.server_process.queue_dict[i])))
            print()


            #check whether server busy to start transmitting packets
            if self.server_process.server_busy == False:
                self.server_process.server_busy = True
                #wait for some time in order to let the process yield again
                #yield self.env.timeout(15)
                #self.server_process.action.interrupt()
                







class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time



def main():

    num_hosts = 30
    called_before = False
    arrival_called_before = False 

    for arrival_rate in [0.5]:
        env = simpy.Environment()
        server_process = Server_Process(env, called_before)

        arrival = Arrival_Process(env, arrival_rate, server_process, arrival_called_before)
        env.run(until=G.SIM_TIME)
    signal.pause()



main()
