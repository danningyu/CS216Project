#include <core.p4>
#include <v1model.p4>

const int MAX_HOPS = 10;
const int STANDARD = 0x00;
const int HOPS = 0x01;

typedef standard_metadata_t std_meta_t;

header standard_t {
  bit<8> src;
  bit<8> dst;
  bit<8> outputFace;
}

struct headers_t {
  standard_t standard;
}
///////////////////////////////////////////////////////////////////////////////
struct node_t {
    bool hasPrefix;
    bit<8> outputFace; // special value of 99 if does not exist
    bool hasLeft;
    bit<8> lIdx; // for 0 bit, index of node in next layer
    bool hasRight;
    bit<8> rIdx; // for 1 bit, index of node in next layer
    
}

const node_t root = {false, 99, true, 0, true, 1};
const node_t n1 = {true, 5, false, 0, false, 0};
const node_t n2 = {true, 4, false, 0, true, 0};
const node_t n3 = {false, 99, false, 0, true, 0};
const node_t n4 = {true, 2, false, 0, false, 0};

const tuple<node_t> layer0 = {root};
const tuple<node_t, node_t> layer1 = {n1, n2};
const tuple<node_t> layer2 = {n3};
const tuple<node_t> layer3 = {n4};

///////////////////////////////////////////////////////////////////////////////

const bit<8> hello = 0x00;

struct meta_t { }

