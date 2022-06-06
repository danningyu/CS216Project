import math

def isNotNone_to_str(val):
    if val is not None:
        return "true"
    else:
        return "false"

# strides are len 4 - internalBitmap is 15 bits, externalBitmap is 16 bits
class Node:                    
    def __init__(self):
        self.internalBitmap = 0 # 15 bits
        self.externalBitmap = 0 # 16 bits
        # outFace/nextHop is 99 by default
        self.outFaceArray = [99]*15 # need to change this to individual variables when
                                    # translating to p4
    
    def __str__(self):
        return f"{self.internalBitmap=} {self.externalBitmap=} {self.outFaceArray=}"

# assume 16 bit IP addresses, for 4 bit strides
# 5 (4+1) possible layers, but each node has 16 children
prefixes = {
    "101": 1,
    "111": 2,
    "11001": 3,
    "1": 4,
    "0": 5,
    "1000": 6,
    "100000": 7,
    "100": 8,
    "110": 9,
    "11110000": 10
}

root = Node()
nodes = [None] * 1048575 # "nodemap" in level order traversal for all nodes
nodes[0] = root

# create nodes based on prefix inputs
# basically need to create nodes as needed based on prefixes
# only update the internal bitmap on exact match of prefix
# must upload externalBitmap as we create children nodes
for ip, next_hop in prefixes.items():
    curr_node = root
    curr_node_index = 0 # index of node within nodes array
    curr_index = 0 # index of node within multibit node
    for bit in ip:
        if bit == "0":
            # check if index in last layer of multi-bit trie, 
            # if so, create new node and set curr_index = 0
            # set external bitmap accordingly
            if curr_index >= 7:
                # add 1 to externalBitmap to mark that we need to create a child
                mask = 2**(14-2*(curr_index-7)+1)
                curr_node.externalBitmap = curr_node.externalBitmap | mask
                # set curr_node to child or if no child, create one
                curr_node_index = 16*curr_node_index+(2*(curr_index-7)+1) # node tree is a 16-ary tree
                if nodes[curr_node_index] == None:
                    curr_node = Node()
                    nodes[curr_node_index] = curr_node
                else:
                    curr_node = nodes[curr_node_index]
                curr_index = 0
            else:
                curr_index = 2*curr_index+1
        else:
            # check if index in last layer of multi-bit trie, 
            # if so, create new node and set curr_index = 0
            # set external bitmap accordingly
            if curr_index >= 7:
                # add 1 to externalBitmap to mark that we need to create a child
                mask = 2**(14-2*(curr_index-7))
                curr_node.externalBitmap = curr_node.externalBitmap | mask
                # set curr_node to child or if no child, create one
                curr_node_index = 16*curr_node_index+(2*(curr_index-7)+2)
                if nodes[curr_node_index] == None:
                    curr_node = Node()
                    nodes[curr_node_index] = curr_node
                else:
                    curr_node = nodes[curr_node_index]
                curr_index = 0
            else:
                curr_index = 2*curr_index+2
    # end of prefix, must update internal bitmap and outface array
    curr_node.internalBitmap = curr_node.internalBitmap | 2**(14-curr_index)
    curr_node.outFaceArray[curr_index] = next_hop

# for i, n in enumerate(nodes):
#     if n != None:
#         print(i, n)

# append variable declarations to .p4 file
with open("var_decls.p4gen", "w") as f:
    for index, node in enumerate(nodes):
        if node != None:
            tree_level = math.floor(math.log(15*index+1)/math.log(16)) # level in tree
            level_index = index - math.floor((16**(tree_level) - 1)/15) # index of node within level (0-indexed)
            outfaces = str(node.outFaceArray[0])
            for i in range(1, 15):
                outfaces += ", "
                outfaces += str(node.outFaceArray[i])
            text = f"\nconst tbmnode_t nlevel_{tree_level}_{level_index} = {{{node.internalBitmap}, {node.externalBitmap}, {outfaces}}};"
            f.write(text)
            # print(text)

# print("=========================================================")

