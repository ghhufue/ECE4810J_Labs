"""Check the Zynq boot header, partition checksums, bounds and image order."""
from pathlib import Path
import hashlib
import struct

lab = Path(__file__).resolve().parents[1]
path = lab / 'boot/section4-divider-BOOT.bin'
data = path.read_bytes()
def word(offset):
    return struct.unpack_from('<I', data, offset)[0]

assert word(0x20) == 0xaa995566, 'Invalid width detection word'
assert word(0x24) == 0x584c4e58, 'Invalid Zynq image identifier'
assert sum(struct.unpack_from('<11I', data, 0x20)) & 0xffffffff == 0xffffffff, 'Boot header checksum'
iht = word(0x98)
assert word(iht + 4) == 3, 'Expected FSBL, bitstream, application'
pht = word(iht + 8) * 4
assert pht == word(0x9c), 'Partition table offset mismatch'
expected = [('FSBL', 0x10, 0), ('PL bitstream', 0x20, 0), ('Divider application', 0x10, 0x100000)]
lines = ['Zynq boot image header and partition verification: PASS']
last_end = 0
for i, (name, attribute, load) in enumerate(expected):
    header = struct.unpack_from('<16I', data, pht + 64*i)
    assert sum(header) & 0xffffffff == 0xffffffff, f'{name}: partition checksum'
    assert header[6] == attribute, f'{name}: unexpected destination attribute'
    assert header[3] == load, f'{name}: unexpected load address'
    begin, length = header[5] * 4, header[2] * 4
    assert length > 0 and begin >= last_end and begin + length <= len(data), f'{name}: partition bounds'
    last_end = begin + length
    lines.append(f'{i+1}. {name}: offset=0x{begin:x}, length={length}, load=0x{load:x}, checksum PASS')
lines += [f'Image bytes: {len(data)}', f'SHA256: {hashlib.sha256(data).hexdigest()}',
          'Hardware execution: pending (board unavailable)']
report = '\n'.join(lines) + '\n'
report_logs = lab / 'report/logs'
report_logs.mkdir(parents=True, exist_ok=True)
(report_logs / 'section4_divider_boot_validation.txt').write_text(report, encoding='utf-8')
print(report, end='')
