control prefixMatch0(inout bit<8> ipAddr, inout bit<8> outputFace, out bool hasLeft, out bool hasRight) {
	action match0(){
		if(n0.hasPrefix){ outputFace = n0.outputFace; }
		hasLeft = n0.hasLeft;
		hasRight = n0.hasRight;
	}

	table matcher {
		key = { ipAddr: exact; }
		actions = { match0; }
		const default_action = match0;
	}

	apply { matcher.apply(); }
}

control prefixMatch1(inout bit<8> ipAddr, inout bit<8> outputFace, out bool hasLeft, out bool hasRight) {
	action match1(){
		if(n1.hasPrefix){ outputFace = n1.outputFace; }
		hasLeft = n1.hasLeft;
		hasRight = n1.hasRight;
	}

	table matcher {
		key = { ipAddr: exact; }
		actions = { match1; }
		const default_action = match1;
	}

	apply { matcher.apply(); }
}

control prefixMatch2(inout bit<8> ipAddr, inout bit<8> outputFace, out bool hasLeft, out bool hasRight) {
	action match2(){
		if(n2.hasPrefix){ outputFace = n2.outputFace; }
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
	action match3(){
		if(n3.hasPrefix){ outputFace = n3.outputFace; }
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
	action match4(){
		if(n4.hasPrefix){ outputFace = n4.outputFace; }
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

