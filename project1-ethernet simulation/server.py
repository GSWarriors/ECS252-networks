
from socket import *
import os
import signal
import simpy
import random
import time 
import math


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
            
            for i in range(0, 5):
                self.process_dict[i] = [None, []]

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
            #check here if any of the process queues have a packet that just arrived in the last slot 
            for key, val in self.process_dict.items():

                print("process: " + str(key))

                for packet in val[1]:
                    if self.env.now - packet.arrival_time <= 1:
                        print("arrival time: " + str(packet.arrival_time))

                        if key not in interrupt_list:
                            interrupt_list.append((key, val[0]))
                            #print("a packet in process " + str(key) + " has just arrived, servicing.")
                            #print("the arrival time: " + str(packet.arrival_time))
                            #print()
                        #else:
                            #print("packet from same process " + str(key) + " has arrived.")
                print()
             

            

            #check for collision and remove that packet from queues of both processes
            #if we actually have a collision
            process_freq = {}

            if len(interrupt_list) >= 2:
                print("interrupt list: " + str(interrupt_list))

                for index, tuple in enumerate(interrupt_list):
                    key = tuple[0]
                    reference = tuple[1]
                    
                    if key not in process_freq:
                        process_freq[key] = 1
                    else:
                        process_freq[key] += 1
            
                can_interrupt = self.check_processes(process_freq)



                if can_interrupt:
                    for i in range(0, len(interrupt_list)):
                        curr_queue = self.process_dict[interrupt_list[i][0]][1]
                        removed_packet = curr_queue.pop()
                        print("removed packet from process " + str(interrupt_list[i][0]) + " with arrival time: " + 
                        str(removed_packet.arrival_time))
                        interrupt_list[i][1].interrupt()

            
            self.server_busy = False 

    

        
    def check_processes(self, process_freq):

        check_val = 1
        can_interrupt = True

        for val in process_freq.values():
            if val != check_val:
                can_interrupt = False 
        
        #if can_interrupt:
        #    print("we can interrupt these processes")
        #else:
        #    print("can't interrupt processes. they have at least one of the same process listed twice")
        
        return can_interrupt





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



    """for key, val in self.process_dict.items():
        print("process: " + str(key))
        
        for packet in val[1]:
            print("arrival time: " + str(packet.arrival_time))

        print()

    print()"""

                


class Arrival_Process(object):
    def __init__(self, env, arrival_rate, server_process, called_before):

        if not called_before:
            self.env = env
            self.arrival_rate = arrival_rate
            self.server_process = server_process
            self.packet_number = 0
  

            for i in range(0, 5):
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

                #retransmit = random.randint(0, 1)
                retransmit = random.uniform(0, 1)

                #retransmit packet for each process with a 50% probability by adding to the queue again 
                #reduce packet number by 1 because retransmitting that packet
                if retransmit <= 0.8:
                    self.packet_number -= 1
                    arrival_time = self.env.now
                    new_packet = Packet(self.packet_number,arrival_time)
                    print("collision packet for process: " + str(i) + " has been resent with arrival time: " 
                    + str(arrival_time))
                    
                    #add to queue again
                    if not self.server_process.process_dict[i][1]:
                        self.server_process.process_dict[i][1] = [new_packet]
                    else:
                        self.server_process.process_dict[i][1].append(new_packet)
                
                    #check whether server busy to start transmitting packets
                    if self.server_process.server_busy == False:
                        self.server_process.server_busy = True
                else:
                    #wait for next time slot to retransmit if not in threshold value
                    while retransmit > 0.8:
                        yield self.env.timeout(1)
                        retransmit = random.uniform(0, 1)
                    
                    #once this loop is broken, then retransmit as usual - make this part into a function
                    self.packet_number -= 1
                    arrival_time = self.env.now
                    new_packet = Packet(self.packet_number,arrival_time)
                    print("multiple collision packet for process: " + str(i) + " has been resent with arrival time: " 
                    + str(arrival_time))
                    
                    #add to queue again
                    if not self.server_process.process_dict[i][1]:
                        self.server_process.process_dict[i][1] = [new_packet]
                    else:
                        self.server_process.process_dict[i][1].append(new_packet)
                
                    #check whether server busy to start transmitting packets
                    if self.server_process.server_busy == False:
                        self.server_process.server_busy = True

                        







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
