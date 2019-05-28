import socket
import ipaddress
import ipv4_pkt
import threading

class VirtualNetworkRunner:
    def __init__(self, cli):
        self.ip_addr, self.ll_addr = cli[0], cli[1] #ll_addr is the port numb acting as a mac address
        self.subnet = ipaddress.ip_interface(self.ip_addr)
        self.gw = None
        self.hosting = True
        self.arp_table = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', int(self.ll_addr)))
        self.socket.setblocking(False)
        self.MTU = 1500

    def recv_msg(self):
        try:
            data = self.socket.recvfrom(4096)
            return data
        except Exception:
            return None

    def ip_split(self, ip):
        split_ip = ip.split('/')
        return [split_ip[0], split_ip[1]]
    
    def send_msg(self, information):
        ip_addr = information[0:information.find(' ')]
        ip_addr = ipaddress.ip_address(ip_addr)
        payload = information[information.find(' ')+1: ].strip('"')
        if ip_addr in self.subnet.network:
            if str(ip_addr) not in self.arp_table.keys():
                print("No ARP entry found")
            else:
                self.sending_pkt(ip_addr, self.subnet.ip, payload, int(self.arp_table[str(ip_addr)]))       
        else:
            if self.gw == None:
                    print("No gateway found")
            else:
                if str(self.gw) in self.arp_table.keys():
                    self.sending_pkt(ip_addr, self.subnet.ip, payload, int(self.arp_table[self.gw]))
                else:
                    print("No ARP entry found")

    def sending_pkt(self, ipaddress, subnet_ip, payload, port):
        sending_payload = []
        if len(payload) + 20 > self.MTU:
            i = 0
            message = ''
            while i < len(payload):
                message = message + payload[i]
                if len(message) == self.MTU -21:
                    sending_payload.append(message)
                    message = ''
                i = i+1
            for j in sending_payload:
                pkt = ipv4_pkt.IPPacketV4(dst=ipaddress, src=subnet_ip)
                if j == len(sending_payload)-1:
                    pkt.update_flags(offset=i)
                    pkt.assemble_pkt()
                    send_pkt = pkt.pkt + j.encode('UTF-8')
                    self.socket.sendto(send_pkt, ('localhost', port))
                else:
                    pkt.update_flags(mrf=1)
                    pkt.assemble_pkt()
                    send_pkt = pkt.pkt + j.encode('UTF-8')
                    self.socket.sendto(send_pkt, ('localhost', port))
        else:                    
            pkt = ipv4_pkt.IPPacketV4(dst=ipaddress, src=subnet_ip)
            pkt.assemble_pkt()
            send_pkt = pkt.pkt + payload.encode('UTF-8')
            self.socket.sendto(send_pkt, ('localhost', port))

    def get_cmd(self):
        cli = input('> ')
        cmd, information = self.segment_input(cli)
        return [cmd, information]

    def close(self):
        self.hosting = False
        self.socket.close()

    def gw_get(self):
        print(self.gw)
    
    def arp_get(self, ip):
        if ip in self.arp_table.keys():
            print(self.arp_table[ip])
        else:
            print(None)

    def gw_set(self, information):
        self.gw = information
    
    def arp_set(self, information):
        split_info = information.split()
        self.arp_table[split_info[0]] = split_info[1]

    def mtu_set(self, information):
        self.MTU = int(information)
    
    def mtu_get(self):
        print(self.MTU)

    def segment_input(self, cli):
        split_cli = cli.split()
        if split_cli[0] == 'gw':
            if split_cli[1] == 'set':
                return ['%s %s' % (split_cli[0], split_cli[1]), split_cli[2]]
            else:
                return ['%s %s' % (split_cli[0], split_cli[1]), None]
        if split_cli[0] == 'arp':
            if split_cli[1] == 'set':
                return ['%s %s' % (split_cli[0], split_cli[1]), \
                                '%s %s' % (split_cli[2], split_cli[3])]
            else:
                return ['%s %s' % (split_cli[0], split_cli[1]), split_cli[2]]
        if split_cli[0] == 'mtu':
            if split_cli[1] == 'set':
                return ['%s %s' % (split_cli[0], split_cli[1]), split_cli[2]]
            else:
                return ['%s %s' % (split_cli[0], split_cli[1]), None]
        if split_cli[0] == 'msg':
            return [split_cli[0], '%s %s' % (split_cli[1], split_cli[2])]
        if split_cli[0] == 'exit':
            return [split_cli[0], None]
        
