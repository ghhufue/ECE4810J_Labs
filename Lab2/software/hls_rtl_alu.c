#include "platform.h"
#include "xparameters.h"
#include "xil_io.h"
#include "xil_printf.h"
#include "xhls_alu.h"
#include "xhls_multiplier.h"
#include "alu_vectors.h"
#include <stdint.h>
#include <stdlib.h>
#include <errno.h>

#define RTL_MULT_BASE XPAR_RTL_MULTIPLIER_0_S00_AXI_BASEADDR
#define RTL_ALU_BASE XPAR_RTL_PIPE_ALU_0_S00_AXI_BASEADDR
#define HLS_TIMEOUT 1000000u
static XHls_alu hls_alu;
static XHls_multiplier hls_multiplier;
static const char *const names[18] = {
    "ADD","SUB","SLT","SLTU","AND","OR","XOR","SLL","SRL","SRA",
    "MUL","MULH","MULHSU","MULHU","DIV","DIVU","REM","REMU"
};

static int initialize_ip(void) {
    if (XHls_alu_Initialize(&hls_alu,XPAR_HLS_ALU_0_DEVICE_ID) != XST_SUCCESS ||
        XHls_multiplier_Initialize(&hls_multiplier,XPAR_HLS_MULTIPLIER_0_DEVICE_ID) != XST_SUCCESS) {
        xil_printf("ERROR: HLS IP initialization failed\r\n");
        return 0;
    }
    return 1;
}

static uint32_t rtl_compute(uint32_t a,uint32_t b,unsigned op) {
    Xil_Out32(RTL_ALU_BASE+0,a);
    Xil_Out32(RTL_ALU_BASE+4,b);
    Xil_Out32(RTL_ALU_BASE+8,op);
    // The AXI slave delays the result read until its pipeline completes.
    return Xil_In32(RTL_ALU_BASE+12);
}

static int hls_compute(uint32_t a,uint32_t b,unsigned op,uint32_t *result) {
    unsigned timeout=HLS_TIMEOUT;
    XHls_alu_Set_opa(&hls_alu,a);
    XHls_alu_Set_opb(&hls_alu,b);
    XHls_alu_Set_func(&hls_alu,op);
    XHls_alu_Start(&hls_alu);
    while (!XHls_alu_IsDone(&hls_alu)) {
        if (--timeout == 0) { xil_printf("ERROR: HLS ALU timeout\r\n"); return 0; }
    }
    *result=XHls_alu_Get_return(&hls_alu);
    return 1;
}

static int multiplier_compute(uint32_t a,uint32_t b,uint32_t *rtl,uint32_t *hls) {
    unsigned timeout=HLS_TIMEOUT;
    Xil_Out32(RTL_MULT_BASE,(a<<16)|b);
    *rtl=Xil_In32(RTL_MULT_BASE+4);
    XHls_multiplier_Set_a(&hls_multiplier,a);
    XHls_multiplier_Set_b(&hls_multiplier,b);
    XHls_multiplier_Start(&hls_multiplier);
    while (!XHls_multiplier_IsDone(&hls_multiplier)) {
        if (--timeout == 0) { xil_printf("ERROR: HLS multiplier timeout\r\n"); return 0; }
    }
    *hls=XHls_multiplier_Get_return(&hls_multiplier);
    return 1;
}

static void self_test(void) {
    unsigned rtl_errors=0,hls_errors=0,mul_errors=0,op_errors[18]={0},op_count[18]={0};
    const uint32_t edge[]={0,1,2,3,255,256,32767,32768,65534,65535};
    xil_printf("\r\n--- Multiplier self-test ---\r\n");
    for (unsigned i=0;i<100;++i) {
        uint32_t a=edge[i/10],b=edge[i%10],r=0,h=0,expected=a*b;
        int ok=multiplier_compute(a,b,&r,&h);
        if (!ok || r!=expected || h!=expected) {
            ++mul_errors;
            xil_printf("FAIL MUL16 a=%d b=%d RTL=%08x HLS=%08x expected=%08x\r\n",a,b,r,h,expected);
            if (!ok) break;
        }
    }
    xil_printf("MULTIPLIER RESULT: 100 tests, %d failures\r\n",mul_errors);
    xil_printf("\r\n--- RV32IM ALU self-test (independent reference vectors) ---\r\n");
    for (unsigned i=0;i<ALU_VECTOR_COUNT;++i) {
        const struct alu_vector *v=&alu_vectors[i];
        uint32_t r=rtl_compute(v->a,v->b,v->op),h=0;
        int ok=hls_compute(v->a,v->b,v->op,&h);
        if (r!=v->expected) ++rtl_errors;
        if (!ok || h!=v->expected) ++hls_errors;
        if (v->op<18) {
            ++op_count[v->op];
            if (!ok || r!=v->expected || h!=v->expected) ++op_errors[v->op];
        }
        if ((!ok || r!=v->expected || h!=v->expected) && rtl_errors+hls_errors<=10)
            xil_printf("FAIL op=%d a=%08x b=%08x RTL=%08x HLS=%08x expected=%08x\r\n",
                       v->op,v->a,v->b,r,h,v->expected);
        if (!ok) { xil_printf("ALU TEST ABORTED\r\n"); return; }
    }
    for (unsigned op=0;op<18;++op)
        xil_printf("op %d %s: %d tests, %d failures (RTL + HLS)\r\n",op,names[op],op_count[op],op_errors[op]);
    xil_printf("RTL ALU RESULT: %d tests, %d failures\r\n",(unsigned)ALU_VECTOR_COUNT,rtl_errors);
    xil_printf("HLS ALU RESULT: %d tests, %d failures\r\n",(unsigned)ALU_VECTOR_COUNT,hls_errors);
    xil_printf("LAB2 SELF-TEST: %s\r\n",(rtl_errors||hls_errors||mul_errors)?"FAIL":"PASS");
}

