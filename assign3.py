import sys
import virt_network_runner
import threading
import struct
import _thread
import time
import socket

listening_lock = threading.Lock()

def incoming_listen(virt_network, fragmented_list, assemble_frag):
    while virt_network.hosting:
        data = virt_network.recv_msg()
        if data != None:
            ipheader = data[0][0:20]
            unpacked = struct.unpack('!BBHHHBBH4s4s', ipheader)
            payload = data[0][20:].decode('UTF-8')
            payload = '"%s"'%payload
            addr = socket.inet_ntoa(unpacked[len(unpacked)-2])
            proto = '{0:#0{1}x}'.format(unpacked[6],4)
            ip_fragmentation = '{0:016b}'.format(unpacked[4])
            if ip_fragmentation[2] == 1:
                fragmented_list.append(payload)
                continue
            if int(ip_fragmentation[2:]) > 0:
                fragmented_list.append(payload)
                assemble_frag = True
                continue
            if proto == '0x00':
                print("Message received from " + addr +': ' + payload)
                sys.stdout.flush()
            else:
                print("Message received from " + addr +" with protocol "+proto)
                sys.stdout.flush()
      

def main():
    cli_args = sys.argv[1:]
    virt_network = virt_network_runner.VirtualNetworkRunner(cli_args)
    net_operations = {'exit': virt_network.close, 'gw set': virt_network.gw_set, \
                    'arp set': virt_network.arp_set, 'gw get': virt_network.gw_get, \
                    'arp get': virt_network.arp_get, 'msg': virt_network.send_msg,
                    'mtu set': virt_network.mtu_set, 'mtu get': virt_network.mtu_get}
    listening_lock.acquire()
    fragmented_list = []
    assemble_frag = False
    while virt_network.hosting:
        _thread.start_new_thread(incoming_listen, (virt_network,fragmented_list,assemble_frag,))
        cmd, information = virt_network.get_cmd()

        if assemble_frag == True:
            message = ''
            for i in fragmented_list:
                message = message + i
            assemble_frag = False
            fragmented_list = []

        if information is not None:
            net_operations[cmd](information)
        else:
            if cmd == 'exit':
                listening_lock.release()
            net_operations[cmd]()

if __name__ == "__main__":
    main()
