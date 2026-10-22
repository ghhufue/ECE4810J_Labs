"""Complete interrupted Vitis application metadata using Lab 1's working schema.

Vitis regenerates its Debug output during an IDE build. After screenshot capture,
run build_arm.py to restore the O2 release ELF, then verify_boot.py to verify it
against the published BOOT.BIN. The BIN itself is not rebuilt by this script.
"""
from pathlib import Path
import hashlib
import shutil
import xml.etree.ElementTree as ET

lab=Path(__file__).resolve().parents[1]
old=lab.parent/'Lab1/vitis_workspace/hello_rtl_divider'
app=lab/'vitis_workspace/hello_hls_rtl_alu'
backup=lab/'report/vitis_metadata_backup'
backup.mkdir(parents=True,exist_ok=True)
for name in ['.project','.cproject']:
    if not (backup/name).exists(): shutil.copyfile(app/name,backup/name)

cproject=(old/'.cproject').read_text().replace('hello_rtl_divider','hello_hls_rtl_alu')
(app/'.cproject').write_text(cproject,encoding='utf-8')

prj=(old/'hello_rtl_divider.prj').read_text()
prj=prj.replace('hello_rtl_divider','hello_hls_rtl_alu')
prj=prj.replace('Lab1/vitis_workspace','Lab2/vitis_workspace')
prj=prj.replace('platform_section4_divider','lab2_platform')
root=ET.fromstring(prj)
root.set('mssSignature',hashlib.md5((app/'system.mss').read_bytes()).hexdigest())
ET.register_namespace('sdkproject','http://www.xilinx.com/sdkproject')
ET.register_namespace('xmi','http://www.omg.org/XMI')
ET.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance')
ET.ElementTree(root).write(app/'hello_hls_rtl_alu.prj',encoding='ASCII',xml_declaration=True)

system_file=lab/'vitis_workspace/hello_hls_rtl_alu_system/hello_hls_rtl_alu_system.sprj'
tree=ET.parse(system_file)
tree.getroot().set('xmlns:sdsproject','http://www.xilinx.com/sdsproject')
for configuration in tree.findall('configuration'):
    options=configuration.find('configBuildOptions')
    if not options.findall('applications'):
        ET.SubElement(options,'applications',name='hello_hls_rtl_alu',
                      domainName='standalone_ps7_cortexa9_0',
                      domainPrettyName='standalone_ps7_cortexa9_0',appBuildConfig=configuration.get('name'))
    for application in options.findall('applications'):
        application.set('appBuildConfig',configuration.get('name'))
ET.register_namespace('systemproject','http://www.xilinx.com/systemproject')
ET.register_namespace('sdsproject','http://www.xilinx.com/sdsproject')
tree.write(system_file,encoding='ASCII',xml_declaration=True)
print('Vitis project metadata ready; restore the release ELF after IDE capture.')
