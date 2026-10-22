#include <stdint.h>
#include <stdio.h>
uint32_t hls_multiplier(uint16_t a, uint16_t b);
int main() {
    const uint16_t edge[] = {0,1,2,3,255,256,32767,32768,65534,65535};
    unsigned errors=0, count=0;
    uint32_t seed=48102;
    for (unsigned i=0; i<356; ++i) {
        uint16_t a,b;
        if (i<100) { a=edge[i/10]; b=edge[i%10]; }
        else {
            seed=1664525u*seed+1013904223u; a=seed>>16;
            seed=1664525u*seed+1013904223u; b=seed>>16;
        }
        uint32_t p=hls_multiplier(a,b);
        uint32_t expected=(uint32_t)((uint64_t)a*b);
        ++count;
        if (p != expected) { ++errors; printf("FAIL %u * %u = %u\n",a,b,p); }
    }
    printf("HLS_MULTIPLIER_%s: %u tests, %u failures\n",errors?"FAIL":"PASS",count,errors);
    return errors?1:0;
}
