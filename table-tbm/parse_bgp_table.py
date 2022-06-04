def get_prefixes(routing_table, num_prefixes_to_save=-1):
    prefixes = {}
    next_hops = {}
    mac_addr = 0x080000000001
    port = 1
    i = 0
    with open(routing_table, "r") as f:
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
