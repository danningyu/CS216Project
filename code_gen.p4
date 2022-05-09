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
struct node_t {
    bool hasPrefix;
    bit<8> outputFace; // special value of 99 if does not exist
    bool hasLeft;
    bit<8> lIdx; // for 0 bit, index of node in next layer
    bool hasRight;
    bit<8> rIdx; // for 1 bit, index of node in next layer
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

#include "control_decls.p4"

#include "ingress.p4"

control MyEgress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {
    apply { }
}

control MyDeparser(packet_out pkt, in headers_t hdr) {
    apply {
        pkt.emit(hdr.standard);
    }
}

V1Switch(MyParser(), MyVerifyChecksum(), MyIngress(), MyEgress(), MyComputeChecksum(), MyDeparser()) main;
