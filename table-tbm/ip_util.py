import ipaddress

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
