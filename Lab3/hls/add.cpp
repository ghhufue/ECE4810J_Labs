void add(unsigned a, unsigned b, unsigned *c) {
#pragma HLS INTERFACE s_axilite port=a bundle=CTRL offset=0x10
#pragma HLS INTERFACE s_axilite port=b bundle=CTRL offset=0x18
#pragma HLS INTERFACE s_axilite port=c bundle=CTRL offset=0x20
#pragma HLS INTERFACE ap_ctrl_none port=return
    *c=a+b;
}
