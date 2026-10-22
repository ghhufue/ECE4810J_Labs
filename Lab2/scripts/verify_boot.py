"""Validate Zynq boot structure and checksums, and record exact build inputs."""
from pathlib import Path
import hashlib
import json
import struct

lab=Path(__file__).resolve().parents[1]
path=lab/'boot/BOOT.BIN'
data=path.read_bytes()
def word(offset): return struct.unpack_from('<I',data,offset)[0]
assert word(0x20)==0xaa995566,'Invalid width detection word'
assert word(0x24)==0x584c4e58,'Invalid Zynq image identifier'
assert sum(struct.unpack_from('<11I',data,0x20)) & 0xffffffff == 0xffffffff,'Boot header checksum'
iht=word(0x98)
assert word(iht+4)==3,'Expected FSBL, bitstream, application'
pht=word(iht+8)*4
assert pht==word(0x9c),'Partition table offset mismatch'
expected=[('FSBL',0x10,0),('PL bitstream',0x20,0),('Lab 2 application',0x10,0x100000)]
lines=['Zynq boot image structure validation: PASS']
partitions=[]
last_end=0
for i,(name,attribute,load) in enumerate(expected):
    header=struct.unpack_from('<16I',data,pht+64*i)
    assert sum(header) & 0xffffffff == 0xffffffff,f'{name}: partition header checksum'
    assert header[6]==attribute,f'{name}: unexpected destination'
    assert header[3]==load,f'{name}: unexpected load address'
    begin,length=header[5]*4,header[2]*4
    assert length>0 and begin>=last_end and begin+length<=len(data),f'{name}: bounds'
    last_end=begin+length
    partitions.append((begin,length,load))
    lines.append(f'{i+1}. {name}: offset=0x{begin:x}, bytes={length}, load=0x{load:x}, header checksum PASS')
elfs=[(0,lab/'vitis_workspace/lab2_platform/export/lab2_platform/sw/lab2_platform/boot/fsbl.elf'),
      (2,lab/'vitis_workspace/hello_hls_rtl_alu/Debug/hello_hls_rtl_alu.elf')]
for index,elf_path in elfs:
    elf=elf_path.read_bytes()
    assert elf[:7]==b'\x7fELF\x01\x01\x01','Expected ELF32 little endian'
    assert struct.unpack_from('<H',elf,18)[0]==40,'Expected ARM ELF'
    phoff=struct.unpack_from('<I',elf,28)[0]
    phsize,phcount=struct.unpack_from('<HH',elf,42)
    begin,length,load=partitions[index]
    for j in range(phcount):
        kind,offset,virtual,physical,filesz,memsz,flags,align=struct.unpack_from('<8I',elf,phoff+j*phsize)
        if kind==1 and filesz:
            target=begin+physical-load
            assert physical>=load and target+filesz<=begin+length,'ELF segment bounds'
            assert data[target:target+filesz]==elf[offset:offset+filesz],f'{elf_path.name}: payload mismatch'
    entry=struct.unpack_from('<I',elf,24)[0]
    assert entry==load,'Unexpected executable entry point'
    lines.append(f'{elf_path.name}: ARM ELF load segments match image bytes, entry=0x{entry:x} PASS')
bit_path=lab/'vivado/lab2/lab2.runs/impl_1/Zynq_CPU_wrapper.bit'
bit=bit_path.read_bytes()
pos=2+struct.unpack_from('>H',bit,0)[0]
assert struct.unpack_from('>H',bit,pos)[0]==1,'Invalid bitstream header'
pos+=2
while bit[pos]!=ord('e'):
    field_size=struct.unpack_from('>H',bit,pos+1)[0]
    pos+=3+field_size
bit_size=struct.unpack_from('>I',bit,pos+1)[0]
payload=bit[pos+5:pos+5+bit_size]
assert len(payload)==bit_size and bit_size%4==0,'Invalid bitstream length'
swapped=b''.join(payload[i:i+4][::-1] for i in range(0,len(payload),4))
begin,length,load=partitions[1]
assert data[begin:begin+bit_size]==swapped,'PL partition differs from generated bitstream'
# Bootgen pads the configuration data to an even number of words with NOOPs.
padding=data[begin+bit_size:begin+length]
assert length>=bit_size and len(padding)<=4 and padding in (b'',b'\x00\x00\x00\x20'),'Unexpected PL padding'
import zipfile
with zipfile.ZipFile(lab/'exported/lab2.xsa') as xsa:
    embedded=[name for name in xsa.namelist() if name.endswith('.bit')]
    assert len(embedded)==1 and xsa.read(embedded[0])==bit,'XSA bitstream differs'
lines.append('PL partition matches generated bitstream (32-bit byte swap); XSA contains identical bitstream PASS')
sha=hashlib.sha256(data).hexdigest()
(lab/'boot/BOOT.sha256').write_text(f'{sha}  BOOT.BIN\n')
inputs=['vitis_workspace/lab2_platform/export/lab2_platform/sw/lab2_platform/boot/fsbl.elf',
        'vivado/lab2/lab2.runs/impl_1/Zynq_CPU_wrapper.bit',
        'vitis_workspace/hello_hls_rtl_alu/Debug/hello_hls_rtl_alu.elf','exported/lab2.xsa']
manifest={'board':'Arty Z7-20','part':'xc7z020clg400-1','tools':'Vivado/Vitis 2022.1',
          'image':{'path':'boot/BOOT.BIN','bytes':len(data),'sha256':sha},
          'inputs':{f:hashlib.sha256((lab/f).read_bytes()).hexdigest() for f in inputs},
          'hardware_execution':'Pending; board unavailable'}
(lab/'boot/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
lines.extend([f'Image bytes: {len(data)}',f'SHA256: {sha}','Hardware execution: pending (board unavailable)'])
report='\n'.join(lines)+'\n'
(lab/'logs/boot_validation.txt').write_text(report)
print(report,end='')
