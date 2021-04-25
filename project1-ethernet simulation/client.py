#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 22:35:14 2021

@author: dghosal
"""
# client
from socket import *
import os



def main(): 
    serverName = 'localhost'
    serverPort = 12001
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    """print('Socket', clientSocket.fileno(), 'opened to server', serverName, ':', serverPort)
    firstName = input('What is your first name? ')
    clientSocket.send(str.encode(firstName))
    response = clientSocket.recv(1024)
    print('Server says:', bytes.decode(response))
    lastName = input('What is your last name? ')
    clientSocket.send(str.encode(lastName))
    response = clientSocket.recv(1024)
    print('Server says:', bytes.decode(response))"""
    clientSocket.close()



main()