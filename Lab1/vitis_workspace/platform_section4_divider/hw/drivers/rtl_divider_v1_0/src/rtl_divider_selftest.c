#include "rtl_divider.h"
// Must be called only when the divider is idle; bounded polling prevents a hang.
XStatus RTL_DIVIDER_Reg_SelfTest(void *baseaddr_p) {
    UINTPTR base = (UINTPTR)baseaddr_p;
    unsigned count;
    if (RTL_DIVIDER_mReadReg(base, 12) & RTL_DIVIDER_BUSY) return XST_FAILURE;
    RTL_DIVIDER_mWriteReg(base, 0, (17U << 16) | 5U);
    for (count = 0; count < 100000U; ++count) {
        u32 status = RTL_DIVIDER_mReadReg(base, 12);
        if ((status & 3U) == RTL_DIVIDER_DONE)
            return (status == RTL_DIVIDER_DONE &&
                    RTL_DIVIDER_mReadReg(base, 4) == 3U &&
                    RTL_DIVIDER_mReadReg(base, 8) == 2U) ? XST_SUCCESS : XST_FAILURE;
    }
    return XST_FAILURE;
}
