#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "platform.h"
#include "xil_io.h"
#include "xil_printf.h"
#include "xtime_l.h"
#include "dct_vectors.h"
#include "xdct_accel_hw.h"
#include "xfir_accel_hw.h"
#include "xadd_hw.h"
#include "xparameters.h"

#define DCT_BASE XPAR_DCT_ACCEL_0_S_AXI_CTRL_BASEADDR
#define FIR_BASE XPAR_FIR_ACCEL_0_S_AXI_CTRL_BASEADDR
#define ADD_BASE XPAR_SCALAR_ADD_S_AXI_CTRL_BASEADDR
static const int fir_coeff[128]={
#include "fir_coefficients.h"
};
static int wait_done(UINTPTR base) {
    XTime begin,now;
    XTime_GetTime(&begin);
    do {
        if(Xil_In32(base)&2u) return 0;
        XTime_GetTime(&now);
    } while(now-begin < COUNTS_PER_SECOND);
    xil_printf("TIMEOUT at 0x%08x\r\n",(unsigned)base);
    return 1;
}
static int hw_dct(const short *in,short *out,int inverse) {
    for(int i=0;i<64;++i) Xil_Out32(DCT_BASE+XDCT_ACCEL_CTRL_ADDR_INPUT_R_BASE+4*i,(uint32_t)(int32_t)in[i]);
    Xil_Out32(DCT_BASE+XDCT_ACCEL_CTRL_ADDR_INVERSE_DATA,(unsigned)inverse);
    Xil_Out32(DCT_BASE,1);
    if(wait_done(DCT_BASE))return 1;
    for(int i=0;i<64;++i)out[i]=(short)Xil_In32(DCT_BASE+XDCT_ACCEL_CTRL_ADDR_OUTPUT_R_BASE+4*i);
    return 0;
}
static int hw_fir(int sample,int clear,int *result) {
    Xil_Out32(FIR_BASE+XFIR_ACCEL_CTRL_ADDR_SAMPLE_DATA,(uint32_t)sample);
    Xil_Out32(FIR_BASE+XFIR_ACCEL_CTRL_ADDR_CLEAR_DATA,(unsigned)clear);
    Xil_Out32(FIR_BASE,1);
    if(wait_done(FIR_BASE))return 1;
    *result=(int32_t)Xil_In32(FIR_BASE+XFIR_ACCEL_CTRL_ADDR_RESULT_DATA);
    return 0;
}
static int test_dct(void) {
    short output[64],recovered[64];
    int errors=0;
    for(int t=0;t<DCT_TEST_COUNT;++t) {
        if(hw_dct(dct_inputs[t],output,0) || hw_dct(output,recovered,1)) return 1;
        for(int i=0;i<64;++i) {
            if(output[i]!=dct_expected[t][i] || recovered[i]!=idct_expected[t][i]) {
                if(errors<5) xil_printf("DCT mismatch block=%d index=%d\r\n",t,i);
                ++errors;
            }
        }
    }
    xil_printf("DCT/IDCT RESULT: %d blocks, %d values, %d failures\r\n",DCT_TEST_COUNT,2*64*DCT_TEST_COUNT,errors);
    return errors;
}
static int test_fir(void) {
    int history[128]={0},got,errors=0;
    unsigned state=48103;
    if(hw_fir(0,1,&got))return 1;
    for(int i=0;i<1024;++i) {
        if(i==512) {
            if(hw_fir(0,1,&got))return 1;
            for(int j=0;j<128;++j)history[j]=0;
        }
        state=1664525u*state+1013904223u;
        int sample=(int)(state>>24)-128,expected=0;
        for(int j=127;j>0;--j)history[j]=history[j-1];
        history[0]=sample;
        for(int j=0;j<128;++j)expected+=history[j]*fir_coeff[j];
        if(hw_fir(sample,0,&got))return 1;
        if(got!=expected)++errors;
    }
    xil_printf("FIR RESULT: 1024 samples, %d failures\r\n",errors);
    return errors;
}
static int test_add(void) {
    const uint32_t values[]={0,1,0xffffffffu,0x80000000u,0x7fffffffu,12345};
    int errors=0;
    for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j) {
        Xil_Out32(ADD_BASE+XADD_CTRL_ADDR_A_DATA,values[i]);
        Xil_Out32(ADD_BASE+XADD_CTRL_ADDR_B_DATA,values[j]);
        uint32_t result=Xil_In32(ADD_BASE+XADD_CTRL_ADDR_C_DATA);
        if(result!=values[i]+values[j])++errors;
    }
    xil_printf("ADD RESULT: 36 tests, %d failures\r\n",errors);
    return errors;
}
static void selftest(void) {
    int failures=test_add()+test_dct()+test_fir();
    xil_printf("LAB3 SELF-TEST: %s\r\n",failures?"FAIL":"PASS");
}
static void show_lena(void) {
    short transformed[64],recovered[64];
    if(hw_dct(dct_inputs[2],transformed,0) || hw_dct(transformed,recovered,1))return;
    xil_printf("Lena top-left block: input, DCT, recovered\r\n");
    for(int block=0;block<3;++block) {
        const short *p=block==0?dct_inputs[2]:block==1?transformed:recovered;
        for(int r=0;r<8;++r){for(int c=0;c<8;++c)xil_printf("%d ",p[8*r+c]);xil_printf("\r\n");}
        xil_printf("\r\n");
    }
}
static void fir_csv(void) {
    int out; unsigned state=48103;
    if(hw_fir(0,1,&out))return;
    xil_printf("FIR_CSV_BEGIN\r\nindex,input,output\r\n");
    for(int i=0;i<1024;++i) {
        state=1664525u*state+1013904223u;
        int sample=(int)(state>>24)-128;
        if(hw_fir(sample,0,&out))return;
        xil_printf("%d,%d,%d\r\n",i,sample,out);
    }
    xil_printf("FIR_CSV_END\r\n");
}
int main(void) {
    init_platform();
    xil_printf("\r\nECE4810J LAB3 | Arty Z7-20 | PL 100 MHz\r\n");
    xil_printf("DCT/IDCT 0x%08x, FIR 0x%08x, ADD 0x%08x\r\n",DCT_BASE,FIR_BASE,ADD_BASE);
    selftest();
    while(1) {
        xil_printf("\r\nMenu: t=self-test, d=Lena block, f=FIR CSV\r\n> ");
        char c=inbyte();
        xil_printf("%c\r\n",c);
        if(c=='t')selftest(); else if(c=='d')show_lena(); else if(c=='f')fir_csv();
    }
    cleanup_platform();
    return 0;
}
