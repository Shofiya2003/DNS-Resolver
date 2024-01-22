
import codecs
import socket

GOOGLE_IP = "8.8.8.8"
GOOGLE_PORT = 53


class DNSMessage:
    def __init__(self,header,question) -> None:
        self.header = header
        self.question = question

class Header:
    # def __init__(self) -> None:
    #     self.id = 0
    
    def __init__(self,id,qr,opcode,aa,tc,rd,ra,rcode,qdcount,ancount,nscount,arcount) -> None:
        self.id = [id,16]
        self.qr = [qr,1]
        self.opcode = [opcode,4]
        self.aa = [aa,1] 
        self.tc = [tc,1]
        self.rd = [rd,1] 
        self.ra = [ra,1] 
        self.z = [0,3]
        self.rcode = [rcode,4]
        self.qdcount = [qdcount,16]
        self.ancount = [ancount,16]
        self.nscount = [nscount,16]
        self.arcount = [arcount,16]

class Question:
    def __init__(self,qname,qtype,qclass) -> None:
        self.qname = qname
        self.qtype = qtype
        self.qclass = qclass


def parseHeader(resp):
    responseHeader = Header(0,0,0,0,0,0,0,0,0,0,0,0)
    start = 0
    values = []
    for item in responseHeader.__dict__.items():
        values.append(convertToNumber(resp[start:start+item[1][1]]))
        start+=item[1][1]

    idx = 0
    for key in responseHeader.__dict__.keys():
        setattr(responseHeader,key,values[idx])
        idx+=1

    print(responseHeader.id)


def parseQuestion(data):
    respQuestion = Question(0,0,0)
    start = 0
    question = ""
    length = 0
    while start<len(data):
        # print(data[start:start+2])
        if(data[start:start+2]=="00"):
            start+=2
            break
        if(length==0):
            if(start!=0):
                question+="."
            length=int(data[start:start+2],16)
        else:
            question+=chr(int(data[start:start+2],16))
            length-=1
        start+=2
        
    respQuestion.qname = question

    values = []
    print(data[start:start+8])
    for item in respQuestion.__dict__.items():
        if item[0] == "qname":
            values.append(0)
            continue
        else:
            values.append(int(data[start:start+4],16))
        start+=4

    idx = 0
    for key in respQuestion.__dict__.keys():
        if(idx==0):
            idx+=1
            continue
        setattr(respQuestion,key,values[idx])
        idx+=1
        
    print(respQuestion.qname)
    print(respQuestion.qtype)
    print(respQuestion.qclass)


def convertToBits(number,numberOfBits):
    bits = bin(number)[2:].zfill(numberOfBits)
    return bits
    

def convertToNumber(binary):
    return int(binary,2)

def HexToBinary(resp):
    hex_dict = {'0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101', '6': '0110', '7': '0111', '8': '1000', '9': '1001', 'a': '1010', 'b': '1011', 'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111'}
    binary = ''
    for digit in resp:
        binary += hex_dict[digit]
    return binary

def getMessage():

    header1 = Header(22,1,0,0,0,1,0,0,1,0,0,0)
    question = Question("3dns6google3com0",1,1)
    binaryString = ""
    for item in header1.__dict__.items():
        binaryString+=convertToBits(item[1][0],item[1][1])

    
    for item in question.__dict__.items():
        
        if item[0] == "qname":
            
            binaryString+=''.join(format(ord(i), '08b') for i in item[1]) 
            
        else:
            binaryString+=convertToBits(item[1],16)

    return hex(int(binaryString,2))


UDP_IP = "127.0.0.1"
PORT = 5005
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


message = getMessage()

message = message[2:]
message = "00"+message
# fix the error in getMessage()

message = bytes.fromhex("00160100000100000000000003646e7306676f6f676c6503636f6d0000010001")

resp = sock.sendto(message,(GOOGLE_IP,GOOGLE_PORT))
print(resp)
while True:
    data,addr = sock.recvfrom(2048)
    print()
    header = HexToBinary(bytes.hex(data[1:13]))
    parseHeader(header)
    parseQuestion(bytes.hex(data)[24:])
    print(bytes.hex(data)[38:])

