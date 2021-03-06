import json

def generate(next_hop_map, stride_length=3, default_next_hop=(0x0, 0), output_file="tbm.p4gen", runtime_file="simple-topo/s1-runtime.json"):
    """
    Takes in params next_hop_map (maps 32-bit IP addresses to 32-bit next hops),
    as well as length of each stride. The default_next_hop param sets the default next
    hop if no match (this is overriden if * is in the next_hop_map keys).

    Generates tree bit map internal/external bitmaps, converts to p4 code representation,
    then saves p4 layer code in output file and runtime file.
    """
    
    validate_input(next_hop_map)
    
    # ensure a next hop is set for "*"
    if "" not in next_hop_map:
        next_hop_map[""] = default_next_hop
    
    levels = build_trie_nodes(next_hop_map, stride_length)
    
    write_levels_to_p4(levels, stride_length, output_file, runtime_file)

def validate_input(next_hop_map):
    """ Sanity check that next_hop_map keys/values are valid """
    for key in next_hop_map:
        # keys should be bitstring prefixes of length 0-32
        assert(0 <= len(key) and len(key) <= 32)
        for c in key:
            if c != "0" and c != "1":
                print(key)
            assert(c == "0" or c == "1")
        # next hops should fit in 32-bit unsigned integer
        # changed to tuple of (output MAC, output router port)
        # assert(0 <= next_hop_map[key] and next_hop_map[key] <= 2**32 - 1)

def get_internal_level(prefix, stride_length):
    """
    Compute the level where the node containing this prefix is.
    For a stride length S, the level is given by:
        0-(S-1): level 0
        S-(2S-1): level 1
        ...
    """
    return len(prefix) // stride_length

