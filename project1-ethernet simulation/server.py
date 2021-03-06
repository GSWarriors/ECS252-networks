from socket import *
import signal
import simpy
import random
import time 
import sys
from threading import Event 



class G:
    RANDOM_SEED = 33
    SIM_TIME = 100
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
            
            for i in range(0, 10):
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
                #checking the queue. add head to interrupt list
                curr_queue = val[1]
                if len(curr_queue) > 0: 
                    packet = curr_queue[0]

                    #don't add packet to interrupt list if retransmitting
                    if self.process_dict[key][2] == False:
                        interrupt_list.append((key, val[0], packet))
                        self.process_dict[key][2] = True 
                    
            print()

          
            #check number of processes not waiting
            not_waiting_count = 0
            processes_not_waiting = []
            for j in range(0, len(interrupt_list)):
                curr_process = interrupt_list[j][0]
                not_waiting_count += 1
                processes_not_waiting.append(curr_process)


            print("number of processes waiting: " + str(not_waiting_count))
            if len(interrupt_list) >= 3:
                print("the interrupt list: " + str(interrupt_list))
                print()





            #interrupt the processes that have packets that collided.
            #[curr_process][2] tells us whether a retransmission for the current process is already in progress
            if not_waiting_count > 1:

                for i in range(0, len(interrupt_list)):

                    process_num = interrupt_list[i][0]
                    process_id = interrupt_list[i][1]
                    packet_num = interrupt_list[i][2] 
                    

                    #process ready to transmit but collision
                    #two cases, process has come here before or process is coming for first time
                        
                    if len(self.retransmit_dict[process_num]) == 2:
                        if packet_num == self.retransmit_dict[process_num][0]:
                            self.retransmit_dict[process_num][1] += 1
                        
                        process_id.interrupt()

                    else:
                        self.retransmit_dict[process_num].append(packet_num)
                        self.retransmit_dict[process_num].append(0)
                        print("added to retransmit dict: " + str(self.retransmit_dict[process_num]))
                        process_id.interrupt()
    


            elif not_waiting_count == 1:
                #check the process number and the packet number from interrupt list 
                curr_not_waiting = processes_not_waiting[0]
                curr_queue = self.process_dict[curr_not_waiting][1] 


                #remove the process/packet from retransmit dict
                #look at this tomorrow, might be incorrect
                if len(self.retransmit_dict[curr_not_waiting]) == 2:
                    retransmit_packet = self.retransmit_dict[curr_not_waiting][0]

                    if curr_queue[0] == retransmit_packet:
                        self.retransmit_dict[curr_not_waiting] = []
                

                 
                popped_packet = curr_queue.pop(0)
                print("removed packet from process: " + str(curr_not_waiting))
                print("packet number: " + str(popped_packet.identifier))

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

                #we are now waiting for the retransmit to happen
                curr_process = self.server_process.process_dict[i]

                if self.algo == 'beb':
                    
                    delay_slots = -1
                    n = self.server_process.retransmit_dict[i][1]
                    print("n is " + str(n))
                    

                    if n == 0:
                        delay_slots = 0
                        print("retransmitting from process: " + str(i) + " in next time slot.")
                        yield self.env.timeout(1)
                        #print("current env time for n = 0: " + str(self.env.now))
                    
                        

                    else:
                        k = min(n, 11)
                        delay_slots = random.randint(1, pow(2, k))
                        print("retransmitting from process: " + str(i) + " after: " + str(delay_slots) + " delay slots")
                        yield self.env.timeout(delay_slots)
                        #print("current env time: " + str(self.env.now))


                
                    #check whether server busy to start transmitting packets
                    if self.server_process.server_busy == False:
                        self.server_process.server_busy = True
                        

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

    for arrival_rate in [0.1]:
        env = simpy.Environment()
        server_process = Server_Process(env, called_before)

        arrival = Arrival_Process(env, arrival_rate, server_process, arrival_called_before, algo)
        env.run(until=G.SIM_TIME)
    signal.pause()



main()
