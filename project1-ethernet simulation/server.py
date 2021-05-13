
from socket import *
import os
import signal
import simpy
import random
import time 
import math
import threading


class G:
    RANDOM_SEED = 33
    SIM_TIME = 80
    MU = 1
    LONG_SLEEP_TIMER = 1000000000




class Server_Process(object):
    def __init__(self, env, called_before):

        if not called_before:
            self.env = env
            self.process_dict = {}
            self.server_busy = False 
            self.retransmitting = False 
            
            for i in range(0, 10):
                self.process_dict[i] = [None, [], self.retransmitting]

            self.called_before = True
            #run the server here 
            self.action = env.process(self.run())



    def run(self):

        while 1:

            print("yielding server")
            print()

            yield self.env.timeout(1)

            print("current time: " + str(self.env.now))

            interrupt_list = []

            for key, val in self.process_dict.items():
                print("process: " + str(key))

                #checking the queue. pop from the queues
                curr_queue = val[1]
                if len(curr_queue) > 0: 
                    packet = curr_queue.pop(0)
                    print("popped packet from process: " + str(key))
                    print("packet arrived at: " + str(packet.arrival_time))
                    interrupt_list.append((key, val[0], packet))
                    
            print()

          

            #interrupt the processes that have packets that were dequeued 
            if len(interrupt_list) >= 2:
                print("interrupt list: " + str(interrupt_list))

                for i in range(0, len(interrupt_list)):
                    curr_process = interrupt_list[i][0]
                    
                    while self.process_dict[curr_process][2] == True:
                        print("already retransmitting, wait")
                        yield self.env.timeout(1)

                    self.process_dict[curr_process][2] = True
                    interrupt_list[i][1].interrupt()
                
            else:
                #yield self.env.timeout(random.expovariate(G.MU))
                print("packet serviced")
            
            self.server_busy = False




class Arrival_Process(object):
    def __init__(self, env, arrival_rate, server_process, called_before):

        if not called_before:
            self.env = env
            self.arrival_rate = arrival_rate
            self.server_process = server_process
            self.packet_number = 0
  

            for i in range(0, 10):
                self.action = env.process(self.run(i))
                self.server_process.process_dict[i][0] = self.action

        self.called_before = True




    def run(self, i):

        while True:

            try: 
                yield self.env.timeout(random.expovariate(self.arrival_rate))

                #create and enqueue new packet
                self.packet_number += 1
                arrival_time = self.env.now
                new_packet = Packet(self.packet_number,arrival_time)
                
                if not self.server_process.process_dict[i][1]:
                    self.server_process.process_dict[i][1] = [new_packet]
                else:
                    self.server_process.process_dict[i][1].append(new_packet)


                #check whether server busy to start transmitting packets
                if self.server_process.server_busy == False:
                    self.server_process.server_busy = True
                    #wait for some time in order to let the process yield again




            except simpy.Interrupt:

                curr_process = self.server_process.process_dict[i]
                retransmit = random.randint(0, 1)

                #retransmit packet for each process with a 50% probability by adding to the queue again 
                #reduce packet number by 1 because retransmitting that packet
                if retransmit == 1:
                    self.packet_number -= 1
                    arrival_time = self.env.now
                    new_packet = Packet(self.packet_number,arrival_time)
                    print("collision packet for process: " + str(i) + " has been resent with arrival time: " 
                    + str(arrival_time))
                    
                    #add to queue again
                    curr_queue = curr_process[1]

                    if not curr_queue:
                        curr_queue = [new_packet]
                    else:
                        curr_queue.append(new_packet)
                
                    #check whether server busy to start transmitting packets
                    if self.server_process.server_busy == False:
                        self.server_process.server_busy = True
                else:

                    #wait for next time slot to retransmit if not in threshold value
                    while retransmit != 1:
                        yield self.env.timeout(1)
                        retransmit = random.randint(0, 1)
                    
                    #once this loop is broken, then retransmit as usual - make this part into a function
                    self.packet_number -= 1
                    arrival_time = self.env.now
                    new_packet = Packet(self.packet_number,arrival_time)
                    print("multiple collision packet for process: " + str(i) + " has been resent with arrival time: " 
                    + str(arrival_time))
                    
                    curr_queue = curr_process[1]
                    #add to queue again
                    if not curr_queue:
                        curr_queue = [new_packet]
                    else:
                        curr_queue.append(new_packet)
                
                    #check whether server busy to start transmitting packets
                    if self.server_process.server_busy == False:
                        self.server_process.server_busy = True

                curr_process[2] = False 







class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time



def main():

    num_hosts = 30
    called_before = False
    arrival_called_before = False 

    for arrival_rate in [0.09]:
        env = simpy.Environment()
        server_process = Server_Process(env, called_before)

        arrival = Arrival_Process(env, arrival_rate, server_process, arrival_called_before)
        env.run(until=G.SIM_TIME)
    signal.pause()



main()
