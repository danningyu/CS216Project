mappings = {}

with open("bgptable.txt", "r") as f:
    curr_prefix = None
    for line in f.readlines():
        components = line.strip().split()
        if line[3] != " ":
            prefix = components[1]
            
            prefix_parts = prefix.split('/')
            mask = None
            # print(prefix_parts)
            if len(prefix_parts) == 1:
                mask = 32
            else:
                assert(len(prefix_parts) == 2)
                mask = int(prefix_parts[1])
            
            prefix = prefix_parts[0]


            next_hop = components[2]
            mappings[(prefix, mask)] = next_hop
            
        
            
with open("bgptable.csv", "w") as f:
    for k, v in mappings.items():
        f.write(f"{k[0]},{k[1]},{v}\n")