static int read_line(char *buf,unsigned capacity) {
    unsigned n=0;
    int overflow=0;
    for (;;) {
        char c=inbyte();
        if (c=='\r' || c=='\n') {
            if (n==0 && !overflow) continue; // Also skips CRLF's second byte.
            xil_printf("\r\n"); buf[n]=0; return !overflow;
        }
        if (c=='\b' || c==127) {
            if (n) { --n; xil_printf("\b \b"); }
        } else if (c>=32 && c<=126) {
            if (n+1<capacity) { buf[n++]=c; outbyte(c); }
            else overflow=1;
        }
    }
}

static int operand(const char *prompt,uint32_t *value,int narrow) {
    char line[48],*end;
    long long parsed;
    xil_printf("%s",prompt);
    if (!read_line(line,sizeof(line))) { xil_printf("Input too long\r\n"); return 0; }
    errno=0;
    // Base 0 accepts decimal and 0x-prefixed hexadecimal.
    parsed=strtoll(line,&end,0);
    while (*end==' ' || *end=='\t') ++end;
    if (end==line || *end || errno==ERANGE || parsed < (narrow?0:-2147483648LL) ||
        parsed > (narrow?65535LL:4294967295LL)) {
        xil_printf("Invalid operand (allowed: %s)\r\n",narrow?"0..65535":"-2147483648..4294967295");
        return 0;
    }
    *value=(uint32_t)parsed;
    return 1;
}

int main(void) {
    char command[16];
    init_platform();
    xil_printf("\r\nECE4810J Lab 2 | Arty Z7-20 | 100 MHz PL\r\n");
    xil_printf("RTL/HLS multipliers + RTL pipelined/HLS RV32IM ALUs\r\n");
    xil_printf("UART: 115200 8N1; SD boot image\r\n");
    if (!initialize_ip()) { cleanup_platform(); return 1; }
    self_test();
    for (;;) {
        uint32_t a,b,op,r=0,h=0;
        xil_printf("\r\nMenu: t = self-test, m = 16-bit multiply, a = 32-bit ALU\r\n> ");
        if (!read_line(command,sizeof(command))) continue;
        if (command[1]!=0) { xil_printf("Enter t, m, or a\r\n"); continue; }
        if (command[0]=='t') self_test();
        else if (command[0]=='m') {
            if (!operand("Enter operand A (0..65535): ",&a,1) ||
                !operand("Enter operand B (0..65535): ",&b,1)) continue;
            if (multiplier_compute(a,b,&r,&h))
                xil_printf("%d * %d: RTL=0x%08x HLS=0x%08x expected=0x%08x %s\r\n",
                           a,b,r,h,a*b,(r==a*b && h==a*b)?"PASS":"FAIL");
        } else if (command[0]=='a') {
            for (unsigned i=0;i<18;++i) xil_printf("%d=%s ",i,names[i]);
            xil_printf("\r\n");
            if (!operand("Operation (0..17): ",&op,1) || op>17 ||
                !operand("Operand A (decimal or 0xhex): ",&a,0) ||
                !operand("Operand B (decimal or 0xhex): ",&b,0)) continue;
            r=rtl_compute(a,b,op);
            if (hls_compute(a,b,op,&h))
                xil_printf("%s A=0x%08x B=0x%08x RTL=0x%08x HLS=0x%08x %s\r\n",
                           names[op],a,b,r,h,r==h?"MATCH":"MISMATCH");
        } else xil_printf("Enter t, m, or a\r\n");
    }
}
