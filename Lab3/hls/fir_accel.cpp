#include "../lab3_starter/fir/fir.h"
void fir_accel(int sample, int clear, int *result) {
#pragma HLS INTERFACE s_axilite port=sample bundle=CTRL
#pragma HLS INTERFACE s_axilite port=clear bundle=CTRL
#pragma HLS INTERFACE s_axilite port=result bundle=CTRL
#pragma HLS INTERFACE s_axilite port=return bundle=CTRL
    if(clear) { fir_reset(); *result=0; }
    else fir(result,sample);
}
