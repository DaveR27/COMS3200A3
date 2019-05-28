import socket
import struct

class IPPacketV4:
    def __init__(self, dst, src):
        self.pkt = None
        self.dst = dst
        self.src = src
        self.ip_ver = 4
        self.ip_header_len = 5
        self.update_service()
        self.total_length = 0
        self.pkt_identifier = 5432 # increment by one for every datagram (all fragments have the same number)
        self.update_flags()
        self.ttl = 255 #timetolive
        self.ip_proto = 0
        self.ip_check_sum = 0
        self.source_ip = socket.inet_aton(str(self.src)) #converted ip
        self.dest_ip = socket.inet_aton(str(self.dst)) #converted ip

    def update_service(self, dscp=0, ecn=0):
        self.dscp = dscp #differentiated service code point (used in real-time streaming)
        self.ecn = ecn #allows end to end notification of network congestion
        self.service_type = (self.dscp << 2) + self.ecn

    def update_flags(self,rsv=0, df=0, mrf=0, offset=0):
        self.rsv = rsv #flag 1 reserved and must be 0
        self.df = df #flag 2 Don't fragment
        self.mrf = mrf #flag 3 More fragments coming
        self.fragment_offset = offset # specifies the offset of the fragment in relation to the original unfragmented datagram
        self.pkt_flags = (self.rsv << 7) + (self.df << 6) \
            + (self.mrf << 5) + (self.fragment_offset) #ip flags to fragment (16bits)

    def assemble_pkt(self):
        self.pkt = struct.pack('!BBHHHBBH4s4s' , 
        self.ip_ver,   #IP Version 
        self.service_type,   #Differentiate Service Feild
        self.ip_header_len,   #Total Length
        self.pkt_identifier,   #Identification
        self.pkt_flags,   #Flags
        self.ttl,   #Time to live
        self.ip_proto, #protocol
        self.ip_check_sum,   #Checksum
        self.source_ip, #Source IP 
        self.dest_ip  #Destination IP
        )

    def get_pkt_identifier(self):
        return self.pkt_identifier
    

