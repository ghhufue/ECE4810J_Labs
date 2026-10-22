// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2022.1 (64-bit)
// Tool Version Limit: 2022.04
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// ==============================================================
#ifndef __linux__

#include "xstatus.h"
#include "xparameters.h"
#include "xhls_alu.h"

extern XHls_alu_Config XHls_alu_ConfigTable[];

XHls_alu_Config *XHls_alu_LookupConfig(u16 DeviceId) {
	XHls_alu_Config *ConfigPtr = NULL;

	int Index;

	for (Index = 0; Index < XPAR_XHLS_ALU_NUM_INSTANCES; Index++) {
		if (XHls_alu_ConfigTable[Index].DeviceId == DeviceId) {
			ConfigPtr = &XHls_alu_ConfigTable[Index];
			break;
		}
	}

	return ConfigPtr;
}

int XHls_alu_Initialize(XHls_alu *InstancePtr, u16 DeviceId) {
	XHls_alu_Config *ConfigPtr;

	Xil_AssertNonvoid(InstancePtr != NULL);

	ConfigPtr = XHls_alu_LookupConfig(DeviceId);
	if (ConfigPtr == NULL) {
		InstancePtr->IsReady = 0;
		return (XST_DEVICE_NOT_FOUND);
	}

	return XHls_alu_CfgInitialize(InstancePtr, ConfigPtr);
}

#endif

