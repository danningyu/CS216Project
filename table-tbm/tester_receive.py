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

from network_util import (
    create_ip_addr_entries, 
    int_to_ip, ip_to_int,
    get_if
)

# mapping of (dst addr, mask) to counter
expected_dsts = {}
error_ips = []

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
    """
    For each incoming packet, check if we expect to receive it.
    If so, decrement its entry in `expected_dsts`. Otherwise, it
    was received in error, so save its details in `error_ips`.
    """
    global expected_dsts
    global error_ips

    if TCP in pkt and pkt[TCP].dport == 1234:
        dst_ip = pkt[IP].dst
        contents = bytes(pkt[Raw]).decode('utf-8')
        print("got a packet from " + dst_ip + " with content " + contents)
        # pkt.show2()
        # hexdump(pkt)
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
    """
    Check that we received all the expected packets and that
    there are no missing or extraneous packets
    """
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
    """Parse the BGP table to get all the expected packets for the
    machine this script runs on. Then, listen for those expected packets.
    Then, check if we got all the packets we expected to get when SIGINT (^C)
    is sent.
    """
    global expected_dsts
    global error_ips

    if len(sys.argv) < 2:
        print('pass 1 argument: <num_prefixes_to_test>')
        exit(1)
    
    my_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    print("Running on " + my_ip)

    prefixes, bgptable = create_ip_addr_entries("../bgptable.csv", int(sys.argv[1]))

    for k, v in prefixes.items():
        if bgptable[v] == my_ip:
            if (int_to_ip(v[0]), v[1]) not in expected_dsts:
                expected_dsts[(int_to_ip(v[0]), v[1])] = 0
            expected_dsts[(int_to_ip(v[0]), v[1])] += 1

    ifaces = [i for i in os.listdir('/sys/class/net/') if 'eth' in i]
    iface = ifaces[0]
    print("sniffing on %s" % iface)
    sys.stdout.flush()

    signal.signal(signal.SIGINT, handle_shutdown)

    sniff(iface = iface, prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
