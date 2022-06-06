#!/usr/bin/env python3
import random
import sys

from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp

from network_util import (
    create_ip_addr_entries, 
    int_to_ip, ip_to_int,
    get_if
)

def main():
    """Send packets to the specified number of entries in the BGP table"""
    if len(sys.argv) < 2:
        print('pass 1 argument: <num_prefixes_to_test>')
        exit(1)
    
    prefixes, _ = create_ip_addr_entries("../bgptable.csv", int(sys.argv[1]))

    for k, v in prefixes.items():
        ip_dst = k[0]
        if v[1] != 32:
            # If we have address 1.0.4.0, convert to 1.0.4.1
            # since address 1.0.4.0 is technically reserved
            # But only if mask is not /32
            ip_dst = int_to_ip(ip_dst + 1)
            
        iface = get_if()

        print("sending on interface %s to %s" % (iface, str(ip_dst)))
        pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / IP(dst=ip_dst) / TCP(dport=1234, sport=random.randint(49152,65535)) / f"{int_to_ip(v[0])},{v[1]}"
        # pkt.show2()
        sendp(pkt, iface=iface, verbose=False)

if __name__ == '__main__':
    main()
