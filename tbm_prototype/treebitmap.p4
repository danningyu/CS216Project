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

typedef bit<8> outputFace;

struct tbnode_t {
    bit<7> internalBitmap; // bitmap corresponding to presence of prefixes in internal trie nodes
    bit<8> pathsBitmap; //bitmap corresponding to presence of child prefixes in internal trie leaves

    outputFace[7] outputFaces; //not sure if this is right syntax, array of output faces for internal trie nodes
}

const tbnode_t root = {88,13,[1,99,2,3,99,99,99]}
const tbnode_t c1 = {32,0,[99,6,99,99,99,99,99]}
const tbnode_t c2 = {64,0,[4,99,99,99,99,99,99]}
const tbnode_t c3 = {68,0,[5,99,99,99,7,99,99]}

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

control layer0Match(inout bit<8> ipAddr, inout bit<8> idx, inout bit<8> outputFace, inout bool done){
    action match0(){
        //First we extract the first 2 bits of the ip address since our root node deals with prefixes of length <= 2

        bit<2> prefix = (ipAddr & 0xC0) >> 6;
        bool checkChild = false;

        //Now we check if there is a corresponding prefix for the first 2 bits


        //Case 1: There is a prefix corresponding to no bits e.g. the prefix *
        
        if(root.internalBitmap[0] == 1) //replace with shifting later
        {
            outputFace = root.outputFaces[0];
        }

        //Case 2: There is a prefix corresponding to the first bit e.g. 0*, 1*
                
        if((prefix == 0 || prefix == 1) && root.internalBitmap[1] == 1) //replace with shifting later
        {
            outputFace = root.outputFaces[1];
        }

        if((prefix == 2 || prefix == 3) && root.internalBitmap[2] == 1) //replace with shifting later
        {
            outputFace = root.outputFaces[2];
        }


        //Case 3: There is a prefix corresponding to the first 2 bits e.g. 00*, 11*, 01*, etc
                
        if(prefix == 0 && root.internalBitmap[3] == 1) //replace with shifting later
        {
            outputFace = root.outputFaces[3];
            checkChild = true;
        }

        if(prefix == 1 && root.internalBitmap[4] == 1) //replace with shifting later
        {
            outputFace = root.outputFaces[4];
            checkChild = true;
        }

        if(prefix == 2 && root.internalBitmap[5] == 1) //replace with shifting later
        {
            outputFace = root.outputFaces[5];
            checkChild = true;
        }
        
        if(prefix == 3 && root.internalBitmap[6] == 1) //replace with shifting later
        {
            outputFace = root.outputFaces[6];
            checkChild = true;
        }

        if(checkChild == false)
        {
            done = true;
            return;
        }

        //Now that we've gotten the longest match from within the node
        //We need to check if there's an even longer one at one of the children nodes
        //Need to use the pathsBitmap for this

        bit<3> fullPrefix = (ipAddr & 0xE0) >> 5; //The 3 bit full prefix corresponds to the 8 entries in the paths bitmap

        if(fullPrefix == 0 && root.pathsBitmap[0] == 1) //replace with shifting later
        {
            idx = 0 //We wanna examine child 0 in the layer below
        }

        if(fullPrefix == 1 && root.pathsBitmap[1] == 1) //replace with shifting later
        {
            idx = 1 //We wanna examine child 1 in the layer below
        }

        if(fullPrefix == 2 && root.pathsBitmap[2] == 1) //replace with shifting later
        {
            idx = 2 //We wanna examine child 2 in the layer below
        }

        if(fullPrefix == 3 && root.pathsBitmap[3] == 1) //replace with shifting later
        {
            idx = 3 //We wanna examine child 3 in the layer below
        }

        if(fullPrefix == 4 && root.pathsBitmap[4] == 1) //replace with shifting later
        {
            idx = 4 //We wanna examine child 4 in the layer below
        }

        if(fullPrefix == 5 && root.pathsBitmap[5] == 1) //replace with shifting later
        {
            idx = 5 //We wanna examine child 5 in the layer below
        }

        if(fullPrefix == 6 && root.pathsBitmap[6] == 1) //replace with shifting later
        {
            idx = 6 //We wanna examine child 6 in the layer below
        }

        if(fullPrefix == 7 && root.pathsBitmap[7] == 1) //replace with shifting later
        {
            idx = 7 //We wanna examine child 7 in the layer below
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
        done = true;
    }

    action match1(){
        done = true;
    }

    actionmatch2()
    {
        done = true;
    }

    actionmatch3()
    {
        done = true;
    }

    actionmatch4()
    {
        //First we extract the fourth & fifth bits of the ip address

        bit<2> prefix = (ipAddr & 0x18) >> 3;
        bool checkChild = false;

        //Now we check if there is a corresponding prefix for the fourth and fifth bits


        //Case 1: There is a prefix corresponding to no bits e.g. the prefix *
        
        if(c1.internalBitmap[0] == 1) //replace with shifting later
        {
            outputFace = c1.outputFaces[0];
        }

        //Case 2: There is a prefix corresponding to the first bit e.g. 0*, 1*
                
        if((prefix == 0 || prefix == 1) && c1.internalBitmap[1] == 1) //replace with shifting later
        {
            outputFace = c1.outputFaces[1];
        }

        if((prefix == 2 || prefix == 3) && c1.internalBitmap[2] == 1) //replace with shifting later
        {
            outputFace = c1.outputFaces[2];
        }


        //Case 3: There is a prefix corresponding to the first 2 bits e.g. 00*, 11*, 01*, etc
                
        if(prefix == 0 && c1.internalBitmap[3] == 1) //replace with shifting later
        {
            outputFace = c1.outputFaces[3];
            checkChild = true;
        }

        if(prefix == 1 && c1.internalBitmap[4] == 1) //replace with shifting later
        {
            outputFace = c1.outputFaces[4];
            checkChild = true;
        }

        if(prefix == 2 && c1.internalBitmap[5] == 1) //replace with shifting later
        {
            outputFace = c1.outputFaces[5];
            checkChild = true;
        }
        
        if(prefix == 3 && c1.internalBitmap[6] == 1) //replace with shifting later
        {
            outputFace = c1.outputFaces[6];
            checkChild = true;
        }

        if(checkChild == false)
        {
            done = true;
            return;
        }
        
        return;
    }

    actionmatch5()
    {
        //First we extract the fourth & fifth bits of the ip address

        bit<2> prefix = (ipAddr & 0x18) >> 3;
        bool checkChild = false;

        //Now we check if there is a corresponding prefix for the fourth and fifth bits


        //Case 1: There is a prefix corresponding to no bits e.g. the prefix *
        
        if(c2.internalBitmap[0] == 1) //replace with shifting later
        {
            outputFace = c2.outputFaces[0];
        }

        //Case 2: There is a prefix corresponding to the first bit e.g. 0*, 1*
                
        if((prefix == 0 || prefix == 1) && c2.internalBitmap[1] == 1) //replace with shifting later
        {
            outputFace = c2.outputFaces[1];
        }

        if((prefix == 2 || prefix == 3) && c2.internalBitmap[2] == 1) //replace with shifting later
        {
            outputFace = c2.outputFaces[2];
        }


        //Case 3: There is a prefix corresponding to the first 2 bits e.g. 00*, 11*, 01*, etc
                
        if(prefix == 0 && c2.internalBitmap[3] == 1) //replace with shifting later
        {
            outputFace = c2.outputFaces[3];
            checkChild = true;
        }

        if(prefix == 1 && c2.internalBitmap[4] == 1) //replace with shifting later
        {
            outputFace = c2.outputFaces[4];
            checkChild = true;
        }

        if(prefix == 2 && c2.internalBitmap[5] == 1) //replace with shifting later
        {
            outputFace = c2.outputFaces[5];
            checkChild = true;
        }
        
        if(prefix == 3 && c2.internalBitmap[6] == 1) //replace with shifting later
        {
            outputFace = c2.outputFaces[6];
            checkChild = true;
        }

        if(checkChild == false)
        {
            done = true;
            return;
        }
        
        return;
    }

    actionmatch6()
    {
        done = true;
    }

    actionmatch7()
    {
        //First we extract the fourth & fifth bits of the ip address

        bit<2> prefix = (ipAddr & 0x18) >> 3;
        bool checkChild = false;

        //Now we check if there is a corresponding prefix for the fourth and fifth bits


        //Case 1: There is a prefix corresponding to no bits e.g. the prefix *
        
        if(c3.internalBitmap[0] == 1) //replace with shifting later
        {
            outputFace = c3.outputFaces[0];
        }

        //Case 2: There is a prefix corresponding to the first bit e.g. 0*, 1*
                
        if((prefix == 0 || prefix == 1) && c3.internalBitmap[1] == 1) //replace with shifting later
        {
            outputFace = c3.outputFaces[1];
        }

        if((prefix == 2 || prefix == 3) && c3.internalBitmap[2] == 1) //replace with shifting later
        {
            outputFace = c3.outputFaces[2];
        }


        //Case 3: There is a prefix corresponding to the first 2 bits e.g. 00*, 11*, 01*, etc
                
        if(prefix == 0 && c3.internalBitmap[3] == 1) //replace with shifting later
        {
            outputFace = c3.outputFaces[3];
            checkChild = true;
        }

        if(prefix == 1 && c3.internalBitmap[4] == 1) //replace with shifting later
        {
            outputFace = c3.outputFaces[4];
            checkChild = true;
        }

        if(prefix == 2 && c3.internalBitmap[5] == 1) //replace with shifting later
        {
            outputFace = c3.outputFaces[5];
            checkChild = true;
        }
        
        if(prefix == 3 && c3.internalBitmap[6] == 1) //replace with shifting later
        {
            outputFace = c3.outputFaces[6];
            checkChild = true;
        }

        if(checkChild == false)
        {
            done = true;
            return;
        }
        
        return;
    }

    table matcher {
        key = { idx: exact; }
        actions = {
            match0;
            match1;
            match2;
            match3;
            match4;
            match5;
            match6;
            match7;
        }

        const entries = {
            0: match0();
            1: match1();
            2: match2();
            3: match3();
            4: match4();
            5: match5();
            6: match6();
            7: match7();
        }
    }

    apply {
        matcher.apply();
    }
}

control MyIngress(inout headers_t hdr, inout meta_t meta, inout std_meta_t std_meta) {
    layer0Match() layer0Match_inst;
    layer1Match() layer1Match_inst;

    bit<8> ipAddr = hdr.standard.dst;
    bit<8> outputFace;
    tbnode_t curr_node;

    apply {
        // ipAddr ;
        outputFace = 99;
        bit<8> idx = 0;
        bool done = false;

        layer0Match_inst.apply(hdr.standard.dst, idx, outputFace, done);
        hdr.standard.outputFace = outputFace;
        if(done){ return; }

        layer1Match_inst.apply(hdr.standard.dst, idx, outputFace, done);
        hdr.standard.outputFace = outputFace;
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