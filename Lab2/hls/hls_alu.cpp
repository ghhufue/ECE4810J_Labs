#include "hls_alu.h"

// RV32IM results are bit patterns. Unsigned arithmetic avoids C++ signed
// overflow and implementation-defined signed right shifts.
uint32_t hls_alu(uint32_t opa, uint32_t opb, ap_uint<5> func) {
#pragma HLS INTERFACE s_axilite port=return bundle=CTRL
#pragma HLS INTERFACE s_axilite port=opa bundle=CTRL
#pragma HLS INTERFACE s_axilite port=opb bundle=CTRL
#pragma HLS INTERFACE s_axilite port=func bundle=CTRL
    const unsigned op = func;
    const unsigned sh = opb & 31u;
    const uint64_t product = (uint64_t)opa * (uint64_t)opb;
    const uint32_t high = (uint32_t)(product >> 32);
    // Share unsigned division hardware between signed/unsigned DIV and REM.
    const bool signed_op = op == 14 || op == 16;
    const bool neg_a = signed_op && (opa >> 31);
    const bool neg_b = signed_op && (opb >> 31);
    const uint32_t a = neg_a ? 0u - opa : opa;
    const uint32_t b = neg_b ? 0u - opb : opb;
    uint32_t q = 0, r = opa;
    if (op >= 14 && op <= 17) {
        if (b == 0) {
            q = UINT32_MAX;
        } else {
            q = a / b;
            r = a % b;
            if (neg_a != neg_b) q = 0u - q;
            if (neg_a) r = 0u - r;
        }
    }
    switch (op) {
    case 0: return opa + opb;
    case 1: return opa - opb;
    case 2: return (opa ^ 0x80000000u) < (opb ^ 0x80000000u);
    case 3: return opa < opb;
    case 4: return opa & opb;
    case 5: return opa | opb;
    case 6: return opa ^ opb;
    case 7: return opa << sh;
    case 8: return opa >> sh;
    case 9: return (opa >> sh) |
                   ((sh && (opa >> 31)) ? (UINT32_MAX << (32 - sh)) : 0u);
    case 10: return (uint32_t)product;
    case 11: return high - ((opa >> 31) ? opb : 0u) - ((opb >> 31) ? opa : 0u);
    case 12: return high - ((opa >> 31) ? opb : 0u);
    case 13: return high;
    case 14: case 15: return q;
    case 16: case 17: return r;
    default: return 0;
    }
}
