# freecodecamp.org port scanner

import socket
# https://docs.python.org/3/library/socket.html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    try:
        response1 = input("Would you like to enter a URL or IP address? ")
        if response1 = 'url' or 'URL':
            target = input("Enter the URL: ")
        elif response1 = 'ip address' or 'IP address':
            target = input("Enter the IP address: ")
        break
    except:
        print('Error: Invalid input. Enter url, URL, ip address, or IP address.')

print("Next, enter the port range.")
while True:
    try:
        response2 = int(input("Enter the low: "))
        response3 = int(input("Enter the high: "))
        port_range = range(response2, response3)
        break
    except:
        print('Error: Invalid input. Enter the high and low numbers.')

def get_open_ports(target, port_range, True):
    if s.connect_ex((target, port_range)):
        print("Closed: ", port_range)
    else:
        print("Open: ", port_range)

get_open_ports(target, port_range, True)
