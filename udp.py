import socket
import app
UDP_IP = "127.0.0.1"
PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((UDP_IP, PORT))


binaryString=''.join(format(ord(i), '08b') for i in "6google3dns3com0") 
print(binaryString)