def get_num_levels(stride_length, longest_prefix_length):
    """
    Return total number of levels needed to match 32 bits, given a stride length
    """
    return 1 + (longest_prefix_length // stride_length)

class Node:                    
    def __init__(self, stride_length):
        self.S = stride_length
        self.internalBitmap = ""  # 2^S - 1 bits
        self.externalBitmap = "" # 2^S bits
        self.outFaceList = []  # store next hops for each 1 in internal bitmap
        
        # used to build internal/external bitmaps
        self.internal_prefixes = []  # tuples of (prefix, next hop)
        self.external_prefixes = set()  # set of prefixes that should go in external bitmap
    
    def build(self):
        self.build_external_bitmap()
        self.build_internal_bitmap()
        
    def build_external_bitmap(self):
        """ compute external bitmap based on prefixes set """
        bm = [0] * (2**self.S)
        for prefix in self.external_prefixes:
            bm[int("0" + prefix, 2)] = 1
        self.externalBitmap = bm
    
    def build_internal_bitmap(self):
        """ compute internal bitmap and outFaceList based on internal prefixes list """
        # sort internal prefixes in tree level order (first by prefix length, then prefix)
        bm = [0] * (2**self.S - 1)
        next_hops = []
        self.internal_prefixes.sort(key=lambda x:(len(x[0]),int(x[0]+"0",2)))
        for prefix, next_hop in self.internal_prefixes:
            idx = (2**len(prefix) - 1) + int("0" + prefix, 2)
            bm[idx] = 1
            next_hops.append(next_hop)
            
        self.internalBitmap = bm
        self.outFaceList = next_hops
    
    def __str__(self):
        return f"{self.internalBitmap=} {self.externalBitmap=} {self.outFaceList=}"

def build_trie_nodes(next_hop_map, stride_length):
    """
    Builds the trie nodes (computes internal and external bitmaps).
    Returns a list of lists of Nodes (representing the nodes on each level).
    """
    
    longest_prefix_length = max([len(k) for k in next_hop_map.keys()])
    L = get_num_levels(stride_length, longest_prefix_length)
    S = stride_length
    
    levels = []
    for _ in range(L):
        # store a dict for each level, with keys being the roots of each trie node 
        levels.append({})
    
    for prefix in next_hop_map:
        # add prefix to correct node's internal list
        lvl = get_internal_level(prefix, stride_length)
        node_key = prefix[:lvl*S]
        if node_key not in levels[lvl]:
            levels[lvl][node_key] = Node(stride_length)
        levels[lvl][node_key].internal_prefixes.append((prefix[lvl*S:], next_hop_map[prefix]))
        
        # traverse up levels to set nodes in previous levels' external bitmaps
        for i in range(lvl):
            node_key = prefix[:i*S]
            external_key = prefix[i*S:(i+1)*S]
            if node_key not in levels[i]:
                levels[i][node_key] = Node(stride_length)
            levels[i][node_key].external_prefixes.add(external_key)
    
    # convert Node dicts to sorted list by prefix + build bitmaps
    res = []
    for i in range(L):
        res.append([])
        for key in sorted(levels[i].keys()):
            levels[i][key].build()
            res[i].append(levels[i][key])
    return res

def mac_hex_to_colon_separated(mac_addr):
    """
    Covert MAC address in the form 0x010203040506 to 01:02:03:04:05:06
    """
    assert(type(mac_addr) == str and len(mac_addr) == 14)
    return (f"{mac_addr[2:4]}:{mac_addr[4:6]}:{mac_addr[6:8]}"
            f":{mac_addr[8:10]}:{mac_addr[10:12]}:{mac_addr[12:14]}")

def write_levels_to_p4(levels, stride_length, output_file, runtime_file):
    """
    Given list of list of nodes corresponding to each level of the tree bit map,
    convert to a list of p4 controls with tables to encode each internal/external
    bitmap. Also creates an ingress stage that combines these controls and matches
    to a results table.
    
    Converted p4 code written to `output_file`.
    Converted table entries written to `runtime_file`.
    """

    runtime_file_table_entries = []
    runtime_file_json = {
        "target": "bmv2",
        "p4info": "build/tbm.p4.p4info.txt",
        "bmv2_json": "build/tbm.json",
        "table_entries": runtime_file_table_entries
    }

    with open(output_file, "w") as f:        
        # generate controls for each layer
        next_hop_ct = 0  # number each next hop
        for lvl in range(len(levels)):
            header = (f"\ncontrol layer_{lvl}(inout bit<32> next_hop_idx, "
                      f"inout bit<{stride_length}> stride, inout bit<32> node_idx, inout bool done) {{"
                      "\n    action fail() {"
                      "\n      done = true;"
                      "\n    }"
                      "\n    action set_next_hop_idx(bit<32> idx) {"
                      "\n      next_hop_idx = idx;"
                      "\n    }"
                      "\n    action set_node_idx(bit<32> idx) {"
                      "\n      node_idx = idx;"
                      "\n    }"
                      "\n    action nop() {}"
                      "\n"
                     )
            f.write(header)
            
            # count node indexes of next level (for external bitmap)
            node_idx_ct = 0
            
            for i in range(len(levels[lvl])):
                node = levels[lvl][i]
                
                # write each internal table
                internal_action = [-1] * (2**stride_length)
                # iterate through (level-order) internal bitmap, paint action array
                # for all matching prefixes whenever a 1-bit is found
                for bit_len in range(stride_length):
                    for j in range(2**bit_len):
                        idx = j + (2**bit_len - 1)
                        if node.internalBitmap[idx] == 1:
                            scale_factor = 2**(stride_length-bit_len)
                            for k in range(j*scale_factor, (j+1)*scale_factor):
                                internal_action[k] = next_hop_ct
                            next_hop_ct += 1
                internal_table = (f"\n    table internal_{lvl}_{i} {{"
                                  "\n      key = { stride: exact; }"
                                  "\n      actions = { set_next_hop_idx; nop; }"
                                  "\n      size = 16384;"
                                  "\n    }"
                                 )
                
                # specify default table entry
                runtime_file_table_entries.append({   
                    "table": f"MyIngress.layer_{lvl}_inst.internal_{lvl}_{i}",
                    "default_action": True,
                    "action_name": f"MyIngress.layer_{lvl}_inst.nop",
                    "action_params": {}
                })
                
                # save each table entry in s1-runtime.json
                for j in range(len(internal_action)):
                    if internal_action[j] != -1:
                        runtime_file_table_entries.append({
                            "table": f"MyIngress.layer_{lvl}_inst.internal_{lvl}_{i}",
                            "match": {
                                "stride": [j]
                            },
                            "action_name": f"MyIngress.layer_{lvl}_inst.set_next_hop_idx",
                            "action_params": { "idx": internal_action[j]}
                        })

                f.write(internal_table)
                
                # write each external table
                external_table = (f"\n    table external_{lvl}_{i} {{"
                                  "\n      key = { stride: exact; }"
                                  "\n      actions = { set_node_idx; fail; }"
                                  "\n      size = 16384;"
                                  "\n     }"
                                 )
                
                # specify default external table entry in runtime JSON
                runtime_file_table_entries.append({
                    "table": f"MyIngress.layer_{lvl}_inst.external_{lvl}_{i}",
                    "default_action": True,
                    "action_name": f"MyIngress.layer_{lvl}_inst.fail",
                    "action_params": {}
                })

                # save each table entry in s1-runtime.json
                for j in range(len(node.externalBitmap)):
                    if node.externalBitmap[j] == 1:
                        runtime_file_table_entries.append({
                            "table": f"MyIngress.layer_{lvl}_inst.external_{lvl}_{i}",
                            "match": {"stride": [j]},
                            "action_name": f"MyIngress.layer_{lvl}_inst.set_node_idx",
                            "action_params": {"idx": node_idx_ct}
                        })

                        node_idx_ct += 1
                
                f.write(external_table)
                
            # write the apply block
            apply = "\n    apply {"
            for i in range(len(levels[lvl])):
                if_str = "if" if i == 0 else "} else if"
                apply += (f"\n      {if_str} (node_idx == {i}) {{"
                          f"\n        internal_{lvl}_{i}.apply();"
                          f"\n        external_{lvl}_{i}.apply();"
                         )
            if len(levels[lvl]) > 0:
                apply += ("\n      } else {"
                          "\n        fail();"
                          "\n      }"
                         )
            apply += "\n    }"
            f.write(apply)
            f.write("\n}\n")

            # write the results control block
            # converts node index to output MAC address and switch port
            res_block = (f"\ncontrol set_res_{lvl}(inout bit<32> next_hop_idx, "
                         f"inout headers_t hdr, inout std_meta_t std_meta){{"
                         f"\n  action set_output_face(macAddr_t dstAddr, egressSpec_t dstPort) {{"
                         f"\n    hdr.ethernet.dstAddr = dstAddr;"
                         f"\n    std_meta.egress_spec = dstPort;"
                         f"\n  }}"
                         "\n\n  table result {"
                         "\n    key = { next_hop_idx: exact; }"
                         "\n    actions = { set_output_face; }"
                         "\n    size = 16384;"
                         "\n  }"
                    )
            
            res_block += "\n  apply { result.apply(); }\n}\n"
            f.write(res_block)

            # table entries get written to s1-runtime.json
            runtime_file_table_entries.append({
                "table": f"MyIngress.set_res_{lvl}_inst.result",
                "default_action": True,
                "action_name": f"MyIngress.set_res_{lvl}_inst.set_output_face",
                "action_params": { 
                    "dstAddr": "00:00:00:00:00:00",
                    "dstPort": 0
                }
            })
            res_ct = 0
            for lvl_loc in range(len(levels)):
                for node in levels[lvl_loc]:
                    for res in node.outFaceList:
                        runtime_file_table_entries.append({
                            "table": f"MyIngress.set_res_{lvl}_inst.result",
                            "match": { "next_hop_idx": [res_ct] },
                            "action_name": f"MyIngress.set_res_{lvl}_inst.set_output_face",
                            "action_params": {
                                "dstAddr": mac_hex_to_colon_separated(f"0x{res[0]:012x}"),
                                "dstPort": res[1]
                            }
                        })
                        res_ct += 1
        
        with open(runtime_file, "w") as runtime_file_fp:
            json.dump(runtime_file_json, runtime_file_fp, indent=2)
        
        # write ingress stage
        ingress = "\ncontrol MyIngress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {"
        for i in range(len(levels)):
            ingress += f"\n    layer_{i}() layer_{i}_inst;"
            ingress += f"\n    set_res_{i}() set_res_{i}_inst;"

        ingress += (
                    "\n\n    apply {"
                    "\n        bit<32> next_hop_idx = 0;"
                    "\n        bit<32> ip_addr = hdr.ipv4.dstAddr;"
                    "\n        bit<32> node_idx = 0;"
                    "\n        bool done = false;"
                    f"\n        bit<{stride_length}> stride = 0;"
                   )
        msb = 31
        for lvl in range(len(levels)):
            ip_str = "ip_addr"
            if msb < stride_length - 1:
                ip_str = f"(ip_addr << {stride_length - 1 - msb})"
                msb = stride_length - 1
            ingress += (f"\n\n        stride = {ip_str}[{msb}:{msb-stride_length+1}];"
                        f"\n        layer_{lvl}_inst.apply(next_hop_idx, stride, node_idx, done);"
                        "\n        if(done){ "
                        f"\n          set_res_{lvl}_inst.apply(next_hop_idx, hdr, std_meta);"
                        "\n          return;"
                        "\n        }"
                       )
            msb -= stride_length
        
        ingress += "\n    }\n}\n"
        f.write(ingress)
