from collections import deque

def isNotNone_to_str(val):
    if val is not None:
        return "true"
    else:
        return "false"

class Node:
    left = None
    right = None
    outFace = None
    uniq_id = None
    outPort = None

    def __init__(self, val):
        self.val = val
        # self.prefix = prefix
    
    def __str__(self):
        if self.left is not None and self.right is not None:
            return f"{self.val=} {self.outFace=} {self.left.val=} {self.right.val=}"
        elif self.left is not None:
            return f"{self.val=} {self.outFace=} {self.left.val=} None"
        elif self.right is not None:
            return f"{self.val=} {self.outFace=} None {self.right.val=}"
        else:
            return f"{self.val=} {self.outFace=} None None"

prefixes = {
    "0": (0xABCDEFABCDEF, 0), # 0.0.0.0/1
    "00001010 00000000 00000001 0000": (0x080000000110, 1), # 10.0.1.1/28
    "00001010 00000000 00000001 0001": (0x080000000120, 2), #10.0.1.17
    "00001010 00000000 000000":  (0x080000000210, 3), #10.0.0.1
    "00001010 00000000 0000001": (0x080000000220, 4), #10.0.2.17
}

root = Node("root")

nodes = [root]

for k, v in prefixes.items():
    curr_node = root
    val = ""
    for bit in k:
        if bit == " ":
            continue
        val += bit
        if bit == "0":
            if curr_node.left == None:
                curr_node.left = Node(val)
                nodes.append(curr_node.left)
            
            curr_node = curr_node.left
        else:
            if curr_node.right == None:
                curr_node.right = Node(val)
                nodes.append(curr_node.right)
            curr_node = curr_node.right
    
    curr_node.outFace = v[0]
    curr_node.outPort = v[1]

# for i, n in enumerate(nodes):
#     print(n)
#     print("\t" + n.p4_repr(i))

queue = deque([root])
bfs = [] # array of arrays, one array for each level
bfs_flat = []  # flattened version of `bfs`
# bfs = [(root, 0)]
depth = 0

while len(queue) > 0:
    length = len(queue)
    bfs.append([])
    for i in range(length):
        node = queue.popleft()
        node.uniq_id = i
        bfs[-1].append((node, depth))
        bfs_flat.append((node, depth))
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
        
    depth += 1

with open("var_decls.p4gen", "w") as f:
    for tree_depth, node_list in enumerate(bfs):
        for i, node_depth in enumerate(node_list):
            n, depth = node_depth

            print(n, "depth=" + str(depth))
            hasPrefix = isNotNone_to_str(n.outFace)

            outFace = n.outFace
            if n.outFace is None:
                outFace = 99 # the "default" value
            
            outPort = n.outPort
            if n.outPort is None:
                outPort = 0 # the "default" value
            
            hasLeft = isNotNone_to_str(n.left)
            lIdx = 0
            if n.left is not None:
                lIdx = n.left.uniq_id
            
            hasRight = isNotNone_to_str(n.right)
            rIdx = 0
            if n.right is not None:
                rIdx = n.right.uniq_id
            
            
            text = f"\nconst node_t n{tree_depth}_{i} = {{{hasPrefix}, 0x{outFace:012x}, {outPort}, {hasLeft}, {lIdx}, {hasRight}, {rIdx}}};"
            f.write(text)

            print("\t" + text[1:])

print("=========================================================")

# CHANGED to 32 bits
IP_ADDR_WIDTH = 32

masks = [
    # 8 bit masks for now, adjust later
    0x80000000, 0x40000000, 0x20000000, 0x10000000,
    0x08000000, 0x04000000, 0x02000000, 0x01000000,
    0x00800000, 0x00400000, 0x00200000, 0x00100000,
    0x00080000, 0x00040000, 0x00020000, 0x00010000,

    0x00008000, 0x00004000, 0x00002000, 0x00001000,
    0x00000800, 0x00000400, 0x00000200, 0x00000100,
    0x00000080, 0x00000040, 0x00000020, 0x00000010,
    0x00000008, 0x00000004, 0x00000002, 0x00000001
]

