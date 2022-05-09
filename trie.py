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

root = Node("root")

nodes = [root]

for k, v in prefixes.items():
    curr_node = root
    val = ""
    for bit in k:
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
    
    curr_node.outFace = v

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
            
            hasLeft = isNotNone_to_str(n.left)
            lIdx = 0
            if n.left is not None:
                lIdx = n.left.uniq_id
            
            hasRight = isNotNone_to_str(n.right)
            rIdx = 0
            if n.right is not None:
                rIdx = n.right.uniq_id
            
            text = f"\nconst node_t n{tree_depth}_{i} = {{{hasPrefix}, {outFace}, {hasLeft}, {lIdx}, {hasRight}, {rIdx}}};"
            f.write(text)

            print("\t" + text[1:])

print("=========================================================")

# For now, 8 bits
IP_ADDR_WIDTH = 8

masks = [
    # 8 bit masks for now, adjust later
    0x80, 0x40, 0x20, 0x10,
    0x08, 0x04, 0x02, 0x01
]

with open("control_decls.p4gen", "w") as f:
    for tree_depth, node_list in enumerate(bfs):
        start = f"control layer{tree_depth}Match(inout bit<8> ipAddr, inout bit<8> idx, inout bit<8> outputFace, inout bool done){{"
        f.write(start)

        for i, node_depth in enumerate(node_list):
            n, depth = node_depth
            node_var_name = f"n{tree_depth}_{i}"
            print(f"{tree_depth=} {i=} {n.val=} {depth=}")
            action_decl = (
                f"\n    action match{i}(){{"
                f"\n        if({node_var_name}.hasPrefix){{ outputFace = {node_var_name}.outputFace; }}"
            )

            if tree_depth < IP_ADDR_WIDTH:
                action_decl += (
                    f"\n        if({node_var_name}.hasLeft && (ipAddr & 0x{masks[tree_depth]:02x}) >> {IP_ADDR_WIDTH - 1 - tree_depth} == 0){{"
                    f"\n            idx = {node_var_name}.lIdx;"
                    f"\n        }} else if({node_var_name}.hasRight && (ipAddr & 0x{masks[tree_depth]:02x}) >> {IP_ADDR_WIDTH - 1 - tree_depth} == 1){{"
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
        f"\n    bit<8> ipAddr = hdr.standard.src;"
        f"\n    bit<8> outputFace = 99;"
        f"\n    bit<8> idx = 0;"
        f"\n    bool done = false;"
        f"\n    apply {{"
    )

    f.write(text + "\n")

    for tree_depth, node_list in enumerate(bfs):
        control_inst = (
            f"\n        layer{tree_depth}Match_inst.apply(hdr.standard.src, idx, outputFace, done);"
            f"\n        hdr.standard.outputFace = outputFace;"
            f"\n        if(done){{ return; }}"
        )
        f.write(control_inst + "\n")

        for i, node_depth in enumerate(node_list):
            n, depth = node_depth
    
    f.write("    }\n") # close the apply block
    f.write("}\n") # close the control block
