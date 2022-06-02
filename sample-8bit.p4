#include <core.p4>
#include <v1model.p4>

typedef standard_metadata_t std_meta_t;

struct meta_t { }

header standard_t {
  bit<8> src;
  bit<8> dst;
  bit<8> outputFace;
}
struct headers_t {
  standard_t standard;
}

parser MyParser(packet_in pkt, out headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {
    state start {
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

control layer_0(inout bit<8> next_hop_idx, inout bit<3> stride, inout bit<8> node_idx, inout bool done) {
    action fail() {
      done = true;
    }
    action set_next_hop_idx(bit<8> idx) {
      next_hop_idx = idx;
    }
    action set_node_idx(bit<8> idx) {
      node_idx = idx;
    }

    table internal_0_0 {
      key = { stride: exact; }
      actions = {
        set_next_hop_idx;
      }
      const entries = {
        0: set_next_hop_idx(1);
        1: set_next_hop_idx(1);
        2: set_next_hop_idx(1);
        3: set_next_hop_idx(1);
        4: set_next_hop_idx(2); 
        5: set_next_hop_idx(3);
      }
      default_action = set_next_hop_idx(0);
    }
    table external_0_0 {
      key = { stride: exact; }
      actions = {
        set_node_idx;
        fail;
      }
      const entries = {
        1: set_node_idx(0);
        7: set_node_idx(1);
      }
      default_action = fail();
    }

    apply {
      if (node_idx == 0) {
        internal_0_0.apply();
        external_0_0.apply();
      } else {
        fail();
      }
    }
}

control layer_1(inout bit<8> next_hop_idx, inout bit<3> stride, inout bit<8> node_idx, inout bool done) {
    action fail() {
      done = true;
    }
    action set_next_hop_idx(bit<8> idx) {
      next_hop_idx = idx;
    }
    action set_node_idx(bit<8> idx) {
      node_idx = idx;
    }
    action nop() {}

    table internal_1_0 {
      key = { stride: exact; }
      actions = {
        set_next_hop_idx;
      }
      const entries = {
      }
      default_action = set_next_hop_idx(3);
    }
    table external_1_0 {
      key = { stride: exact; }
      actions = {
        set_node_idx;
        fail;
      }
      const entries = {
      }
      default_action = fail();
    }

    table internal_1_1 {
      key = { stride: exact; }
      actions = {
        nop;
      }
      const entries = {
      }
      default_action = nop();
    }
    table external_1_1 {
      key = { stride: exact; }
      actions = {
        set_node_idx;
        fail;
      }
      const entries = {
        7: set_node_idx(0);
      }
      default_action = fail();
    }

    apply {
      if (node_idx == 0) {
        internal_1_0.apply();
        external_1_0.apply();
      } else if (node_idx == 1) {
        internal_1_1.apply();
        external_1_1.apply();
      } else {
        fail();
      }
    }
}

control layer_2(inout bit<8> next_hop_idx, inout bit<3> stride, inout bit<8> node_idx, inout bool done) {
    action fail() {
      done = true;
    }
    action set_next_hop_idx(bit<8> idx) {
      next_hop_idx = idx;
    }
    action set_node_idx(bit<8> idx) {
      node_idx = idx;
    }

    table internal_2_0 {
      key = { stride: exact; }
      actions = {
        set_next_hop_idx;
      }
      const entries = {
      }
      default_action = set_next_hop_idx(4);
    }
    table external_2_0 {
      key = { stride: exact; }
      actions = {
        set_node_idx;
        fail;
      }
      const entries = {
      }
      default_action = fail();
    }

    apply {
      if (node_idx == 0) {
        internal_2_0.apply();
        external_2_0.apply();
      } else {
        fail();
      }
    }
}


control MyIngress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {
    layer_0() layer0_inst;
    layer_1() layer1_inst;
    layer_2() layer2_inst;

    bit<8> next_hop_idx;

    action set_output_face(bit<8> res) {
      hdr.standard.outputFace = res;
    }

    table result {
      key = { next_hop_idx: exact; }
      actions = {
        set_output_face;
      }
      const entries = {
        0: set_output_face(3);  // *
        1: set_output_face(2);  // 0*
        2: set_output_face(5);  // 10*
        3: set_output_face(1);  // 001*
        4: set_output_face(4);  // 111111*
      }
      default_action = set_output_face(0);
    }

    apply {
        bit<8> ip_addr = hdr.standard.src;
        bit<8> node_idx = 0;
        bool done = false;

        bit<3> stride = ip_addr[7:5];
        layer0_inst.apply(next_hop_idx, stride, node_idx, done);
        if(done){ 
          result.apply();
          return; 
        }

        stride = ip_addr[4:2];
        layer1_inst.apply(next_hop_idx, stride, node_idx, done);
        if(done){ 
          result.apply();
          return; 
        }

        stride = (ip_addr << 1)[2:0];
        layer2_inst.apply(next_hop_idx, stride, node_idx, done);
        result.apply();
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
