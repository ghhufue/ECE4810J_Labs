// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.1 (64-bit)
// Tool Version Limit: 2022.04
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
/***************************** Include Files *********************************/
#include "xhls_multiplier.h"

/************************** Function Implementation *************************/
#ifndef __linux__
int XHls_multiplier_CfgInitialize(XHls_multiplier *InstancePtr, XHls_multiplier_Config *ConfigPtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(ConfigPtr != NULL);

    InstancePtr->Crtls_BaseAddress = ConfigPtr->Crtls_BaseAddress;
    InstancePtr->IsReady = XIL_COMPONENT_IS_READY;

    return XST_SUCCESS;
}
#endif

void XHls_multiplier_Start(XHls_multiplier *InstancePtr) {
    u32 Data;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_AP_CTRL) & 0x80;
    XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_AP_CTRL, Data | 0x01);
}

u32 XHls_multiplier_IsDone(XHls_multiplier *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_AP_CTRL);
    return (Data >> 1) & 0x1;
}

u32 XHls_multiplier_IsIdle(XHls_multiplier *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_AP_CTRL);
    return (Data >> 2) & 0x1;
}

u32 XHls_multiplier_IsReady(XHls_multiplier *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_AP_CTRL);
    // check ap_start to see if the pcore is ready for next input
    return !(Data & 0x1);
}

void XHls_multiplier_EnableAutoRestart(XHls_multiplier *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_AP_CTRL, 0x80);
}

void XHls_multiplier_DisableAutoRestart(XHls_multiplier *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_AP_CTRL, 0);
}

u32 XHls_multiplier_Get_return(XHls_multiplier *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_AP_RETURN);
    return Data;
}
void XHls_multiplier_Set_a(XHls_multiplier *InstancePtr, u32 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_A_DATA, Data);
}

u32 XHls_multiplier_Get_a(XHls_multiplier *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_A_DATA);
    return Data;
}

void XHls_multiplier_Set_b(XHls_multiplier *InstancePtr, u32 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_B_DATA, Data);
}

u32 XHls_multiplier_Get_b(XHls_multiplier *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_B_DATA);
    return Data;
}

void XHls_multiplier_InterruptGlobalEnable(XHls_multiplier *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_GIE, 1);
}

void XHls_multiplier_InterruptGlobalDisable(XHls_multiplier *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_GIE, 0);
}

void XHls_multiplier_InterruptEnable(XHls_multiplier *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_IER);
    XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_IER, Register | Mask);
}

void XHls_multiplier_InterruptDisable(XHls_multiplier *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_IER);
    XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_IER, Register & (~Mask));
}

void XHls_multiplier_InterruptClear(XHls_multiplier *InstancePtr, u32 Mask) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    //XHls_multiplier_WriteReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_ISR, Mask);
}

u32 XHls_multiplier_InterruptGetEnabled(XHls_multiplier *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_IER);
}

u32 XHls_multiplier_InterruptGetStatus(XHls_multiplier *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    // Current Interrupt Clear Behavior is Clear on Read(COR).
    return XHls_multiplier_ReadReg(InstancePtr->Crtls_BaseAddress, XHLS_MULTIPLIER_CRTLS_ADDR_ISR);
}

