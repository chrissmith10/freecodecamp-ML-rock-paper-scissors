# Port Scanner

import socket
# https://docs.python.org/3/library/socket.html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#host = "137.74.187.100" # you can get this number by entering "ping 'website URL'" in the CLI
#port = 443 # could check ports 443, 80, 21, etc

host = input("Please enter the IP address you want to scan: ")
port = int(input("Please enter the port you want to scan: "))

def portScanner(port):
    if s.connect_ex((host, port)):
        print("The port is closed")
    else:
        print("The port is open")

portScanner(port)
