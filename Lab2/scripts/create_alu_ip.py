"""Reuse the Lab 1 AXI interface metadata with a new identity and implementation."""
from pathlib import Path
import xml.etree.ElementTree as ET

lab = Path(__file__).resolve().parents[1]
source = lab.parent / 'Lab1/vivado/ip_repo/rtl_multiplier_1.0'
target = lab / 'ip_repo/rtl_pipe_alu_1.0'
for rel in ['component.xml', 'hdl/rtl_multiplier_v1_0.v',
            'xgui/rtl_multiplier_v1_0.tcl', 'bd/bd.tcl',
            'drivers/rtl_multiplier_v1_0/src/Makefile',
            'drivers/rtl_multiplier_v1_0/src/rtl_multiplier.h',
            'drivers/rtl_multiplier_v1_0/src/rtl_multiplier.c',
            'drivers/rtl_multiplier_v1_0/src/rtl_multiplier_selftest.c',
            'drivers/rtl_multiplier_v1_0/data/rtl_multiplier.mdd',
            'drivers/rtl_multiplier_v1_0/data/rtl_multiplier.tcl']:
    dst = target / rel.replace('rtl_multiplier', 'rtl_pipe_alu')
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text((source / rel).read_text().replace('rtl_multiplier','rtl_pipe_alu'),encoding='utf-8')
header = (source/'hdl/rtl_multiplier_v1_0_S00_AXI.v').read_text().split('// AXI4LITE signals')[0]
(target/'hdl/rtl_pipe_alu_v1_0_S00_AXI.v').write_text(
    header.replace('rtl_multiplier','rtl_pipe_alu')+(lab/'rtl/axi_alu_body.vh').read_text())
(target/'src').mkdir(exist_ok=True)
(target/'src/rtl_pipe_alu.sv').write_text((lab/'rtl/rtl_pipe_alu.sv').read_text())
ns='http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'
ET.register_namespace('spirit',ns)
ET.register_namespace('xilinx','http://www.xilinx.com')
ET.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance')
tree=ET.parse(target/'component.xml')
for file in tree.findall(f'.//{{{ns}}}file'):
    name=file.find(f'{{{ns}}}name')
    if name is not None and name.text=='src/rtl_pipe_alu.v':
        name.text='src/rtl_pipe_alu.sv'
        file.find(f'{{{ns}}}fileType').text='systemVerilogSource'
    for entry in list(file):
        if entry.tag==f'{{{ns}}}userFileType' and (entry.text or '').startswith('CHECKSUM_'):
            file.remove(entry)
tree.write(target/'component.xml',encoding='utf-8',xml_declaration=True)
print(f'Packaged {target}')
