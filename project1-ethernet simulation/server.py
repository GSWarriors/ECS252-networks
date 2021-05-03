
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
            #self.processes = []
            self.process_dict = {}

            for i in range(0, 30):
                self.action = env.process(self.new_host(i))
                self.server_busy = False
                #self.processes.append(self.action)
                self.process_dict[i] = [self.action, [], self.server_busy]

            print("processes dict: " + str(self.process_dict))

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
    def __init__(self, env, arrival_rate, server_process):

        self.env = env
        self.arrival_rate = arrival_rate
        self.server_process = server_process
        self.packet_number = 0
        self.action = env.process(self.run())

    def run(self):

        count = 0

        while True:
            for i in range(0, 30):
                yield self.env.timeout(random.expovariate(self.arrival_rate))

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
                    curr_process.interrupt()

            count += 1

            if count == 10:
                break




class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time





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
