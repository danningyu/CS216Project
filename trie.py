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
    
    def p4_repr(self, num):
        outFace = self.outFace
        if self.outFace is None:
            outFace = 99
        
        return f"const node_t n{num} = {{{isNotNone_to_str(self.outFace)}, {outFace}, {isNotNone_to_str(self.left)}, {isNotNone_to_str(self.right)}}};"

prefixes = {
    # "101": 1,
    "111": 2,
    # "11001": 3,
    "1": 4,
    "0": 5,
    # "1000": 6,
    # "100000": 7,
    # "100": 8,
    # "110": 9
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
bfs = []
# bfs = [(root, 0)]
depth = 0

while len(queue) > 0:
    length = len(queue)
    for i in range(length):
        node = queue.popleft()
        bfs.append((node, depth))
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
        
    depth += 1

with open("var_decls.p4", "w") as f:
    for i, node_depth in enumerate(bfs):
        n, depth = node_depth
        print(n, depth)
        f.write(n.p4_repr(i) + "\n")
        print("\t" + n.p4_repr(i))

with open("control_decls.p4", "w") as f:
    for i, node_depth in enumerate(bfs):
        n, depth = node_depth
        control_decl = (
            f"control prefixMatch{i}(inout bit<8> ipAddr, inout bit<8> outputFace, out bool hasLeft, out bool hasRight) {{"
            f"\n\taction match{i}(){{"
            f"\n\t\tif(n{i}.hasPrefix){{ outputFace = n{i}.outputFace; }}"
            f"\n\t\thasLeft = n{i}.hasLeft;"
            f"\n\t\thasRight = n{i}.hasRight;"
            f"\n\t}}"
            f"\n"
            f"\n\ttable matcher {{"
            f"\n\t\tkey = {{ ipAddr: exact; }}"
            f"\n\t\tactions = {{ match{i}; }}"
            f"\n\t\tconst default_action = match{i};"
            f"\n\t}}"
            f"\n"
            f"\n\tapply {{ matcher.apply(); }}"
            f"\n}}"
            f"\n"
        )
        
        f.write(control_decl + "\n")

with open("ingress.p4", "w") as f:
    for i, node_depth in enumerate(bfs):
        control_inst = f"\tprefixMatch{i}() prefixMatch{i}_instance;"
        f.write(control_inst + "\n")
    
    text = (
        "\n\tbit<8> ipAddr;"
        "\n\tbit<8> outputFace;"
        "\n\tbool hasLeft;"
        "\n\tbool hasRight;"
        "\n\tnode_t curr_node;"
        "\n\tapply {"
        "\n\t\tipAddr = hdr.standard.src;"
        "\n\t\tcurr_node = root;"
        "\n\t\toutputFace = 99;"
        "\n\t\thasLeft = false;"
        "\n\t\thasRight = false;"

        "\n\t}"
    )

    f.write(text + "\n")

masks = [
    # 8 bit masks for now, adjust later
    0x80, 0x40, 0x20, 0x10,
    0x08, 0x04, 0x02, 0x01
]

with open("tree_traversal.p4", "w") as f:
    for i, node_depth in enumerate(bfs):
        if i == 0:
            # root layer
            text = (
                f"\n\t\tprefixMatch{i}_instance.apply(hdr.standard.src, outputFace, hasLeft, hasRight)"
            )
            f.write(text + "\n")
        else:
            
    
    text = (
        "\n\tbit<8> ipAddr;"
        "\n\tbit<8> outputFace;"
        "\n\tbool hasLeft;"
        "\n\tbool hasRight;"
        "\n\tnode_t curr_node;"
        "\n\tapply {"
        "\n\t\tipAddr = hdr.standard.src;"
        "\n\t\tcurr_node = root;"
        "\n\t\toutputFace = 99;"
        "\n\t\thasLeft = false;"
        "\n\t\thasRight = false;"

        "\n\t}"
    )

    f.write(text + "\n")
