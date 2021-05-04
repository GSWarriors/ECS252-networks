
from socket import *
import os
import signal
import simpy
import random
import time 


class G:
    RANDOM_SEED = 33
    SIM_TIME = 5000000
    MU = 1
    LONG_SLEEP_TIMER = 1000000000



class Server_Process(object):
    def __init__(self, env, called_before):


        if not called_before:
            self.env = env
            #self.processes = []
            self.process_dict = {}

            for i in range(0, 30):
                self.action = env.process(self.new_host(i))
                self.server_busy = False
                #self.processes.append(self.action)
                self.process_dict[i] = [self.action, [], self.server_busy]

        self.called_before = True



    def new_host(self, i):

        start_time = 0
        end_time = 0

        while 1:
            try:
                print("yielding process: " + str(i))
                print()
                end_time = time.perf_counter()
                print("time taken from interrupt to yield: " + str(end_time - start_time))
                print()
                print()
                yield self.env.timeout(G.LONG_SLEEP_TIMER)

            except simpy.Interrupt:
                start_time = time.perf_counter()
                print("process " + str(i) + " has been interrupted by packet")
                print("servicing packet")
                #queue for current process
                queue = self.process_dict[i][1]
                server_busy = self.process_dict[i][2]

                while len(queue) > 0:

                    packet = queue.pop(0)
                    print("the packet number: " + str(packet.identifier))
                    print("the arrival time: " + str(packet.arrival_time))
                    print()
                    
                    yield self.env.timeout(random.expovariate(G.MU))

                #we have emptied the queue for this process
                server_busy = False
                print("queue emptied for process: " + str(i))





class Arrival_Process(object):
    def __init__(self, env, arrival_rate, server_process, called_before):

        if not called_before:
            self.env = env
            self.arrival_rate = arrival_rate
            self.server_process = server_process
            self.packet_number = 0
            self.arrival_count = [0]*30

            for i in range(0, 30):
                self.action = env.process(self.run(i))

        self.called_before = True



    def run(self, i):

        while True:
            yield self.env.timeout(random.expovariate(self.arrival_rate))

            self.arrival_count[i] += 1

            curr_process = self.server_process.process_dict[i][0]
            curr_queue = self.server_process.process_dict[i][1]
            curr_server_busy = self.server_process.process_dict[i][2]

            #create and enqueue new packet
            self.packet_number += 1
            arrival_time = self.env.now
            new_packet = Packet(self.packet_number,arrival_time)

            curr_queue.append(new_packet)
            print("the queue size for process " + str(i) + " is now: " + str(len(curr_queue)))
            print()


            #check whether server busy to start transmitting packets
            if curr_server_busy == False:
                curr_server_busy = True

                if self.arrival_count[i] > 1:
                    print("packet arrived again at process: " + str(i))

                #wait for some time in order to let the process yield again
                #yield self.env.timeout(5)
                curr_process.interrupt()






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
