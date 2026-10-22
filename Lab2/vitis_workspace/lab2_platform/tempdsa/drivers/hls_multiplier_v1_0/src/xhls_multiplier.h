// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.1 (64-bit)
// Tool Version Limit: 2022.04
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
#ifndef XHLS_MULTIPLIER_H
#define XHLS_MULTIPLIER_H

#ifdef __cplusplus
extern "C" {
#endif

/***************************** Include Files *********************************/
#ifndef __linux__
#include "xil_types.h"
#include "xil_assert.h"
#include "xstatus.h"
#include "xil_io.h"
#else
#include <stdint.h>
#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stddef.h>
#endif
#include "xhls_multiplier_hw.h"

/**************************** Type Definitions ******************************/
#ifdef __linux__
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#else
typedef struct {
    u16 DeviceId;
    u64 Crtls_BaseAddress;
} XHls_multiplier_Config;
#endif

typedef struct {
    u64 Crtls_BaseAddress;
    u32 IsReady;
} XHls_multiplier;

typedef u32 word_type;

/***************** Macros (Inline Functions) Definitions *********************/
#ifndef __linux__
#define XHls_multiplier_WriteReg(BaseAddress, RegOffset, Data) \
    Xil_Out32((BaseAddress) + (RegOffset), (u32)(Data))
#define XHls_multiplier_ReadReg(BaseAddress, RegOffset) \
    Xil_In32((BaseAddress) + (RegOffset))
#else
#define XHls_multiplier_WriteReg(BaseAddress, RegOffset, Data) \
    *(volatile u32*)((BaseAddress) + (RegOffset)) = (u32)(Data)
#define XHls_multiplier_ReadReg(BaseAddress, RegOffset) \
    *(volatile u32*)((BaseAddress) + (RegOffset))

#define Xil_AssertVoid(expr)    assert(expr)
#define Xil_AssertNonvoid(expr) assert(expr)

#define XST_SUCCESS             0
#define XST_DEVICE_NOT_FOUND    2
#define XST_OPEN_DEVICE_FAILED  3
#define XIL_COMPONENT_IS_READY  1
#endif

/************************** Function Prototypes *****************************/
#ifndef __linux__
int XHls_multiplier_Initialize(XHls_multiplier *InstancePtr, u16 DeviceId);
XHls_multiplier_Config* XHls_multiplier_LookupConfig(u16 DeviceId);
int XHls_multiplier_CfgInitialize(XHls_multiplier *InstancePtr, XHls_multiplier_Config *ConfigPtr);
#else
int XHls_multiplier_Initialize(XHls_multiplier *InstancePtr, const char* InstanceName);
int XHls_multiplier_Release(XHls_multiplier *InstancePtr);
#endif

void XHls_multiplier_Start(XHls_multiplier *InstancePtr);
u32 XHls_multiplier_IsDone(XHls_multiplier *InstancePtr);
u32 XHls_multiplier_IsIdle(XHls_multiplier *InstancePtr);
u32 XHls_multiplier_IsReady(XHls_multiplier *InstancePtr);
void XHls_multiplier_EnableAutoRestart(XHls_multiplier *InstancePtr);
void XHls_multiplier_DisableAutoRestart(XHls_multiplier *InstancePtr);
u32 XHls_multiplier_Get_return(XHls_multiplier *InstancePtr);

void XHls_multiplier_Set_a(XHls_multiplier *InstancePtr, u32 Data);
u32 XHls_multiplier_Get_a(XHls_multiplier *InstancePtr);
void XHls_multiplier_Set_b(XHls_multiplier *InstancePtr, u32 Data);
u32 XHls_multiplier_Get_b(XHls_multiplier *InstancePtr);

void XHls_multiplier_InterruptGlobalEnable(XHls_multiplier *InstancePtr);
void XHls_multiplier_InterruptGlobalDisable(XHls_multiplier *InstancePtr);
void XHls_multiplier_InterruptEnable(XHls_multiplier *InstancePtr, u32 Mask);
void XHls_multiplier_InterruptDisable(XHls_multiplier *InstancePtr, u32 Mask);
void XHls_multiplier_InterruptClear(XHls_multiplier *InstancePtr, u32 Mask);
u32 XHls_multiplier_InterruptGetEnabled(XHls_multiplier *InstancePtr);
u32 XHls_multiplier_InterruptGetStatus(XHls_multiplier *InstancePtr);

#ifdef __cplusplus
}
#endif

#endif