with open("control_decls.p4gen", "w") as f:
    for tree_depth, node_list in enumerate(bfs):
        start = f"control layer{tree_depth}Match(inout bit<32> ipAddr, inout bit<8> idx, inout bit<48> outputFace, inout bool done, inout bit<9> outputPort){{"
        f.write(start)

        for i, node_depth in enumerate(node_list):
            n, depth = node_depth
            node_var_name = f"n{tree_depth}_{i}"
            print(f"{tree_depth=} {i=} {n.val=} {depth=}")
            action_decl = (
                f"\n    action match{i}(){{"
                f"\n        if({node_var_name}.hasPrefix){{"
                f"\n            outputFace = {node_var_name}.outputFace;"
                f"\n            outputPort = {node_var_name}.outputPort;"
                f"\n        }}"
            )

            if tree_depth < IP_ADDR_WIDTH:
                action_decl += (
                    f"\n        if({node_var_name}.hasLeft && (ipAddr & 0x{masks[tree_depth]:08x}) >> {IP_ADDR_WIDTH - 1 - tree_depth} == 0){{"
                    f"\n            idx = {node_var_name}.lIdx;"
                    f"\n        }} else if({node_var_name}.hasRight && (ipAddr & 0x{masks[tree_depth]:08x}) >> {IP_ADDR_WIDTH - 1 - tree_depth} == 1){{"
                    f"\n            idx = {node_var_name}.rIdx;"
                    f"\n        }} else {{"
                    f"\n            done = true;"
                    f"\n        }}"
                    f"\n    }}" # close action block
                )
            else:
                action_decl += (
                    f"\n        done = true;"
                    f"\n    }}" # close action block
                )
            
            f.write(action_decl + "\n")
        
        match_list = ""
        entry_list = ""
        for i, node_depth in enumerate(node_list):
            n, depth = node_depth
            match_list += f"            match{i};\n"
            entry_list += f"            {i}: match{i}();\n"
        
        match_list.rstrip('\n')
        entry_list.rstrip('\n')

        table_apply_decl = (
            f"\n    table matcher {{"
            f"\n        key = {{ idx: exact; }}"
            f"\n        actions = {{"
            f"\n{match_list}"
            f"        }}" # close actions block
            f"\n"
            f"\n        const entries = {{"
            f"\n{entry_list}"
            f"        }}" # close entries block
            f"\n    }}" # close table block
            f"\n"
            f"\n    apply {{ matcher.apply(); }}"
        )
        f.write(table_apply_decl + "\n")

        f.write("}" + "\n\n")

with open("ingress.p4gen", "w") as f:
    control_decl = f"control MyIngress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {{"
    f.write(control_decl + "\n")

    for tree_depth, node_list in enumerate(bfs):
        control_inst = f"    layer{tree_depth}Match() layer{tree_depth}Match_inst;"
        f.write(control_inst + "\n")

        for i, node_depth in enumerate(node_list):
            n, depth = node_depth

    text = (
        f"\n    bit<32> ipAddr = hdr.ipv4.dstAddr;"
        f"\n    bit<48> outputFace = 0xFFFFFFFFFF0F;"
        f"\n    bit<9> outputPort = 0;"
        f"\n    bit<8> idx = 0;"
        f"\n    bool done = false;"
        f"\n    apply {{"
    )

    f.write(text + "\n")

    # f.write("\n        std_meta.egress_spec = 2;")
    # f.write("\n        hdr.ethernet.dstAddr = 0x080000000120;")
    # f.write("\n        return;")

    for tree_depth, node_list in enumerate(bfs):
        control_inst = (
            f"\n        layer{tree_depth}Match_inst.apply(hdr.ipv4.dstAddr, idx, outputFace, done, outputPort);"
            f"\n        hdr.ethernet.dstAddr = outputFace;"
            f"\n        std_meta.egress_spec = outputPort;"
            f"\n        if(done){{ return; }}"
        )
        f.write(control_inst + "\n")

        for i, node_depth in enumerate(node_list):
            n, depth = node_depth
    
    f.write("    }\n") # close the apply block
    f.write("}\n") # close the control block
