"""Package the Section 2 combinational ALU for implementation comparison."""
from pathlib import Path
import xml.etree.ElementTree as ET

lab=Path(__file__).resolve().parents[1]
source=lab/'ip_repo/rtl_pipe_alu_1.0'
target=lab/'ip_repo/rtl_alu_1.0'
for src in source.rglob('*'):
    if src.is_file():
        relative=str(src.relative_to(source)).replace('rtl_pipe_alu','rtl_alu')
        dst=target/relative
        dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(src.read_text().replace('rtl_pipe_alu','rtl_alu'),encoding='utf-8')
(target/'src/rtl_alu.sv').write_text((lab/'rtl/rtl_alu.sv').read_text(),encoding='utf-8')
bridge=target/'hdl/rtl_alu_v1_0_S00_AXI.v'
text=bridge.read_text()
start=text.index('rtl_alu core(')
end=text.index(');',start)+2
replacement='''reg done_reg;
reg [31:0] held_result;
wire [31:0] combinational_result;
rtl_alu core(
    .clk(S_AXI_ACLK), .opa(operand_a), .opb(operand_b),
    .func(ALU_FUNC'(selector)), .result(combinational_result)
);
assign done = done_reg;
assign result = held_result;
always @(posedge S_AXI_ACLK) begin
    if (!S_AXI_ARESETN) begin done_reg <= 0; held_result <= 0; end
    else begin
        done_reg <= start;
        if (start) held_result <= combinational_result;
    end
end'''
bridge.write_text(text[:start]+replacement+text[end:],encoding='utf-8')
ns='http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'
ET.register_namespace('spirit',ns)
ET.register_namespace('xilinx','http://www.xilinx.com')
tree=ET.parse(target/'component.xml')
for file in tree.findall(f'.//{{{ns}}}file'):
    name=file.find(f'{{{ns}}}name')
    if name is not None and name.text=='hdl/rtl_alu_v1_0_S00_AXI.v':
        file.find(f'{{{ns}}}fileType').text='systemVerilogSource'
tree.write(target/'component.xml',encoding='utf-8',xml_declaration=True)
print('Packaged combinational baseline:',target)
