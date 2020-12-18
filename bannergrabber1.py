# Banner Grabber

import socket

s = socket.socket()

ip = input("Please enter the IP: ")

port = str(input("Please enter the port: "))

s.connect((ip, int(port)))

print(s.recv(1024))
