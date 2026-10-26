#include <cstdio>
#include <cstdint>
#include "../lab3_starter/dct/dct.h"
#include "dct_vectors.h"
void dct_accel(int input[64],int output[64],unsigned inverse);
void fir_accel(int sample,int clear,int *result);
void add(unsigned,unsigned,unsigned*);
#if defined(TEST_DCT)
int main() {
    int in[64],out[64],errors=0;
    for(int t=0;t<DCT_TEST_COUNT;++t) {
        for(int i=0;i<64;++i) in[i]=dct_inputs[t][i];
        dct_accel(in,out,0);
        for(int i=0;i<64;++i) { if(out[i]!=dct_expected[t][i]) ++errors; in[i]=out[i]; }
        dct_accel(in,out,1);
        for(int i=0;i<64;++i) if(out[i]!=idct_expected[t][i]) ++errors;
    }
    std::printf("AXI DCT/IDCT: %d blocks, %d failures\n",DCT_TEST_COUNT,errors);
    return errors!=0;
}
#elif defined(TEST_FIR)
static const int coefficients[128]={
#include "fir_coefficients.h"
};
int main() {
    int history[128]={0},out,errors=0;
    unsigned state=48103;
    fir_accel(0,1,&out);
    for(int i=0;i<1024;++i) {
        if(i==512) {fir_accel(0,1,&out);for(int j=0;j<128;++j)history[j]=0;}
        state=1664525u*state+1013904223u;
        int sample=(int)(state>>24)-128,expected=0;
        for(int j=127;j>0;--j)history[j]=history[j-1];
        history[0]=sample;
        for(int j=0;j<128;++j) expected+=history[j]*coefficients[j];
        fir_accel(sample,0,&out);
        if(out!=expected)++errors;
    }
    std::printf("AXI FIR: 1024 samples plus reset, %d failures\n",errors);
    return errors!=0;
}
#elif defined(TEST_ADD)
int main() {
    unsigned values[]={0,1,0xffffffffu,0x80000000u,0x7fffffffu,12345},out;
    int errors=0;
    for(unsigned a:values)for(unsigned b:values){add(a,b,&out);if(out!=a+b)++errors;}
    std::printf("AXI ADD: 36 vectors, %d failures\n",errors);
    return errors!=0;
}
#endif
