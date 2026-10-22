// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.1 (64-bit)
// Tool Version Limit: 2022.04
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
/***************************** Include Files *********************************/
#include "xhls_alu.h"

/************************** Function Implementation *************************/
#ifndef __linux__
int XHls_alu_CfgInitialize(XHls_alu *InstancePtr, XHls_alu_Config *ConfigPtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(ConfigPtr != NULL);

    InstancePtr->Ctrl_BaseAddress = ConfigPtr->Ctrl_BaseAddress;
    InstancePtr->IsReady = XIL_COMPONENT_IS_READY;

    return XST_SUCCESS;
}
#endif

void XHls_alu_Start(XHls_alu *InstancePtr) {
    u32 Data;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_AP_CTRL) & 0x80;
    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_AP_CTRL, Data | 0x01);
}

u32 XHls_alu_IsDone(XHls_alu *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_AP_CTRL);
    return (Data >> 1) & 0x1;
}

u32 XHls_alu_IsIdle(XHls_alu *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_AP_CTRL);
    return (Data >> 2) & 0x1;
}

u32 XHls_alu_IsReady(XHls_alu *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_AP_CTRL);
    // check ap_start to see if the pcore is ready for next input
    return !(Data & 0x1);
}

void XHls_alu_EnableAutoRestart(XHls_alu *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_AP_CTRL, 0x80);
}

void XHls_alu_DisableAutoRestart(XHls_alu *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_AP_CTRL, 0);
}

u32 XHls_alu_Get_return(XHls_alu *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_AP_RETURN);
    return Data;
}
void XHls_alu_Set_opa(XHls_alu *InstancePtr, u32 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_OPA_DATA, Data);
}

u32 XHls_alu_Get_opa(XHls_alu *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_OPA_DATA);
    return Data;
}

void XHls_alu_Set_opb(XHls_alu *InstancePtr, u32 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_OPB_DATA, Data);
}

u32 XHls_alu_Get_opb(XHls_alu *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_OPB_DATA);
    return Data;
}

void XHls_alu_Set_func(XHls_alu *InstancePtr, u32 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_FUNC_DATA, Data);
}

u32 XHls_alu_Get_func(XHls_alu *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_FUNC_DATA);
    return Data;
}

void XHls_alu_InterruptGlobalEnable(XHls_alu *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_GIE, 1);
}

void XHls_alu_InterruptGlobalDisable(XHls_alu *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_GIE, 0);
}

void XHls_alu_InterruptEnable(XHls_alu *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_IER);
    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_IER, Register | Mask);
}

void XHls_alu_InterruptDisable(XHls_alu *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_IER);
    XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_IER, Register & (~Mask));
}

void XHls_alu_InterruptClear(XHls_alu *InstancePtr, u32 Mask) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    //XHls_alu_WriteReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_ISR, Mask);
}

u32 XHls_alu_InterruptGetEnabled(XHls_alu *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_IER);
}

u32 XHls_alu_InterruptGetStatus(XHls_alu *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    // Current Interrupt Clear Behavior is Clear on Read(COR).
    return XHls_alu_ReadReg(InstancePtr->Ctrl_BaseAddress, XHLS_ALU_CTRL_ADDR_ISR);
}

