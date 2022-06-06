#include <core.p4>
#include <v1model.p4>

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
// stride length 4

struct tbmnode_t {
    bit<15> internalBitmap; // bitmap corresponding to presence of prefixes in internal trie nodes
    bit<16> externalBitmap; //bitmap corresponding to presence of child prefixes in internal trie leaves
    // 15 next-hop addresses for each node in multi-bit trie node
    bit<8> outputFace1;
    bit<8> outputFace2;
    bit<8> outputFace3;
    bit<8> outputFace4;
    bit<8> outputFace5;
    bit<8> outputFace6;
    bit<8> outputFace7;
    bit<8> outputFace8;
    bit<8> outputFace9;
    bit<8> outputFace10;
    bit<8> outputFace11;
    bit<8> outputFace12;
    bit<8> outputFace13;
    bit<8> outputFace14;
    bit<8> outputFace15;
}

#include "var_decls.p4"

///////////////////////////////////////////////////////////////////////////////
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

#include "control_decls.p4gen"

#include "ingress.p4gen"

control MyEgress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {
    apply { }
}

control MyDeparser(packet_out pkt, in headers_t hdr) {
    apply {
        pkt.emit(hdr.standard);
    }
}

V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;
