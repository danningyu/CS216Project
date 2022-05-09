	prefixMatch0() prefixMatch0_instance;
	prefixMatch1() prefixMatch1_instance;
	prefixMatch2() prefixMatch2_instance;
	prefixMatch3() prefixMatch3_instance;
	prefixMatch4() prefixMatch4_instance;

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
	}