IP_ADDR_WIDTH = 32

# masks = [
#     # 8 bit masks for now, adjust later
#     0x80, 0x40, 0x20, 0x10,
#     0x08, 0x04, 0x02, 0x01
# ]

# with open("control_decls.p4gen", "w") as f:
#     for tree_depth, node_list in enumerate(bfs):
#         start = f"control layer{tree_depth}Match(inout bit<8> ipAddr, inout bit<8> idx, inout bit<8> outputFace, inout bool done){{"
#         f.write(start)

#         for i, node_depth in enumerate(node_list):
#             n, depth = node_depth
#             node_var_name = f"n{tree_depth}_{i}"
#             print(f"{tree_depth=} {i=} {n.val=} {depth=}")
#             action_decl = (
#                 f"\n    action match{i}(){{"
#                 f"\n        if({node_var_name}.hasPrefix){{ outputFace = {node_var_name}.outputFace; }}"
#             )

#             if tree_depth < IP_ADDR_WIDTH:
#                 action_decl += (
#                     f"\n        if({node_var_name}.hasLeft && (ipAddr & 0x{masks[tree_depth]:02x}) >> {IP_ADDR_WIDTH - 1 - tree_depth} == 0){{"
#                     f"\n            idx = {node_var_name}.lIdx;"
#                     f"\n        }} else if({node_var_name}.hasRight && (ipAddr & 0x{masks[tree_depth]:02x}) >> {IP_ADDR_WIDTH - 1 - tree_depth} == 1){{"
#                     f"\n            idx = {node_var_name}.rIdx;"
#                     f"\n        }} else {{"
#                     f"\n            done = true;"
#                     f"\n        }}"
#                     f"\n    }}" # close action block
#                 )
#             else:
#                 action_decl += (
#                     f"\n        done = true;"
#                     f"\n    }}" # close action block
#                 )
            
#             f.write(action_decl + "\n")
        
#         match_list = ""
#         entry_list = ""
#         for i, node_depth in enumerate(node_list):
#             n, depth = node_depth
#             match_list += f"            match{i};\n"
#             entry_list += f"            {i}: match{i}();\n"
        
#         match_list.rstrip('\n')
#         entry_list.rstrip('\n')

#         table_apply_decl = (
#             f"\n    table matcher {{"
#             f"\n        key = {{ idx: exact; }}"
#             f"\n        actions = {{"
#             f"\n{match_list}"
#             f"        }}" # close actions block
#             f"\n"
#             f"\n        const entries = {{"
#             f"\n{entry_list}"
#             f"        }}" # close entries block
#             f"\n    }}" # close table block
#             f"\n"
#             f"\n    apply {{ matcher.apply(); }}"
#         )
#         f.write(table_apply_decl + "\n")

#         f.write("}" + "\n\n")

# with open("ingress.p4gen", "w") as f:
#     control_decl = f"control MyIngress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {{"
#     f.write(control_decl + "\n")

#     for tree_depth, node_list in enumerate(bfs):
#         control_inst = f"    layer{tree_depth}Match() layer{tree_depth}Match_inst;"
#         f.write(control_inst + "\n")

#         for i, node_depth in enumerate(node_list):
#             n, depth = node_depth

#     text = (
#         f"\n    bit<8> ipAddr = hdr.standard.src;"
#         f"\n    bit<8> outputFace = 99;"
#         f"\n    bit<8> idx = 0;"
#         f"\n    bool done = false;"
#         f"\n    apply {{"
#     )

#     f.write(text + "\n")

#     for tree_depth, node_list in enumerate(bfs):
#         control_inst = (
#             f"\n        layer{tree_depth}Match_inst.apply(hdr.standard.src, idx, outputFace, done);"
#             f"\n        hdr.standard.outputFace = outputFace;"
#             f"\n        if(done){{ return; }}"
#         )
#         f.write(control_inst + "\n")

#         for i, node_depth in enumerate(node_list):
#             n, depth = node_depth
    
#     f.write("    }\n") # close the apply block
#     f.write("}\n") # close the control block
