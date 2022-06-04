#!/usr/bin/env python3
import os
import sys
import signal

from scapy.all import (
    TCP,
    IP,
    Raw,
    FieldLenField,
    FieldListField,
    IntField,
    IPOption,
    ShortField,
    get_if_list,
    sniff
)
from scapy.layers.inet import _IPOption_HDR
import netifaces as ni

from ip_util import create_ip_addr_entries, int_to_ip, ip_to_int

# mapping of (dst addr, mask) to counter
expected_dsts = {}
error_ips = []

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swids",
                                  adjust=lambda pkt,l:l+4),
                    ShortField("count", 0),
                    FieldListField("swids",
                                   [],
                                   IntField("", 0),
                                   length_from=lambda pkt:pkt.count*4) ]
def handle_pkt(pkt):
    global expected_dsts
    global error_ips
    
    errors = []

    if TCP in pkt and pkt[TCP].dport == 1234:
        dst_ip = pkt[IP].dst
        contents = bytes(pkt[Raw]).decode('utf-8')
        print("got a packet from " + dst_ip + " with content " + contents)
        # pkt.show2()
    #    hexdump(pkt)
        sys.stdout.flush()

        ip_addr, mask = contents.split(',')
        ip_mask_combo = (ip_addr, int(mask))
        if ip_mask_combo not in expected_dsts:
                error_ips.append((dst_ip, ip_addr, mask))
        else:
            expected_dsts[ip_mask_combo] -= 1
            if expected_dsts[ip_mask_combo] == 0:
                expected_dsts.pop(ip_mask_combo)

def handle_shutdown(signum, stack_frame):
    global expected_dsts
    global error_ips

    my_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']

    print("Finishing test")
    if len(error_ips) == 0 and len(expected_dsts) == 0:
        print(f"SUCCESS: {my_ip} received all expected packets and no extra packets")
        exit(0)
    else:
        for e in error_ips:
            print(f"ERROR: incorrect routing for packet with dst {e}")
        for k, v in expected_dsts.items():
            print(f"ERROR: expected to receive {v} packets with dst {k}")
        exit(1)
    
def main():
    global expected_dsts
    global error_ips

    if len(sys.argv) < 2:
        print('pass 1 argument: <num_prefixes_to_test>')
        exit(1)
    

    my_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    print("Running on " + my_ip)  # should print "192.168.100.37"

    prefixes, bgptable = create_ip_addr_entries("../bgptable.csv", int(sys.argv[1]))

    for k, v in prefixes.items():
        # print(bgptable[v])
        # print(int_to_ip(k[0]), int_to_ip(k[1]), int_to_ip(v[0]), v[1], v[2])
        if bgptable[v] == my_ip:
            if (int_to_ip(v[0]), v[1]) not in expected_dsts:
                expected_dsts[(int_to_ip(v[0]), v[1])] = 0
            expected_dsts[(int_to_ip(v[0]), v[1])] += 1

    # print(expected_dsts)

    ifaces = [i for i in os.listdir('/sys/class/net/') if 'eth' in i]
    iface = ifaces[0]
    print("sniffing on %s" % iface)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, handle_shutdown)

    sniff(iface = iface, prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
