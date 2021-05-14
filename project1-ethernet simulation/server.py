
from socket import *
import signal
import simpy
import random
import time 
import sys
from threading import Event 



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
            self.retransmit_dict = {}
            
            for i in range(0, 2):
                self.process_dict[i] = [None, [], self.retransmitting]
                self.retransmit_dict[i] = []

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
                    print("packet number: " + str(packet.identifier))
                    #print("packet arrived at: " + str(packet.arrival_time))
                    interrupt_list.append((key, val[0], packet))
                    
            print()

          

            #interrupt the processes that have packets that were dequeued 
            #this is the collision handling.
            #[curr_process][2] tells us whether a retransmission for the current process is already in progress

            if len(interrupt_list) >= 2:
                print("interrupt list: " + str(interrupt_list))

                for i in range(0, len(interrupt_list)):
                    curr_process = interrupt_list[i][0]
                    packet_num = interrupt_list[i][2].identifier
                    
                    while self.process_dict[curr_process][2] == True:
                        print("already retransmitting, wait")
                        yield self.env.timeout(1)

                    
                    self.process_dict[curr_process][2] = True

                    if len(self.retransmit_dict[curr_process]) > 0:
                        if packet_num == self.retransmit_dict[curr_process][0]:
                            self.retransmit_dict[curr_process][1] += 1

                    else:
                        self.retransmit_dict[curr_process] = [packet_num, 0]

                    interrupt_list[i][1].interrupt()
                
            elif len(interrupt_list) == 1:
                #yield self.env.timeout(random.expovariate(G.MU))
                #check the process number and the packet number from interrupt list 

                process_num = interrupt_list[0][0]
                packet_num = interrupt_list[0][2] 

                if len(self.retransmit_dict[process_num]) == 1:
                    retransmit_packet_num = self.retransmit_dict[process_num][0]

                    if packet_num == retransmit_packet_num:
                        self.retransmit_dict[process_num].pop()
                        self.retransmit_dict[process_num].pop()
                        print("retransmitted packet: " + str(packet_num) + " has been serviced")

                else:
                    print("an arriving packet has been serviced")

            else:
                print("server idle")


            self.server_busy = False







class Arrival_Process(object):
    def __init__(self, env, arrival_rate, server_process, called_before, algo):

        if not called_before:
            self.env = env
            self.arrival_rate = arrival_rate
            self.server_process = server_process
            self.packet_number = 0
            self.algo = algo
  

            for i in range(0, 2):
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
            

                if self.algo == 'beb':
                    print("algorithm is binary exponential backoff")
                    delay_slots = -1
                    #self.beb_algo(i, curr_process)

                    n = self.server_process.retransmit_dict[i][1]
                    print("n is " + str(n))

                    if n == 0:
                        delay_slots = 0
                        print("retransmitting from process: " + str(i) + " the packet: " + str(self.server_process.retransmit_dict[i][0]) 
                        + " right away.")                        
                    else:
                        delay_slots = random.randint(0, pow(2, n - 1))
                        print("retransmitting from process: " + str(i) + " the packet: " + str(self.server_process.retransmit_dict[i][0]) 
                        + " after: " + str(delay_slots) + " delay slots")
                        
                        yield self.env.timeout(delay_slots)

                    #add packet with same number to queue again

                    self.packet_number = self.server_process.retransmit_dict[i][0]
                    arrival_time = self.env.now
                    retransmit_packet = Packet(self.packet_number,arrival_time)
                    
                    #add to queue again
                    curr_queue = curr_process[1]

                    if not curr_queue:
                        curr_queue = [retransmit_packet]
                    else:
                        curr_queue.append(retransmit_packet)
                
                    #check whether server busy to start transmitting packets
                    if self.server_process.server_busy == False:
                        self.server_process.server_busy = True
                                          
                   
                #we are done with the current retransmission attempt
                curr_process[2] = False


                """
                0.5 aloha, and 1/N aloha - put in separate function based on what's called

                #retransmit = random.randint(0, 1)
                retransmit = random.randint(0, 29)


                #retransmit packet for each process with a 50% probability by adding to the queue again 
                #reduce packet number by 1 because retransmitting that packet
                if retransmit == 0:
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
                    while retransmit > 0:
                        yield self.env.timeout(1)
                        retransmit = random.randint(0, 29)
                    
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
                        self.server_process.server_busy = True"""

                



    #here, use the num times the packet's been retransmitted to det how long to wait 
    #for bin exp backoff. a random number between 0 and 2^n - 1 where n is number of retransmits done.
    #doesn't work in a function for some reason
    """def beb_algo(self, i, curr_process):
    
        print("RUNNING beb")

        n = self.server_process.retransmit_dict[i][0][1]
        print("n is " + str(n))

        delay_slots = random.randint(0, pow(2, n-1))
        print("number of delay slots chosen: " + str(delay_slots))
        yield self.env.timeout(delay_slots)

        #add packet with same number to queue again

        self.packet_number = self.server_process.retransmit_dict[i][0][0]
        arrival_time = self.env.now
        retransmit_packet = Packet(self.packet_number,arrival_time)
        print("retransmitting from process: " + str(i) + " the packet: " + str(self.server_process.retransmit_dict[i][0]))
               
        #add to queue again
        curr_queue = curr_process[1]

        if not curr_queue:
            curr_queue = [retransmit_packet]
        else:
            curr_queue.append(retransmit_packet)
    
        #check whether server busy to start transmitting packets
        if self.server_process.server_busy == False:
            self.server_process.server_busy = True"""
    

   



class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time



def main():

    
    algo = sys.argv[1]

    print("algo is: " + str(algo))
    #arrival_rate = sys.argv[2]


    num_hosts = 30
    called_before = False
    arrival_called_before = False 

    for arrival_rate in [0.5]:
        env = simpy.Environment()
        server_process = Server_Process(env, called_before)

        arrival = Arrival_Process(env, arrival_rate, server_process, arrival_called_before, algo)
        env.run(until=G.SIM_TIME)
    signal.pause()



main()
