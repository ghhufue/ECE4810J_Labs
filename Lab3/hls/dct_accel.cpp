#include "../lab3_starter/dct/dct.h"
void dct_accel(int input[64], int output[64], unsigned inverse) {
#pragma HLS INTERFACE s_axilite port=input bundle=CTRL
#pragma HLS INTERFACE s_axilite port=output bundle=CTRL
#pragma HLS INTERFACE s_axilite port=inverse bundle=CTRL
#pragma HLS INTERFACE s_axilite port=return bundle=CTRL
    short src[64], dst[64];
    for(int i=0;i<64;++i) src[i]=(short)input[i];
    if(inverse) idct(src,dst); else dct(src,dst);
    for(int i=0;i<64;++i) output[i]=dst[i];
}
