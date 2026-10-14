#ifndef RTL_DIVIDER_H
#define RTL_DIVIDER_H
#include "xil_io.h"
#include "xstatus.h"
#define RTL_DIVIDER_S00_AXI_SLV_REG0_OFFSET 0
#define RTL_DIVIDER_S00_AXI_SLV_REG1_OFFSET 4
#define RTL_DIVIDER_S00_AXI_SLV_REG2_OFFSET 8
#define RTL_DIVIDER_S00_AXI_SLV_REG3_OFFSET 12
#define RTL_DIVIDER_BUSY 1U
#define RTL_DIVIDER_DONE 2U
#define RTL_DIVIDER_DIVIDE_BY_ZERO 4U
#define RTL_DIVIDER_mWriteReg(BaseAddress, RegOffset, Data) \
    Xil_Out32((BaseAddress) + (RegOffset), (u32)(Data))
#define RTL_DIVIDER_mReadReg(BaseAddress, RegOffset) \
    Xil_In32((BaseAddress) + (RegOffset))
XStatus RTL_DIVIDER_Reg_SelfTest(void *baseaddr_p);
#endif
