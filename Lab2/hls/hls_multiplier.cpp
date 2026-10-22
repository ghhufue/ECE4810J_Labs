#include <stdint.h>
uint32_t hls_multiplier(uint16_t a, uint16_t b) {
#pragma HLS INTERFACE s_axilite port=return bundle=CRTLS
#pragma HLS INTERFACE s_axilite port=a bundle=CRTLS
#pragma HLS INTERFACE s_axilite port=b bundle=CRTLS
    // Cast before multiplication: 65535 * 65535 exceeds signed int.
    return (uint32_t)a * (uint32_t)b;
}