parser MyParser(packet_in pkt, out headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {
    state start {
        transition parse_standard;
    }
    
    state parse_standard {
        pkt.extract(hdr.standard);
        transition accept;
    }
}

control MyVerifyChecksum(inout headers_t hdr, inout meta_t meta) {
    apply { }
}

control MyComputeChecksum(inout headers_t hdr, inout meta_t meta) {
    apply { }
}

control prefixMatch0(inout bit<8> ipAddr, inout bit<8> outputFace, out bool hasLeft, out bool hasRight) {
    action match0 () {
        if(root.hasPrefix){
            outputFace = root.outputFace;
        }
        hasLeft = root.hasLeft;
        hasRight = root.hasRight;
    }

    table matcher {
        key = { ipAddr: exact; }
        actions = { match0; }
        const default_action = match0;
    }

    apply { matcher.apply(); }
}

control prefixMatch1(inout bit<8> ipAddr, inout bit<8> outputFace, out bool hasLeft, out bool hasRight) {
    action match1 () {
        if(n1.hasPrefix){
            outputFace = n1.outputFace;
        }
        hasLeft = n1.hasLeft;
        hasRight = n1.hasRight;
    }

    table matcher {
        key = { ipAddr: exact; }
        actions = { match1; }
        const default_action = match1;
    }

    apply {
        matcher.apply();
    }
}

control prefixMatch2(inout bit<8> ipAddr, inout bit<8> outputFace, out bool hasLeft, out bool hasRight) {
    action match2 () {
        if(n2.hasPrefix){
            outputFace = n2.outputFace;
        }
        hasLeft = n2.hasLeft;
        hasRight = n2.hasRight;
    }

    table matcher {
        key = { ipAddr: exact; }
        actions = { match2; }
        const default_action = match2;
    }

    apply { matcher.apply(); }
}

control prefixMatch3(inout bit<8> ipAddr, inout bit<8> outputFace, out bool hasLeft, out bool hasRight) {
    action match3 () {
        if(n3.hasPrefix){
            outputFace = n3.outputFace;
        }
        hasLeft = n3.hasLeft;
        hasRight = n3.hasRight;
    }

    table matcher {
        key = { ipAddr: exact; }
        actions = { match3; }
        const default_action = match3;
    }

    apply { matcher.apply(); }
}

control prefixMatch4(inout bit<8> ipAddr, inout bit<8> outputFace, out bool hasLeft, out bool hasRight) {
    action match4 () {
        if(n4.hasPrefix){
            outputFace = n4.outputFace;
        }
        hasLeft = n4.hasLeft;
        hasRight = n4.hasRight;
    }

    table matcher {
        key = { ipAddr: exact; }
        actions = { match4; }
        const default_action = match4;
    }

    apply { matcher.apply(); }
}

control MyIngress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {
    prefixMatch0() prefixMatch0_inst1;
    prefixMatch1() prefixMatch1_inst1;
    prefixMatch2() prefixMatch2_inst1;
    prefixMatch3() prefixMatch3_inst1;
    prefixMatch4() prefixMatch4_inst1;
    bit<8> ipAddr;
    bit<8> outputFace;
    bool hasLeft;
    bool hasRight;
    node_t curr_node;
    tuple<bit<2>, bit<2>> test = {1, 2};
    bit<2> test2 = test[0];

    apply {
        ipAddr = hdr.standard.src;
        curr_node = root;
        outputFace = 99;
        hasLeft = false;
        hasRight = false;

        // layer 0
        if(curr_node.hasPrefix){
            outputFace = curr_node.outputFace;
        }
        if(curr_node.lIdx != -1 && (ipAddr & 0x80) >> 7 == 0){
            curr_node = layer1[curr_node.lIdx];
        } else if(curr_node.rIdx != -1 && (ipAddr & 0x80) >> 7 == 1) {
            curr_node = layer1[curr_node.rIdx];
        } else {
            return; // reached a leaf node
        }

        // layer 1
        if(curr_node.hasPrefix){
            outputFace = curr_node.outputFace;
        }
        if(curr_node.lIdx != -1 && (ipAddr & 0x40) >> 6 == 0){
            curr_node = layer2[curr_node.lIdx];
        } else if(curr_node.rIdx != -1 && (ipAddr & 0x40) >> 6 == 1) {
            curr_node = layer2[curr_node.rIdx];
        } else {
            return; // reached a leaf node
        }

        // layer 2
        if(curr_node.hasPrefix){
            outputFace = curr_node.outputFace;
        }
        if(curr_node.lIdx != -1 && (ipAddr & 0x20) >> 5 == 0){
            curr_node = layer3[curr_node.lIdx];
        } else if(curr_node.rIdx != -1 && (ipAddr & 0x20) >> 5 == 1) {
            curr_node = layer3[curr_node.rIdx];
        } else {
            return; // reached a leaf node
        }

        // layer 3
        if(curr_node.hasPrefix){
            outputFace = curr_node.outputFace;
        }
        // last layer so don't try to advance farther
        // if(curr_node.lIdx != -1 && (ipAddr & 0x20) >> 5 == 0){
        //     curr_node = layer3[curr_node.lIdx];
        // } else if(curr_node.rIdx != -1 && (ipAddr & 0x20) >> 5 == 1) {
        //     curr_node = layer3[curr_node.rIdx];
        // } else {
        //     return; // reached a leaf node
        // }



        
        // // Layer 1: root
        // prefixMatch0_inst1.apply(hdr.standard.src, outputFace, hasLeft, hasRight);
        
        // // Layer 2: first bit
        // if(hasLeft && (ipAddr & 0x80) >> 7 == 0){
        //     prefixMatch1_inst1.apply(hdr.standard.src, outputFace, hasLeft, hasRight);
        //     curr_node = n1;
        //     hdr.standard.outputFace = outputFace;
        //     // return;
        // } else if(hasRight && (ipAddr & 0x80) >> 7 == 1){
        //     prefixMatch2_inst1.apply(hdr.standard.src, outputFace, hasLeft, hasRight);
        //     curr_node = n2;
        //     hdr.standard.outputFace = outputFace;
        //     // return;
        // }

        // // Layer 2: second bit
        // // n2 has no left node so we don't need to check it
        // if(curr_node == n2 && hasRight && (ipAddr & 0x40) >> 6 == 1){
        //     prefixMatch3_inst1.apply(hdr.standard.src, outputFace, hasLeft, hasRight);
        //     curr_node = n3;
        //     hdr.standard.outputFace = outputFace;
        //     // return;
        // }

        // // Layer 3: third bit
        // if(curr_node == n3 && hasRight && (ipAddr & 0x20) >> 5 == 1){
        //     prefixMatch4_inst1.apply(hdr.standard.src, outputFace, hasLeft, hasRight);
        //     curr_node = n4;
        //     hdr.standard.outputFace = outputFace;
        //     // return;
        // }
    }
}

control MyEgress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {
    apply { }
}

control MyDeparser(packet_out pkt, in headers_t hdr) {
    apply {
        pkt.emit(hdr.standard);
    }
}

V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;
