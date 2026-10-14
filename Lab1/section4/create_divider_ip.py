"""Reuse the existing packaged AXI port metadata under a new IP identity."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / 'vivado/ip_repo/rtl_multiplier_1.0'
target = root / 'vivado/ip_repo/rtl_divider_1.0'
for rel in ['component.xml', 'hdl/rtl_multiplier_v1_0.v',
            'xgui/rtl_multiplier_v1_0.tcl',
            'bd/bd.tcl',
            'drivers/rtl_multiplier_v1_0/src/Makefile',
            'drivers/rtl_multiplier_v1_0/data/rtl_multiplier.mdd',
            'drivers/rtl_multiplier_v1_0/data/rtl_multiplier.tcl']:
    dst = target / rel.replace('multiplier', 'divider')
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text((source / rel).read_text().replace('multiplier', 'divider')
                   .replace('Multiplier', 'Divider'), encoding='utf-8')
# Keep the exact packaged port declarations; replace all implementation logic.
header = (source / 'hdl/rtl_multiplier_v1_0_S00_AXI.v').read_text().split('// AXI4LITE signals')[0]
dst = target / 'hdl/rtl_divider_v1_0_S00_AXI.v'
dst.write_text(header.replace('multiplier', 'divider') +
               (root / 'section4/axi_divider_body.vh').read_text(), encoding='utf-8')
