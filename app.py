
import binascii
import codecs
import socket

GOOGLE_IP = "198.41.0.4"
GOOGLE_PORT = 53

currOctet = 0
references = {}
servers = []

class DNSMessage:
    def __init__(self,header,question) -> None:
        self.header = header
        self.question = question

class Header:
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
    if(responseHeader.ancount>=1):
        print("resolved the address")
    print(responseHeader.id,"id")
    print(responseHeader.ancount,"ancount")
    print(responseHeader.arcount,"arcount")
    print(responseHeader.nscount,"nscount")
    return responseHeader

def parseQuestion(header,data):
    global currOctet
    respQuestion = Question(0,0,0)
    domainName = parseDomainName(data,0)
    respQuestion.qname = domainName.get("domainName")
    start = domainName.get("start")
    values = []
    print(data[start:start+8])
    for item in respQuestion.__dict__.items():
        if item[0] == "qname":
            values.append(0)
            continue
        else:
            values.append(int(data[start:start+4],16))
        start+=4
    currOctet+=4
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
    parseRR((data)[start:])

def parseDomainName(data,start):
    global servers
    global currOctet
    initial = start
    start = start
    domainName = ""
    length = 0
    currDomainPart = ""
    startingOctect = currOctet
    while start<len(data):
        curr = data[start:start+4]
        if(HexToBinary(curr)[0:2]=="11"):
            print(currOctet)
            referenceAddress = int(HexToBinary(curr)[3:],2) + 1
            print(referenceAddress,">>>>>>>>>>>")
            domainName+=f".{references[referenceAddress]}"
            servers.append(domainName)
            idx = len(domainName) - 1 - len(f".{references[referenceAddress]}")
            totalLength = len(domainName) - len(f".{references[referenceAddress]}")
            while idx>=0:
                if(domainName[idx]=="."):
                    references[currOctet-(totalLength-idx-1)]=domainName[idx+1:]
                idx-=1
            references[currOctet-(totalLength)] = domainName
            print(references)
            currOctet+=2
            start+=4
            break
        # print(data[start:start+2])
        if(data[start:start+2]=="00"):
            servers.append(domainName)
            idx = len(domainName) - 1
            totalLength = len(domainName)
            while idx>=0:
                if(domainName[idx]=="."):
                    references[currOctet-(totalLength-idx-1)]=domainName[idx+1:]
                idx-=1
            references[currOctet-(totalLength-1)] = domainName
            print(references)
            start+=2
            currOctet+=1
            break
        if(length==0):
            # two cases
            # case1: I am at the start of the domain name so the currDomainPart would be empty so do nothing
            # case2: I have parsed a part of domain name so put it into map and refersh the variables
            if len(currDomainPart)!=0:
                references[startingOctect] = currDomainPart
                startingOctect = currOctet+1
                currDomainPart = ""
            if(start!=initial):
                domainName+="."
            length=int(data[start:start+2],16)
        else:
            domainName+=chr(int(data[start:start+2],16))
            currDomainPart+=chr(int(data[start:start+2],16))
            length-=1
        start+=2
        currOctet+=1
    print("diff ", start - initial)
    
    return {"domainName":domainName,"start":start}
        

def parseRR(data):
    global currOctet
    global servers
    start = 0
    name = data[start:start+4]
    print(name,"name")
    start = start+4
    currOctet+=2

    type = int(data[start:start+4],16)
    print(type," RR type")
    start+=4
    classCode = int(data[start:start+4],16)
    print(classCode," RR class code")
    start+=4
    ttl = int(data[start:start+8],16)
    print(ttl," TTL")
    start+=8
    idx=0
    rdlength = int(data[start:start+4],16)
    print(rdlength," octets")
    start+=4

    currOctet+=10
    if(type==1):
        idx = 0
        ip = ""
        while idx<4:
            ip+=str(int(data[start:start+2],16))
            if(idx!=3):
                ip+="."
            idx+=1
            start+=2
        print(ip," ip")
        GOOGLE_IP = ip
        currOctet = 0
        # servers = []
        print(servers,".................")
        servers = []
        global message
        if responseHeader.ancount==0:
            resp = sock.sendto(message,(GOOGLE_IP,GOOGLE_PORT))
            print("contacted ",ip)
        return
    if(type==2):   
        domainName = parseDomainName(data,start)
        # message2 = getMessage(domainName.get("domainName"))
        # GOOGLE_IP = "198.41.0.4"
        # message2 = bytes.fromhex(message2)
        # resp = sock.sendto(message2,(GOOGLE_IP,GOOGLE_PORT))
        print("contacted ",domainName.get("domainName"))
        # start = domainName.get("start")
    

    if(len(data[start + (rdlength*2):])==0 or responseHeader.ancount==1):
            return
    else:
        print(data[start + (rdlength*2):])
        parseRR(data[start + (rdlength*2):])
        return


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

def getURL(url):
    result = ""
    strs = list(url.split("."))
    for parts in strs:
        result+=str(len(parts))
        result+=parts
    result+="0"
    print(result)
    return result


def binary_to_hex(binary_string):
    """
    Convert a binary string to a hex string.

    Args:
    - binary_string (str): Binary string to be converted.

    Returns:
    - str: Hexadecimal representation of the binary string.
    """
    # Convert binary string to bytes
    binary_bytes = int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, byteorder='big')
    
    # Convert bytes to hex string
    hex_string = binascii.hexlify(binary_bytes).decode('utf-8')
    
    return hex_string

def getMessage(url):
    header1 = Header(22,0,0,0,0,1,0,0,1,0,0,0)
    url = getURL(url)
    question = Question(url,1,1)
    hexString = ""
    binaryString=""
    for item in header1.__dict__.items():
        binaryString+=convertToBits(item[1][0],item[1][1])
    
    hexString+=binary_to_hex(binaryString)
    
    binaryString = ""
    
    for item in question.__dict__.items():
        domainName = ""
        if item[0] == "qname":  
            start = 0
            for idx in range(len(item[1])):
                if item[1][idx].isalpha()==False:
                    binaryString=convertToBits(int(item[1][idx]),8)
                   
                    hexString+=(binary_to_hex(binaryString))+domainName
                else:
                    binaryString=format(ord(item[1][idx]),'08b')
                   
                    hexString+=binary_to_hex(binaryString)
        else:
            binaryString=convertToBits(item[1],16)
            
            hexString+=binary_to_hex(binaryString)

    return hexString


UDP_IP = "127.0.0.1"
PORT = 5005
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP


message = getMessage("dns.google.com")
print(message)

message = bytes.fromhex(message)
resp = sock.sendto(message,(GOOGLE_IP,GOOGLE_PORT))
print(resp)
while True:
    data,addr = sock.recvfrom(2048)
    print(data)
    header = HexToBinary(bytes.hex(data))
    responseHeader = parseHeader(header)
    # header has 12 octects
    currOctet+=12
    parseQuestion(responseHeader,bytes.hex(data)[24:])
