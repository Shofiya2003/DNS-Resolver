# Nimbus: DNS Resolver 

This Project is a DNS resolver which takes in url and resolves it to an IP address by sending UDP packets to external DNS servers. 
It includes logic to parse the Header, Question and Resource Records in the DNS response. Additionally it accomodates the compression technique used in DNS responses to 
reduce the repetition of domain names, while parsing the responses.

## Nimbus In Action 
[Screencast from 27-01-24 06:15:23 PM IST.webm](https://github.com/Shofiya2003/DNS-Resolver/assets/86974918/75c1f32f-5b7e-42ea-a39c-7baa8c1741e5)

## How does this work?

![Untitled-2023-12-26-0443(1)](https://github.com/Shofiya2003/DNS-Resolver/assets/86974918/8a28cb3f-5155-48c1-a63d-7ca8be4cfb6b)


## To Do
- [ ] Cleaner Code
- [ ] Recursively Query the NS records
- [ ] Support for CNAME records
- [ ] Improve the speed
