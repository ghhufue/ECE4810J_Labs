"""Build the Lab 2 PDF and Markdown using the Lab 1 visual conventions.

Run with the Codex bundled Python (reportlab, Pillow, pypdf).
All figures are existing, unmodified experimental screenshots.
"""
from pathlib import Path
from html import unescape
from xml.sax.saxutils import escape
import json
import hashlib
import re

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Table, TableStyle, Preformatted

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent
PDF = ROOT / 'Lab2_Report_Group2.pdf'
MD = ROOT / 'Lab2_Report_Group2.md'
META = ROOT / 'metadata'
META.mkdir(exist_ok=True)
for name, filename in [('Times', 'times.ttf'), ('TimesBold', 'timesbd.ttf'),
                       ('TimesItalic', 'timesi.ttf'), ('Mono', 'consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / filename)))
pdfmetrics.registerFontFamily('Times', normal='Times', bold='TimesBold', italic='TimesItalic', boldItalic='TimesBold')
W, H = A4
M, BOTTOM = 48, 48
CW = W - 2*M
ST = {
    'body': ParagraphStyle('body', fontName='Times', fontSize=10.7, leading=14.2, spaceAfter=7),
    'small': ParagraphStyle('small', fontName='Times', fontSize=9.2, leading=12.1, spaceAfter=6),
    'caption': ParagraphStyle('caption', fontName='TimesItalic', fontSize=9, leading=11.5, alignment=TA_CENTER, spaceAfter=8),
    'h1': ParagraphStyle('h1', fontName='TimesBold', fontSize=18, leading=22, spaceAfter=12),
    'h2': ParagraphStyle('h2', fontName='TimesBold', fontSize=12.2, leading=15, spaceAfter=7),
    'cell': ParagraphStyle('cell', fontName='Times', fontSize=9.2, leading=11.9),
    'headcell': ParagraphStyle('headcell', fontName='TimesBold', fontSize=9.2, leading=11.9),
}


class Report:
    def __init__(self):
        self.c = canvas.Canvas(str(PDF), pagesize=A4, pageCompression=1)
        self.c.setTitle('ECE4810J Lab 2 Report Group 2')
        self.c.setAuthor('Yuan Haotong; Zhao Tong')
        self.c.setSubject('HLS and RTL RV32IM ALUs, SD boot, PYNQ and pipelining')
        self.page, self.y, self.fig_no = 0, 0, 0
        self.md, self.figures, self.layout = [], [], []

    def need(self, height):
        if self.y-height < BOTTOM:
            raise ValueError(f'Overflow page {self.page}: y={self.y:.1f}, need={height:.1f}')

    def footer(self):
        self.c.setFont('Times', 9)
        self.c.setFillColor(colors.HexColor('#444444'))
        self.c.drawString(M, 29, 'ECE4810J  |  Fall 2026  |  Group 2')
        self.c.drawRightString(W-M, 29, str(self.page))
        self.layout.append({'page': self.page, 'body_bottom': round(self.y, 2)})

    def new(self, title=None):
        if self.page:
            self.footer()
            self.c.showPage()
        self.page += 1
        self.c.setFillColor(colors.black)
        self.c.setFont('Times', 9)
        self.c.drawString(M, H-30, 'Lab 2  Design with High Level Synthesis on Arty Z7')
        self.c.drawRightString(W-M, H-30, 'Group 2')
        self.y = H-57
        if title:
            self.p(title, 'h1', md='# '+title)
            self.c.bookmarkPage('page'+str(self.page))
            self.c.addOutlineEntry(title, 'page'+str(self.page), level=0)

    def p(self, text, style='body', md=None):
        obj = Paragraph(text, ST[style])
        _, height = obj.wrap(CW, 2000)
        gap = ST[style].spaceAfter
        self.need(height+gap)
        obj.drawOn(self.c, M, self.y-height)
        self.y -= height+gap
        self.md.append(md if md is not None else unescape(re.sub(r'<[^>]*>', '', text)))

    def h(self, text):
        self.p(text, 'h2', md='## '+text)

    def table(self, headers, rows, fractions=None):
        widths = [CW*x for x in fractions] if fractions else [CW/len(headers)]*len(headers)
        data = [[Paragraph(escape(str(x)), ST['headcell']) for x in headers]]
        data += [[Paragraph(escape(str(x)), ST['cell']) for x in row] for row in rows]
        t = Table(data, colWidths=widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e9edf1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f7f8fa')]),
            ('GRID', (0,0), (-1,-1), .5, colors.HexColor('#d9d9d9')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 7), ('RIGHTPADDING', (0,0), (-1,-1), 7),
            ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        _, height = t.wrap(CW, 2000)
        self.need(height+10)
        t.drawOn(self.c, M, self.y-height)
        self.y -= height+10
        lines = ['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |']
        lines += ['| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows]
        self.md.append('\n'.join(lines))

    def code(self, text, size=8.8, lang='text'):
        lines = text.rstrip().splitlines()
        if any(pdfmetrics.stringWidth(line, 'Mono', size) > CW-12 for line in lines):
            raise ValueError(f'Code too wide page {self.page}')
        obj = Preformatted(text, ParagraphStyle('code', fontName='Mono', fontSize=size, leading=size*1.27))
        _, height = obj.wrap(CW-12, 2000)
        self.need(height+14)
        obj.drawOn(self.c, M+6, self.y-height)
        self.y -= height+14
        self.md.append('```'+lang+'\n'+text+'\n```')

    def fig(self, filename, caption, width=CW):
        path = ROOT/'images'/filename
        with PILImage.open(path) as im:
            iw, ih = im.size
        height = width*ih/iw
        self.fig_no += 1
        caption = f'Figure {self.fig_no}. '+caption
        cap = Paragraph(caption, ST['caption'])
        _, ch = cap.wrap(CW, 2000)
        self.need(height+5+ch+8)
        self.c.drawImage(ImageReader(str(path)), M+(CW-width)/2, self.y-height, width=width, height=height)
        self.y -= height+5
        cap.drawOn(self.c, M, self.y-ch)
        self.y -= ch+8
        self.figures.append({'file': 'images/'+filename, 'page': self.page, 'caption': caption})
        self.md.append(f'![{caption}](images/{filename})')

    def finish(self):
        self.footer()
        self.c.save()
        MD.write_text('\n\n'.join(self.md)+'\n', encoding='utf-8')
        boot = LAB/'boot/BOOT.BIN'
        boot_hash = (hashlib.sha256(boot.read_bytes()).hexdigest() if boot.is_file()
                     else json.loads((ROOT/'screenshots-manifest.json').read_text(encoding='utf-8'))['boot_sha256'])
        manifest = {'pdf': PDF.name, 'markdown': MD.name, 'pages': self.page, 'figures': self.figures,
                    'layout': self.layout, 'group': 2, 'date': '2026-10-22',
                    'authors': [{'name':'Yuan Haotong','student_id':'523370910163'},
                                {'name':'Zhao Tong','student_id':'523370910137'}],
                    'basis': 'Existing Lab2 sources, tool reports and 2026-10-22 board evidence',
                    'limitations': ['No baseline hardware run captured', 'Serial captures use PuTTY',
                                    'No measured application speedup', 'Logictools not exercised on board'],
                    'boot_sha256': boot_hash}
        (META/'lab2_report_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(f'Created {PDF}: {self.page} pages, {len(self.figures)} figures')


r = Report()

# 1
r.new()
r.p('ECE4810J Lab 2 Report', 'h1', md='# ECE4810J Lab 2 Report')
r.p('Design with High Level Synthesis on Arty Z7', 'h2')
r.p('Digilent Arty Z7-20  |  Fall 2026  |  Group 2  |  22 October 2026')
r.table(['Name', 'Student ID'], [['Yuan Haotong','523370910163'],['Zhao Tong','523370910137']], [.52,.48])
r.h('1 Overview')
r.p('We implemented a 16-bit HLS multiplier and two 32-bit RV32IM ALUs, integrated them with the Zynq processing system, and built an SD boot image. The final hardware uses a pipelined RTL ALU alongside the HLS ALU. Captured board output shows 100 multiplier tests and 7,509 tests for each ALU with zero failures. Jupyter also executed Python and loaded the PYNQ base overlay successfully.')
r.p('The combinational RTL baseline was implemented separately for comparison. Its setup WNS was -87.707 ns at 100 MHz; the pipelined system improved this to +1.979 ns. The report separates those implementation results from the board evidence, which belongs to the pipelined image. [1, 2, 3]')
r.h('Environment')
r.table(['Item','Configuration'], [
    ['Board and device','Arty Z7-20; xc7z020clg400-1'],
    ['Design tools','Vivado, Vitis and Vitis HLS 2022.1 on Windows'],
    ['Hardware clock','100 MHz; 10 ns target period'],
    ['Bare metal software','Standalone Cortex-A9 application; UART 115200, 8N1'],
    ['Python environment','PYNQ Linux; browser Jupyter at 192.168.137.42:9090'],
], [.30,.70])
r.h('Report contents')
r.table(['Part','Pages'], [
    ['Section 2  HLS IPs, baseline ALU and functional tests','2-9'],
    ['Section 3  SD boot and interactive multiplication','10'],
    ['Section 4  Python and PYNQ','11'],
    ['Section 5  Pipelined RTL ALU and board verification','12-14'],
    ['Section 6  Post lab questions and conclusions','15-17'],
    ['References and submission evidence index','18'],
], [.83,.17])

# 2
r.new('2 Custom IP Blocks Using HLS')
r.h('2.1 Multiplier design and integration')
r.p('The HLS top function multiplies two 16-bit unsigned inputs and returns a 32-bit product. AXI4-Lite interface pragmas place both operands, the return value and control registers in one interface bundle. We ran C simulation, synthesis and Verilog co-simulation, exported the IP, and connected it to the same PS AXI interconnect as the RTL multiplier. [1, 4]')
r.table(['HLS multiplier result','Recorded value'], [
    ['C simulation','356 tests; 0 failures'],
    ['C/RTL co-simulation','Pass; XSIM / Verilog'],
    ['Synthesis target / estimated period','10.00 ns / 3.150 ns'],
    ['Synthesis latency / interval','3 cycles / 4 cycles'],
    ['HLS estimated resources','193 LUT; 116 FF; 1 DSP; 0 BRAM'],
], [.51,.49])
r.fig('vivado_multipliers_highlighted.jpg', 'Implemented multiplier leaf cells: RTL in red and HLS in yellow. This view is from the final pipelined ALU system.')
r.p('The final address map assigns RTL multiplier 0x43C00000, HLS multiplier 0x43C10000, RTL pipelined ALU 0x43C20000 and HLS ALU 0x43C30000. The RTL multiplier packs A into bits 31:16 and B into bits 15:0 of its input register; the HLS block is controlled through generated driver functions.', 'small')

# 3
r.new('2.2 RV32IM ALU Operations')
r.p('Both ALUs accept two 32-bit operands and a 5-bit selector and return a 32-bit result. The selector encoding follows the manual. Arithmetic results are 32-bit bit patterns; add, subtract and low multiplication wrap modulo 2^32. [1, p. 9]')
r.table(['ID','Operation','Result interpretation'], [
    ['0','ADD','A + B'], ['1','SUB','A - B'], ['2','SLT','Signed A < B, returned as 0 or 1'],
    ['3','SLTU','Unsigned A < B, returned as 0 or 1'], ['4','AND','Bitwise A AND B'],
    ['5','OR','Bitwise A OR B'], ['6','XOR','Bitwise A XOR B'],
    ['7','SLL','Logical left shift by B[4:0]'], ['8','SRL','Logical right shift by B[4:0]'],
    ['9','SRA','Arithmetic right shift by B[4:0]'], ['10','MUL','Low 32 product bits'],
    ['11','MULH','High 32 product bits, signed x signed'], ['12','MULHSU','High 32 product bits, signed x unsigned'],
    ['13','MULHU','High 32 product bits, unsigned x unsigned'], ['14','DIV','Signed quotient, truncated toward zero'],
    ['15','DIVU','Unsigned quotient'], ['16','REM','Signed remainder; sign follows dividend'],
    ['17','REMU','Unsigned remainder'],
], [.09,.20,.71])
r.h('Exceptional operands and completeness')
r.p('A zero divisor returns 0xffffffff for DIV/DIVU and the original dividend for REM/REMU. INT_MIN divided by -1 returns 0x80000000 with zero remainder. Only the low five bits of the shift amount are used, so shifting by 33 is equivalent to shifting by 1. Unused selectors return zero.')
r.p('The reference RTL uses always_comb with a default assignment and complete case handling. Signed comparisons and arithmetic right shift use explicit signed casts. The HLS implementation uses unsigned arithmetic, magnitude conversion and sign correction to avoid C++ signed overflow. High signed products are derived from one unsigned product. [4]')

# 4
r.new('2.3 HLS Functional Verification')
r.p('An independent Python integer model generates 289 directed pairs from 17 edge values and 128 deterministic random pairs. Each of the 417 pairs is tested on all 18 operations, followed by three invalid-selector cases: 417 x 18 + 3 = 7,509 vectors. The HLS test bench checks each result against these stored expected values. [4]')
r.fig('hls_alu_csimulation_pass.jpg', 'HLS ALU C simulation: all 18 selectors covered, with 7,509 vectors and zero failures.', width=480)
r.fig('hls_alu_cosimulation_pass.jpg', 'HLS ALU C/RTL co-simulation report with Verilog Pass status.', width=480)
r.p('The Verilog co-simulation report records transaction latencies of 54-96 cycles and intervals of 45-87 cycles. These simulated transactions include interface activity; they should not be equated to the scheduled arithmetic latency in the synthesis report. Both checks use expected values from the independent model rather than accepting agreement between RTL and HLS alone.', 'small')

# 5
r.new('2.4 HLS Synthesis Results')
r.p('The HLS solution targets xc7z020clg400-1 with a 10 ns clock and a 2.70 ns clock uncertainty. The ALU uses an AXI4-Lite control interface. Its C/C++ operations are scheduled into multiple cycles, with separate sequential unsigned division and remainder units visible in the synthesis hierarchy. [4]')
r.fig('hls_alu_synthesis_summary.jpg', 'HLS ALU synthesis summary, including timing, latency and estimated resources.')
r.table(['Metric','HLS multiplier','HLS ALU'], [
    ['Target period','10.00 ns','10.00 ns'], ['Estimated period','3.150 ns','6.912 ns'],
    ['Scheduled latency','3 cycles','4-39 cycles'], ['Initiation interval','4 cycles','5-40 cycles'],
    ['LUT estimate','193','2,332'], ['FF estimate','116','1,687'],
    ['DSP / BRAM estimate','1 / 0','3 / 0'],
], [.40,.30,.30])
r.p('These are HLS estimates before Vivado implementation. Routed utilization differs because technology mapping, DSP inference and optimization alter the generated logic. For example, the routed HLS ALU instance uses 1,259 LUTs, 1,079 FFs and 4 DSPs. Resource comparisons later in this report use routed hierarchical data on both sides.')

# 6
r.new('2.5 Combinational RTL Baseline')
r.p('The Section 2 baseline pairs rtl_alu with hls_alu and retains both multipliers. The RTL arithmetic datapath is combinational, including division and remainder. Its wrapper exposes four AXI registers. The following views belong to the separate lab2_baseline implementation. [2]')
r.fig('baseline_alus_highlighted.jpg', 'Baseline implemented design: combinational RTL ALU in red and HLS ALU in yellow.')
r.fig('baseline_utilization_summary.jpg', 'Baseline routed utilization summary for the complete PL system.')
r.p('The complete baseline contains 5,032 LUTs, 2,339 FFs, 10 DSPs and no block RAM. No latches are reported. The highlighted ALU regions represent part of this system; PS interface logic, interconnect and multiplier IPs are also included in the total.', 'small')

# 7
r.new('2.6 Baseline Timing and Resources')
r.fig('baseline_design_timing_summary.jpg', 'Baseline at the 100 MHz target: setup WNS -87.707 ns; timing constraints are not met.')
r.p('The baseline has 32 setup failing endpoints and setup TNS -2,783.881 ns. Hold timing passes with WHS +0.012 ns. The large combinational division path cannot satisfy a 10 ns period. Passing functional simulation does not establish reliable operation at this clock. No board run of this baseline is included. [2]')
r.table(['Routed baseline instance','LUT','FF','DSP'], [
    ['RTL multiplier','49','138','1'], ['HLS multiplier','75','155','1'],
    ['Combinational RTL ALU','3,098','320','4'], ['HLS ALU','1,259','1,079','4'],
    ['Entire PL system','5,032','2,339','10'],
], [.52,.16,.16,.16])
r.p('The instance counts include each IP\'s AXI interface. Their sum is below the whole-system total because the system also contains shared interface and infrastructure logic. The HLS ALU uses fewer LUTs but more registers than the combinational RTL ALU. Its scheduled multi-cycle datapath avoids forcing all arithmetic through one combinational cycle.')

# 8
r.new('2.7 ARM Application and AXI Access')
r.p('The application initializes the HLS drivers, runs automatic self-tests and enters a UART menu. RTL access writes A at +0x00, B at +0x04 and selector/start at +0x08, then reads the result at +0x0c. The final AXI slave holds off read acceptance while computation is busy. HLS access sets operands and selector, starts the IP, polls completion with a timeout, and reads its return register. [4]')
r.fig('vitis_alu_build_finished.jpg', 'Vitis IDE build of hello_hls_rtl_alu completed successfully.')
r.code('Xil_Out32(RTL_ALU_BASE + 0, a);\nXil_Out32(RTL_ALU_BASE + 4, b);\nXil_Out32(RTL_ALU_BASE + 8, op);\nresult = Xil_In32(RTL_ALU_BASE + 12);', lang='c')
r.p('The AXI wrapper buffers write address and write data independently, supports byte strobes, keeps responses stable during backpressure, and returns SLVERR for invalid accesses or writes while busy. A zero byte-enable write does not start an operation. Reset clears pending activity. The AXI test bench passes all 7,509 vectors plus these protocol checks.')
r.p('The screenshot records a Debug IDE build with -O0. The released ELF uses -O2 and the same source; its recorded build enables -Wall -Wextra -Werror. The published BOOT.BIN was checked against the restored release ELF, FSBL and bitstream. The IDE screenshot is compilation evidence; the next page supplies execution evidence. [3, 4]', 'small')

# 9
r.new('2.8 Board Functional Results')
r.p('The captured PuTTY session on 22 October 2026 contains the startup self-test and a second complete self-test after reset. Both use the final SD image with the pipelined RTL ALU. Every valid selector has 417 directed/random cases, with three additional invalid selectors in each 7,509-case ALU total. [3]')
r.fig('lab2_alu_selftest.png', 'Actual board self-test: all 18 ALU operations and both 7,509-case totals pass.', width=420)
r.table(['Board check','Recorded result'], [
    ['RTL/HLS 16-bit multipliers','100 operand pairs; 0 failures'],
    ['RTL pipelined ALU','7,509 tests; 0 failures'], ['HLS ALU','7,509 tests; 0 failures'],
    ['Overall status','LAB2 SELF-TEST: PASS'],
], [.52,.48])
r.p('The serial captures use PuTTY rather than the Vitis Serial Terminal named in the Section 2 checklist. They record the same application results and also support the Section 3 SD-boot checks. No separate combinational-baseline board capture is claimed.', 'small')

# 10
r.new('3 SD Boot and Interactive Operation')
r.p('The boot configuration orders the Zynq FSBL, PL bitstream and ARM application. With BOOT.BIN in the FAT32 SD root and JP4 set to SD, the captured terminal shows the application banner, self-test and menu. The UART uses 115200 baud, 8 data bits, no parity, one stop bit and no flow control. [1, pp. 10-12; 3]')
r.fig('lab2_sd_boot.png', 'Startup output captured for the SD boot test with the final Lab 2 image.', width=360)
r.fig('lab2_sd_interactive_multiplier.png', 'Interactive multiplication: 2 x 3 = 0x00000006 and 65535 x 65535 = 0xfffe0001; both RTL and HLS pass.', width=470)
r.p('The menu command m accepts two 16-bit operands and prints both hardware results and the expected product; a selects an ALU operation; t reruns the full self-test. Repeated menu prompts show that execution continues after each transaction.')
r.p('The 4,313,680-byte image passed partition-header and payload checks. Its SHA-256 is shown below; the current file matches this value. [4]', 'small')
r.code('9f57c42b36ea5f82667ab36efd79304cbb6\nb2ceaaef4f7b6c0282296e1ca9d08', size=8.6)

# 11
r.new('4 Python and PYNQ on Arty Z7')
r.p('For the Python exercise we used the PYNQ Linux environment separately from the bare-metal BOOT.BIN. The browser reached Jupyter at 192.168.137.42:9090. The file view contains base, common, getting_started, logictools and pynq_peripherals directories; the notebook view executes Python and loads BaseOverlay. [3]')
r.fig('lab2_pynq_jupyter_files.png', 'Jupyter file browser with the board address visible and the supplied notebook directories.')
r.fig('lab2_pynq_overlay_loaded.png', 'Notebook execution: BaseOverlay("base.bit") completes and prints PYNQ overlay loaded OK; a separate cell prints hello.')
r.p('These captures establish browser access, kernel execution and successful base-overlay construction. They do not establish tests of every peripheral, a logictools run or a custom ALU overlay. The notebook uses the supplied base overlay rather than importing the bare-metal Lab 2 boot image.', 'small')

# 12
r.new('5 RTL ALU Pipelining')
r.h('5.1 Datapath and completion')
r.p('The optional implementation replaces the combinational RTL IP with rtl_pipe_alu. Simple arithmetic, logic and shifts produce a registered result when a request is sampled. Multiplication registers the unsigned 64-bit product, then selects the low or corrected high word. Division uses 32 restoring stages between input preparation and final sign correction. [4]')
r.table(['Core path','Clock edges relative to sampled start'], [
    ['ADD through SRA and invalid selector','Result and done at the sampling edge'],
    ['MUL, MULH, MULHSU, MULHU','Product captured at start; result at the next edge'],
    ['DIV, DIVU, REM, REMU','Input at start; 32 divide stages; result 33 cycles later'],
], [.41,.59])
r.p('Each restoring stage shifts one dividend bit into the partial remainder, compares it to the divisor, conditionally subtracts, and appends a quotient bit. Valid, quotient sign, remainder sign, operation choice and the divide-by-zero flag travel with the data. Reset clears valid bits so an interrupted computation cannot publish an old result.')
r.fig('vivado_alus_highlighted.jpg', 'Final implemented design: pipelined RTL ALU in red and HLS ALU in yellow.')
r.p('The AXI wrapper permits one outstanding arithmetic request and stalls reads while busy. Therefore, the core\'s pipeline structure is not evidence of one completed software transaction per cycle. AXI handshakes and processor accesses add latency to the core schedule.', 'small')

# 13
r.new('5.2 Routed Pipeline Implementation')
r.p('The final system retains the same HLS ALU, multipliers, PS configuration and 100 MHz target as the baseline. The following screenshots document the complete routed system used by the released SD image. [2]')
r.fig('vivado_utilization_summary.jpg', 'Final PL utilization: 4,414 LUTs, 6,598 FFs, 10 DSPs, no block RAM and no latches.')
r.fig('vivado_design_timing_summary.jpg', 'Final routed timing: setup WNS +1.979 ns and hold WHS +0.013 ns; all timing constraints met.')
r.p('Setup, hold and pulse-width failing endpoint counts are zero. Setup TNS and hold THS are zero. The positive margins demonstrate closure for the constrained 100 MHz implementation; they do not constitute a measured application speedup or a sweep of the maximum operating frequency.', 'small')

# 14
r.new('5.3 Pipeline Board Checks')
r.p('The full board self-test already exercises all multiply, divide and remainder selectors. Additional interactive captures make the signed behavior and special operands visible. Each line reports the RTL and HLS result; the values below also agree with the independent expected results. [3]')
r.fig('lab2_pipe_alu_mul_div_rem.png', 'Signed pipeline checks: MUL(-20,5) = 0xffffff9c; DIV(-20,3) = 0xfffffffa; REM(-20,3) = 0xfffffffe.', width=400)
r.fig('lab2_alu_boundary.png', 'Boundary checks: DIV(123,0) = 0xffffffff; REM(123,0) = 123; DIV(INT_MIN,-1) = 0x80000000.', width=400)
r.p('MATCH alone means that both implementations agree. Correctness here is additionally supported by the expected bit patterns and the self-test\'s stored reference results. RTL simulation separately passes 7,509 vectors for each architecture and reset cancellation; AXI simulation covers 7,509 vectors and protocol corner cases. [4]', 'small')

# 15
r.new('6 Post Lab Questions')
r.h('6.1 RTL and HLS resource utilization')
r.p('The following counts come from routed hierarchical reports, including each IP\'s interface. The HLS instance has identical counts in the baseline and final system. These are separate from the earlier HLS synthesis estimates. [2]')
r.table(['Instance','LUT','FF','DSP','BRAM'], [
    ['RTL multiplier','49','138','1','0'], ['HLS multiplier','75','155','1','0'],
    ['Combinational RTL ALU','3,098','320','4','0'],
    ['Pipelined RTL ALU','2,482','4,579','4','0'], ['HLS ALU','1,259','1,079','4','0'],
], [.44,.14,.14,.14,.14])
r.p('The HLS multiplier needs 26 more LUTs and 17 more FFs than the RTL multiplier, with the same DSP count. The generated AXI control interface and scheduled datapath differ from the custom RTL register interface, so this is an IP-level comparison rather than an isolated multiplication operator comparison.')
r.p('The combinational RTL ALU uses 1,839 more LUTs but 759 fewer FFs than the HLS ALU. Its division/remainder network creates a long path; HLS schedules multi-cycle arithmetic and inserts state and registers. The exact area difference also depends on interface logic, sharing, mapping and optimization. The observations support an architectural explanation, not a claim that one language always produces smaller circuits.')
r.h('Effect of explicit RTL pipelining')
r.table(['Complete PL system','Baseline','Pipeline'], [
    ['LUT','5,032','4,414'], ['FF','2,339','6,598'], ['DSP / BRAM','10 / 0','10 / 0'],
    ['Setup WNS at 100 MHz','-87.707 ns','+1.979 ns'],
    ['Hold WHS','+0.012 ns','+0.013 ns'], ['Setup failing endpoints','32','0'],
], [.48,.26,.26])
r.p('Pipelining reduces total LUT use by 618 (12.3%) and adds 4,259 FFs (182.1%). At the RTL ALU instance it reduces LUTs by 616 and adds the same 4,259 FFs. Registers shorten arithmetic paths and preserve intermediate division state; the changed architecture and mapping also alter logic area. The final system meets the clock target at the cost of more sequential state and multi-cycle completion.')

# 16
r.new('6.2 Design Choices and Overlays')
r.h('Ten sorting algorithms in one IP')
r.p('We would start with HLS for a block implementing ten sorting algorithms. C/C++ makes the algorithm variants, test data and reference checks easier to express and reuse. We could verify ordering and permutation preservation in C simulation before exploring the hardware architecture. This is a development choice; the experiment does not measure sorting hardware.')
r.p('We would first define bounded array sizes, supported element widths, memory interfaces and the required throughput. Loop dependencies, data-dependent iteration and memory access patterns still limit hardware parallelism. Pipelining and unrolling would be introduced only after checking resource and bandwidth constraints. RTL would be appropriate for a fixed sorting network or a critical block requiring precise cycle control. HLS is useful for comparing many algorithms, while final quality still depends on the architecture.')
r.h('What is a Jupyter notebook and why use it')
r.p('A Jupyter notebook combines executable cells, explanatory text and saved output in a browser document. A kernel executes the code; the browser is its interactive front end. In this exercise the server and Python kernel run on the board\'s ARM processor. It lets us check imports, run short experiments and retain results alongside explanations without rebuilding a standalone application for each Python edit. The screenshot demonstrates both a Python print and an overlay load. [1, pp. 13-15; 3]')
r.h('What are overlays and their benefits')
r.p('An overlay packages a programmable-logic design for reuse from Python. In the documented PYNQ interface, a bitstream configures the PL and a matching hardware handoff file describes IPs and connections; Python classes provide access to the design. Loading an overlay changes the PL hardware while Linux remains available on the PS. Hardware designers can build an accelerator once and expose a reusable interface to application developers. The bitstream must match the target board and available connections. [5]')
r.h('Which overlays are available in this environment')
r.p('The captured PYNQ image exposes base and logictools notebook directories. BaseOverlay("base.bit") was successfully instantiated, so the base overlay is the one demonstrated on this Arty Z7 setup. The PYNQ-Z1 documentation, relevant to the image specified in the lab manual, also describes the logictools overlay: Boolean, pattern and finite-state-machine generation with trace capture. Its presence in documentation and the notebook directory does not prove that it was exercised on our board. [1, 3, 6, 7]')
r.p('The base overlay provides drivers for board I/O and can serve as a starting point for custom overlays. Peripheral pin assignments and physical interfaces remain board dependent; using a PYNQ-Z1 image does not establish that all PYNQ-Z1 peripherals exist on Arty Z7. No additional overlay or custom Lab 2 ALU overlay was tested here. [6]', 'small')

# 17
r.new('6.3 C and Python Development Flows')
r.p('The C/C++ part and the PYNQ part operate at different stages. In Part 2, HLS translates a restricted C/C++ function into hardware. In Part 4, ordinary Python executes on the ARM under Linux and controls already-built PL hardware through the PYNQ interface. Python statements are not automatically synthesized into RTL. [1, 5]')
r.table(['Aspect','Part 2 HLS and bare metal','Part 4 PYNQ'], [
    ['Hardware creation','C/C++ top function becomes RTL; Vivado implements the integrated design','An existing overlay supplies PL hardware; custom hardware still needs a design flow'],
    ['Control program','Compiled C ARM application with generated HLS drivers and MMIO','Python cells in a Linux-hosted Jupyter kernel'],
    ['Deployment','FSBL, bitstream and application packaged in BOOT.BIN','Linux SD image plus overlay bitstream, metadata and Python drivers'],
    ['Iteration','Hardware edits require synthesis/implementation; software edits require compile/link','Python edits run interactively; overlay edits still require a hardware rebuild'],
    ['Timing and overhead','Explicit register transactions; deterministic core clocking','Interpreter, operating system and driver overhead around accelerator calls'],
    ['Observed result','18 ALU operations and SD menu tested on the final hardware','Python execution and supplied base overlay loading demonstrated'],
], [.19,.405,.405])
r.h('Conclusions')
r.p('We completed HLS IP generation, AXI integration, SD-boot execution and a basic PYNQ notebook exercise. The independent test vectors and board log support all 18 RV32IM operations, including signed high multiplication, divide by zero and signed division overflow. The pipelined RTL design resolves the baseline\'s 100 MHz setup violation, and its routed utilization exposes the register cost of that change.')
r.p('The results do not measure end-to-end acceleration over software or establish the maximum clock frequency. The combinational baseline is validated by simulation and implementation reports, while the captured hardware tests use the pipelined image. PuTTY supplies the serial evidence; the Vitis screenshot establishes a successful IDE build. PYNQ evidence is limited to the supplied base overlay and does not demonstrate a custom ALU Python driver.')

# 18
r.new('References and Evidence Index')
r.p('[1] ECE4810J, Lab 2 Design with High Level Synthesis on Arty Z7 SoC Development Platform, Digilent Arty Z7-20 Version, Fall 2026. Local file: Lab2/docs/ECE4810J_FA2026_Lab_2_Manual_Arty_Z7-20.pdf. Requirements: pp. 9-17.', 'small')
r.p('[2] Vivado 2022.1 routed reports: Lab2/logs/baseline_utilization_hierarchical.txt, baseline_utilization.txt, baseline_timing.txt; utilization_hierarchical.txt, utilization.txt and timing.txt. The baseline and final systems share a 100 MHz clock target.', 'small')
r.p('[3] Board evidence captured 22 October 2026: Lab2/report/logs/lab2_serial.txt and the lab2_*.png images in Lab2/report/images/. The serial log includes startup, interactive arithmetic, boundary cases and repeated self-test output.', 'small')
r.p('[4] Lab2 implementation and verification artifacts: hls/, rtl/, tests/, software/, scripts/, boot/manifest.json and boot/lab2.bif; logs/hls_multiplier_csim.txt, hls_multiplier_csynth.txt, hls_multiplier_cosim.txt, hls_alu_csim.txt, hls_alu_csynth.txt, hls_alu_cosim.txt, rtl_simulation.txt, axi_simulation.txt, vitis_ide_build.txt and boot_validation.txt.', 'small')
r.p('[5] PYNQ documentation, Overlay. Accessed 22 October 2026.<br/><link href="https://pynq.readthedocs.io/en/latest/pynq_libraries/overlay.html">https://pynq.readthedocs.io/en/latest/pynq_libraries/overlay.html</link>', 'small')
r.p('[6] PYNQ v2.4 documentation, PYNQ-Z1 Base Overlay. Accessed 22 October 2026.<br/><link href="https://pynq.readthedocs.io/en/v2.4/pynq_overlays/pynqz1/pynqz1_base_overlay.html">https://pynq.readthedocs.io/en/v2.4/pynq_overlays/pynqz1/pynqz1_base_overlay.html</link>', 'small')
r.p('[7] PYNQ v2.5 documentation, PYNQ-Z1 Logictools Overlay. Accessed 22 October 2026.<br/><link href="https://pynq.readthedocs.io/en/v2.5/pynq_overlays/pynqz1/pynqz1_logictools_overlay.html">https://pynq.readthedocs.io/en/v2.5/pynq_overlays/pynqz1/pynqz1_logictools_overlay.html</link>', 'small')
r.h('Submission evidence index')
r.table(['Manual item','Report location or accompanying source'], [
    ['Section 2 multiplier implementation','Figure 1; board result on p. 9 and Figure 11'],
    ['HLS ALU simulation, synthesis, co-simulation','Figures 2-4; synthesis table on p. 5'],
    ['Baseline implementation and timing','Figures 5-7; routed resources on p. 7'],
    ['Vitis build and ALU board output','Figures 8-9; method qualification on p. 9'],
    ['SD boot and interactive multiplier','Figures 10-11'],
    ['PYNQ notebook including address bar','Figures 12-13'],
    ['Pipeline implementation and tests','Figures 14-18; comparison on p. 15'],
    ['Post lab questions','Section 6 on pp. 15-17'],
    ['Code delivered separately','rtl/rtl_alu.sv; rtl/rtl_pipe_alu.sv; hls/hls_alu.cpp; hls/hls_alu.h; hls/test_hls_alu.cpp; software/hls_rtl_alu.c; tests/alu_vectors.h; AXI/IP sources and build scripts'],
], [.38,.62])
r.p('The companion Markdown is editable; the PDF is the compiled group report. Code is kept as source files rather than printed in full, as permitted by the manual\'s separate-code deliverable. Individual peer evaluations are completed and submitted separately. All figures are existing experimental captures, with no generated substitute screenshots.', 'small')
r.finish()
