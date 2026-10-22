#include "hls_alu.h"
#include "../tests/alu_vectors.h"
#include <stdio.h>
int main() {
    unsigned errors = 0;
    unsigned coverage[18] = {0};
    for (unsigned i = 0; i < ALU_VECTOR_COUNT; ++i) {
        const alu_vector &v = alu_vectors[i];
        uint32_t got = hls_alu(v.a, v.b, v.op);
        if (v.op < 18) ++coverage[v.op];
        if (got != v.expected) {
            if (++errors < 10)
                printf("FAIL op=%u a=%08x b=%08x expected=%08x got=%08x\n",
                       v.op, v.a, v.b, v.expected, got);
        }
    }
    for (unsigned op = 0; op < 18; ++op)
        printf("Operation %2u: %u tests\n", op, coverage[op]);
    printf("HLS_ALU_%s: %u tests, %u failures\n", errors ? "FAIL" : "PASS",
           (unsigned)ALU_VECTOR_COUNT, errors);
    return errors ? 1 : 0;
}
