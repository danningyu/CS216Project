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

// const tuple<node_t> layer0 = {root};
// const tuple<node_t, node_t> layer1 = {n1, n2};
// const tuple<node_t> layer2 = {n3};
// const tuple<node_t> layer3 = {n4};

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

control layer0Match(inout bit<8> ipAddr, inout bit<8> idx, inout bit<8> outputFace, inout bool done){
    action match0(){
        outputFace = root.outputFace;
        if(root.hasLeft && (ipAddr & 0x80) >> 7 == 0){
            idx = root.lIdx;
        } else if(root.hasRight && (ipAddr & 0x80) >> 7 == 1){
            idx = root.rIdx;
        } else {
            done = true;
        }
    }

    table matcher {
        key = { idx: exact; }
        actions = {
            match0;
        }

        const entries = {
            0: match0();
        }
    }

    apply {
        matcher.apply();
    }
}


control layer1Match(inout bit<8> ipAddr, inout bit<8> idx, inout bit<8> outputFace, inout bool done){
    action match0(){
        outputFace = n1.outputFace;
        if(n1.hasLeft && (ipAddr & 0x40) >> 6 == 0){
            idx = n1.lIdx;
        } else if(n1.hasRight && (ipAddr & 0x40) >> 6 == 0){
            idx = n1.rIdx;
        } else {
            done = true;
        }
    }

    action match1(){
        outputFace = n2.outputFace;
        if(n2.hasLeft && (ipAddr & 0x40) >> 6 == 0){
            idx = n2.lIdx;
        } else if(n2.hasRight && (ipAddr & 0x40) >> 6 == 0){
            idx = n2.rIdx;
        } else {
            done = true;
        }
    }

    table matcher {
        key = { idx: exact; }
        actions = {
            match0;
            match1;
        }

        const entries = {
            0: match0();
            1: match1();
        }
    }

    apply {
        matcher.apply();
    }
}

control MyIngress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {
    layer0Match() layer0Match_inst;
    layer1Match() layer1Match_inst;
    bit<8> ipAddr;
    bit<8> outputFace;
    bool hasLeft;
    bool hasRight;
    node_t curr_node;

    apply {
        ipAddr = hdr.standard.src;
        curr_node = root;
        outputFace = 99;
        hasLeft = false;
        hasRight = false;
        bit<8> idx = 0;
        bool done = false;

        layer0Match_inst.apply(hdr.standard.src, idx, outputFace, done);
        hdr.standard.outputFace = outputFace;
        if(done){ return; }

        layer1Match_inst.apply(hdr.standard.src, idx, outputFace, done);
        hdr.standard.outputFace = outputFace;
        if(done){ return; }
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
