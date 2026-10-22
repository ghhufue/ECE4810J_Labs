// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.1 (64-bit)
// Tool Version Limit: 2022.04
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
#ifndef XHLS_ALU_H
#define XHLS_ALU_H

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
#include "xhls_alu_hw.h"

/**************************** Type Definitions ******************************/
#ifdef __linux__
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#else
typedef struct {
    u16 DeviceId;
    u64 Ctrl_BaseAddress;
} XHls_alu_Config;
#endif

typedef struct {
    u64 Ctrl_BaseAddress;
    u32 IsReady;
} XHls_alu;

typedef u32 word_type;

/***************** Macros (Inline Functions) Definitions *********************/
#ifndef __linux__
#define XHls_alu_WriteReg(BaseAddress, RegOffset, Data) \
    Xil_Out32((BaseAddress) + (RegOffset), (u32)(Data))
#define XHls_alu_ReadReg(BaseAddress, RegOffset) \
    Xil_In32((BaseAddress) + (RegOffset))
#else
#define XHls_alu_WriteReg(BaseAddress, RegOffset, Data) \
    *(volatile u32*)((BaseAddress) + (RegOffset)) = (u32)(Data)
#define XHls_alu_ReadReg(BaseAddress, RegOffset) \
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
int XHls_alu_Initialize(XHls_alu *InstancePtr, u16 DeviceId);
XHls_alu_Config* XHls_alu_LookupConfig(u16 DeviceId);
int XHls_alu_CfgInitialize(XHls_alu *InstancePtr, XHls_alu_Config *ConfigPtr);
#else
int XHls_alu_Initialize(XHls_alu *InstancePtr, const char* InstanceName);
int XHls_alu_Release(XHls_alu *InstancePtr);
#endif

void XHls_alu_Start(XHls_alu *InstancePtr);
u32 XHls_alu_IsDone(XHls_alu *InstancePtr);
u32 XHls_alu_IsIdle(XHls_alu *InstancePtr);
u32 XHls_alu_IsReady(XHls_alu *InstancePtr);
void XHls_alu_EnableAutoRestart(XHls_alu *InstancePtr);
void XHls_alu_DisableAutoRestart(XHls_alu *InstancePtr);
u32 XHls_alu_Get_return(XHls_alu *InstancePtr);

void XHls_alu_Set_opa(XHls_alu *InstancePtr, u32 Data);
u32 XHls_alu_Get_opa(XHls_alu *InstancePtr);
void XHls_alu_Set_opb(XHls_alu *InstancePtr, u32 Data);
u32 XHls_alu_Get_opb(XHls_alu *InstancePtr);
void XHls_alu_Set_func(XHls_alu *InstancePtr, u32 Data);
u32 XHls_alu_Get_func(XHls_alu *InstancePtr);

void XHls_alu_InterruptGlobalEnable(XHls_alu *InstancePtr);
void XHls_alu_InterruptGlobalDisable(XHls_alu *InstancePtr);
void XHls_alu_InterruptEnable(XHls_alu *InstancePtr, u32 Mask);
void XHls_alu_InterruptDisable(XHls_alu *InstancePtr, u32 Mask);
void XHls_alu_InterruptClear(XHls_alu *InstancePtr, u32 Mask);
u32 XHls_alu_InterruptGetEnabled(XHls_alu *InstancePtr);
u32 XHls_alu_InterruptGetStatus(XHls_alu *InstancePtr);

#ifdef __cplusplus
}
#endif

#endif
