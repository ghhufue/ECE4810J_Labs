"""Independent Python integer oracle, shared only as data by RTL/HLS/ARM tests."""
from pathlib import Path
import random

LAB = Path(__file__).resolve().parents[1]
MASK = (1 << 32) - 1

def signed(x):
    return x if x < 1 << 31 else x - (1 << 32)

def reference(a, b, op):
    sa, sb, sh = signed(a), signed(b), b & 31
    if op == 0: value = a + b
    elif op == 1: value = a - b
    elif op == 2: value = int(sa < sb)
    elif op == 3: value = int(a < b)
    elif op == 4: value = a & b
    elif op == 5: value = a | b
    elif op == 6: value = a ^ b
    elif op == 7: value = a << sh
    elif op == 8: value = a >> sh
    elif op == 9: value = sa >> sh
    elif op == 10: value = a * b
    elif op == 11: value = (sa * sb) >> 32
    elif op == 12: value = (sa * b) >> 32
    elif op == 13: value = (a * b) >> 32
    elif op in (14, 16):
        if b == 0: return MASK if op == 14 else a
        q = abs(sa) // abs(sb)
        if (sa < 0) != (sb < 0): q = -q
        value = q if op == 14 else sa - q * sb
    elif op == 15: value = a // b if b else MASK
    elif op == 17: value = a % b if b else a
    else: value = 0
    return value & MASK

def main():
    edge = [0, 1, 2, 3, 5, 7, 31, 32, 33, 63, 0x7fffffff,
            0x80000000, 0x80000001, 0xfffffffe, 0xffffffff, 0x55555555, 0xaaaaaaaa]
    pairs = [(a, b) for a in edge for b in edge]
    rng = random.Random(48102)
    pairs += [(rng.getrandbits(32), rng.getrandbits(32)) for _ in range(128)]
    rows = [(a,b,op,reference(a,b,op)) for a,b in pairs for op in range(18)]
    rows += [(0xffffffff,0x80000000,op,0) for op in (18,19,31)]
    out = LAB / 'tests'
    out.mkdir(exist_ok=True)
    (out/'alu_vectors.hex').write_text(''.join(f'{op:08x}{a:08x}{b:08x}{r:08x}\n' for a,b,op,r in rows))
    header = '#ifndef LAB2_ALU_VECTORS_H\n#define LAB2_ALU_VECTORS_H\n#include <stdint.h>\n'
    header += 'struct alu_vector { uint32_t a, b, op, expected; };\n'
    header += 'static const struct alu_vector alu_vectors[] = {\n'
    header += ''.join(f'    {{0x{a:08x}u,0x{b:08x}u,{op}u,0x{r:08x}u}},\n' for a,b,op,r in rows)
    header += '};\n#define ALU_VECTOR_COUNT (sizeof(alu_vectors)/sizeof(alu_vectors[0]))\n#endif\n'
    (out/'alu_vectors.h').write_text(header)
    print(f'Generated {len(rows)} vectors; {len(pairs)} operand pairs for all 18 operations plus invalid selectors.')

if __name__ == '__main__': main()
