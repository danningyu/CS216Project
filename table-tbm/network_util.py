import ipaddress

from scapy.all import get_if_list

def get_if():
    ifs = get_if_list()
    iface = None
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def get_prefixes(bgptable_file, num_prefixes_to_save=-1):
    prefixes = {}
    next_hops = {}
    mac_addr = 0x080000000001
    port = 1
    i = 0
    with open(bgptable_file, "r") as f:
        for l in f.readlines():
            content = l.strip().split(',')
            ip_addr = [int(x) for x in content[0].split('.')]
            prefix_length = int(content[1])
            next_hop = content[2]
            if next_hop == "0.0.0.0":
                # TODO: handle this broadcast next hop case
                continue
            ip_addr_binary = f"{ip_addr[0]:08b}{ip_addr[1]:08b}{ip_addr[2]:08b}{ip_addr[3]:08b}"
            ip_addr_masked = ip_addr_binary[:prefix_length]

            if next_hop not in next_hops:
                next_hops[next_hop] = (mac_addr, port)
                mac_addr += 1
                port += 1

            prefixes[ip_addr_masked] = next_hops[next_hop]

            if content[0] not in ["10.0.1.1", "10.0.1.17", "10.0.0.1", "10.0.2.17"]:
                i += 1

            if i == num_prefixes_to_save:
                break

    print("Next hops:")
    for k, v in next_hops.items():
        print(f"{k}\t0x{v[0]:012x} {v[1]}")
    
    return prefixes

def create_ip_addr_entries(bgptable_file, num_entries):
    prefixes = {}
    with open(bgptable_file, "r") as f:
        i = 0
        for l in f.readlines():
            curr_line_comps = l.strip().split(',')
            dst_ip = curr_line_comps[0]
            
            mask = int(curr_line_comps[1])
            next_hop = curr_line_comps[2]

            if dst_ip in ["10.0.1.1", "10.0.1.17", "10.0.0.1", "10.0.2.17"]:
                continue
            
            network = ipaddress.ip_network(f"{dst_ip}/{mask}", strict=False)

            lower = network[0]
            upper = network[-1]
            # print(lower, upper)

            prefixes[(int(network[0]), mask, dst_ip)] = next_hop

            i += 1
            if i == num_entries:
                break
    
    ip_ranges = {} # key: (lower, upper), value: 
    low_ips = [] # start of leftmost unfinalized interval
    high_ips = [] # start of rightmost unfinalized inverval

    curr_mask = None
    for ip, mask, dst_ip in sorted(prefixes.keys(), key=lambda x: (x[0], x[1])):
        # print(f"{int_to_ip(ip)} {mask=}")
        num_addresses = 2 ** (32 - mask)

        # continue
        low_ip = ip
        high_ip = ip + num_addresses
        
        change_made = False
        for k in list(ip_ranges.keys()):
            if k[0] <= low_ip and high_ip <= k[1]:
                old_val = ip_ranges.pop(k)
                if k[0] == low_ip and k[1] == high_ip:
                    _ = 0
                    # print("WARNING: completely overlapping range")
                elif k[0] <= low_ip and k[1] == high_ip:                    
                    ip_ranges[(k[0], low_ip)] = old_val
                elif k[0] == low_ip and k[1] >= high_ip:
                    ip_ranges[(high_ip, k[1])] = old_val
                elif k[0] < low_ip and k[1] > high_ip:
                    ip_ranges[(k[0], low_ip)] = old_val
                    ip_ranges[(high_ip, k[1])] = old_val
                else:
                    print("ERROR: did not catch this case")
                
                ip_ranges[(low_ip, high_ip)] = (ip, mask, dst_ip)
                change_made = True

        if not change_made:
            ip_ranges[(low_ip, high_ip)] = (ip, mask, dst_ip)

        
        # for k, v in ip_ranges.items():
        #     print(ipaddress.ip_address(k[0]), ipaddress.ip_address(k[1]))
        # print("----------------")
    
    return ip_ranges, prefixes

def int_to_ip(ip_addr):
    return str(ipaddress.ip_address(ip_addr))

def ip_to_int(ip_addr):
    return int(ipaddress.ip_address(ip_addr))

if __name__ == "__main__":
    ip_ranges, prefixes = create_ip_addr_entries("../bgptable.csv", 100)
    for k, v in ip_ranges.items():
        print(prefixes[v])
