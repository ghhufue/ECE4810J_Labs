#ifndef LAB2_HLS_ALU_H
#define LAB2_HLS_ALU_H
#include <ap_int.h>
#include <stdint.h>
uint32_t hls_alu(uint32_t opa, uint32_t opb, ap_uint<5> func);
#endif
