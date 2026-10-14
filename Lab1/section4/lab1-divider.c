#include "platform.h"
#include "xparameters.h"
#include "rtl_divider.h"
#include "xil_printf.h"

#define DIV_BASE XPAR_RTL_DIVIDER_0_S00_AXI_BASEADDR
static int test(unsigned a, unsigned b) {
    unsigned status = 0, q, r, polls;
    unsigned expected_q = b ? a / b : 65535U;
    unsigned expected_r = b ? a % b : a;
    RTL_DIVIDER_mWriteReg(DIV_BASE, 0, (a << 16) | b);
    for (polls = 0; polls < 100000U; ++polls) {
        status = RTL_DIVIDER_mReadReg(DIV_BASE, 12);
        if ((status & (RTL_DIVIDER_BUSY | RTL_DIVIDER_DONE)) == RTL_DIVIDER_DONE)
            break;
    }
    if (polls == 100000U) {
        xil_printf("FAIL: timeout for %u / %u\r\n", a, b);
        return 1;
    }
    q = RTL_DIVIDER_mReadReg(DIV_BASE, 4);
    r = RTL_DIVIDER_mReadReg(DIV_BASE, 8);
    if (q != expected_q || r != expected_r ||
        status != (b ? RTL_DIVIDER_DONE : (RTL_DIVIDER_DONE | RTL_DIVIDER_DIVIDE_BY_ZERO))) {
        xil_printf("FAIL: %u / %u -> div=%u mod=%u status=0x%x\r\n", a, b, q, r, status);
        return 1;
    }
    xil_printf("PASS: %u / %u -> div=%u mod=%u status=0x%x\r\n", a, b, q, r, status);
    return 0;
}
int main(void) {
    static const unsigned cases[][2] = {
        {17, 5}, {100, 7}, {65535, 255}, {65535, 1}, {65535, 65535},
        {3, 7}, {0, 7}, {32768, 3}, {12345, 0}, {0, 0}, {42, 6}
    };
    unsigned i, failures = 0;
    init_platform();
    xil_printf("\r\n=== Section 4 RTL_DIVIDER: unsigned 16-bit AXI-Lite ===\r\n");
    xil_printf("Base address: 0x%08x\r\n", (unsigned)DIV_BASE);
    for (i = 0; i < sizeof(cases) / sizeof(cases[0]); ++i)
        failures += test(cases[i][0], cases[i][1]);
    xil_printf("RESULT: %u tests, %u failures\r\n", i, failures);
    xil_printf("End of test\r\n");
    cleanup_platform();
    return failures ? 1 : 0;
}
