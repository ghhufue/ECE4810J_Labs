"""Build the Group 2 Lab 1 PDF and its Markdown companion.

Use the bundled Python runtime, which includes reportlab, Pillow and pypdf.
Missing transition photos are drawn as placeholders without creating image assets.
"""
from pathlib import Path
from xml.sax.saxutils import escape
from html import unescape
import json

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Preformatted, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent
IMAGES = ROOT / 'images'
SCRIPTS = ROOT / 'scripts'
METADATA = ROOT / 'metadata'
PDF = ROOT / 'Lab1_Report_Group2.pdf'
MD = ROOT / 'Lab1_Report_Group2.md'
FONT_DIR = Path('C:/Windows/Fonts')
for name, filename in [('Times', 'times.ttf'), ('TimesBold', 'timesbd.ttf'),
                       ('TimesItalic', 'timesi.ttf'), ('Mono', 'consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily('Times', normal='Times', bold='TimesBold', italic='TimesItalic', boldItalic='TimesBold')

W, H = A4
M = 48
CW = W - 2*M
BOTTOM = 48
styles = {
    'body': ParagraphStyle('body', fontName='Times', fontSize=10.7, leading=14.2, spaceAfter=7),
    'small': ParagraphStyle('small', fontName='Times', fontSize=9.2, leading=12.1, spaceAfter=6),
    'caption': ParagraphStyle('caption', fontName='TimesItalic', fontSize=9, leading=11.5,
                              alignment=TA_CENTER, spaceAfter=7),
    'h1': ParagraphStyle('h1', fontName='TimesBold', fontSize=18, leading=22, spaceAfter=12),
    'h2': ParagraphStyle('h2', fontName='TimesBold', fontSize=12.2, leading=15, spaceBefore=3, spaceAfter=7),
    'cell': ParagraphStyle('cell', fontName='Times', fontSize=9.2, leading=11.9),
    'headcell': ParagraphStyle('headcell', fontName='TimesBold', fontSize=9.2, leading=11.9),
}


class Report:
    def __init__(self):
        self.c = canvas.Canvas(str(PDF), pagesize=A4, pageCompression=1)
        self.c.setTitle('ECE4810J Lab 1 Report Group 2')
        self.c.setAuthor('Yuan Haotong; Zhao Tong')
        self.c.setSubject('Arty Z7-20 Zynq systems, GPIO, AXI multiplier and divider')
        self.page = 0
        self.y = 0
        self.markdown = []
        self.figures = []
        self.pending = []

    def need(self, height):
        if self.y - height < BOTTOM:
            raise ValueError(f'Layout overflow on page {self.page}: y={self.y:.1f}, height={height:.1f}')

    def footer(self):
        self.c.setFont('Times', 9)
        self.c.setFillColor(colors.HexColor('#444444'))
        self.c.drawString(M, 29, 'ECE4810J  |  Fall 2026  |  Group 2')
        self.c.drawRightString(W-M, 29, str(self.page))

    def new(self, title=None):
        if self.page:
            self.footer()
            self.c.showPage()
        self.page += 1
        self.c.setFillColor(colors.black)
        self.c.setFont('Times', 9)
        self.c.drawString(M, H-30, 'Lab 1  Getting Started with Arty Z7 SoC Development')
        self.c.drawRightString(W-M, H-30, 'Group 2')
        self.y = H-57
        if title:
            self.p(title, 'h1', md='# '+title)

    def p(self, text, style='body', md=None, width=None, gap=None):
        width = width or CW
        obj = Paragraph(text, styles[style])
        _, height = obj.wrap(width, 2000)
        after = styles[style].spaceAfter if gap is None else gap
        self.need(height + after)
        obj.drawOn(self.c, M+(CW-width)/2, self.y-height)
        self.y -= height+after
        self.markdown.append(md if md is not None else unescape(text.replace('<b>', '**').replace('</b>', '**')))

    def h(self, text):
        self.p(text, 'h2', md='## '+text)

    def table(self, headers, rows, widths=None):
        widths = widths or [CW/len(headers)]*len(headers)
        data = [[Paragraph(escape(str(v)), styles['headcell']) for v in headers]]
        data += [[Paragraph(escape(str(v)), styles['cell']) for v in row] for row in rows]
        t = Table(data, colWidths=widths, hAlign='LEFT')
        commands = [('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e9edf1')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d9d9d9')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 7), ('RIGHTPADDING', (0,0), (-1,-1), 7),
                    ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]
        for row in range(2, len(data), 2):
            commands.append(('BACKGROUND', (0,row), (-1,row), colors.HexColor('#f7f8fa')))
        t.setStyle(TableStyle(commands))
        _, ht = t.wrap(CW, 2000)
        self.need(ht+10)
        t.drawOn(self.c, M, self.y-ht)
        self.y -= ht+10
        self.markdown += ['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |']
        self.markdown += ['| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows]

    def code(self, text, size=8.8, leading=None, lang='text', compact=False):
        if compact:
            text = '\n'.join(line.rstrip() for line in text.splitlines() if line.strip())
        lines = text.rstrip().splitlines()
        widest = max((pdfmetrics.stringWidth(line.expandtabs(4), 'Mono', size) for line in lines), default=0)
        if widest > CW-12:
            raise ValueError(f'Code line too wide on page {self.page}: {widest:.1f} > {CW-12:.1f}')
        st = ParagraphStyle('code', fontName='Mono', fontSize=size, leading=leading or size*1.25)
        obj = Preformatted(text.expandtabs(4), st)
        _, ht = obj.wrap(CW-12, 2000)
        self.need(ht+14)
        obj.drawOn(self.c, M+6, self.y-ht)
        self.y -= ht+14
        self.markdown.append('```'+lang+'\n'+text.rstrip()+'\n```')

    def fig(self, filename, caption, width=CW):
        path = IMAGES / filename
        with PILImage.open(path) as im:
            iw, ih = im.size
        height = width*ih/iw
        self.need(height+8)
        self.c.drawImage(ImageReader(str(path)), M+(CW-width)/2, self.y-height,
                         width=width, height=height, preserveAspectRatio=True)
        self.y -= height+5
        self.p(caption, 'caption')
        self.figures.append(f'images/{filename}')
        self.markdown.append(f'![{caption}](images/{filename})')

    def grid(self, items, height=244, photo_width=183, cell_height=276):
        grid_height = cell_height*2
        self.need(grid_height+5)
        top = self.y
        half = CW/2
        for i, (filename, caption, expected) in enumerate(items):
            row, col = divmod(i,2)
            cell_x = M+col*half
            box_y = top-row*cell_height-height
            box_x = cell_x+(half-photo_width)/2
            path = IMAGES / filename
            if path.is_file():
                with PILImage.open(path) as im:
                    iw, ih = im.size
                scale = min(photo_width/iw, height/ih)
                dw, dh = iw*scale, ih*scale
                self.c.drawImage(ImageReader(str(path)), cell_x+(half-dw)/2,
                                 box_y+(height-dh)/2, width=dw, height=dh)
                self.figures.append(f'images/{filename}')
                self.markdown.append(f'![{caption}](images/{filename})')
            else:
                self.c.saveState()
                self.c.setStrokeColor(colors.HexColor('#777777'))
                self.c.setDash(4,3)
                self.c.rect(box_x, box_y, photo_width, height, stroke=1, fill=0)
                self.c.setDash()
                self.c.setFillColor(colors.black)
                self.c.setFont('TimesBold', 12)
                self.c.drawCentredString(box_x+photo_width/2, box_y+height/2+32, 'Photo placeholder')
                self.c.setFont('Times', 10)
                for j, line in enumerate(['Insert actual board photograph']+expected):
                    self.c.drawCentredString(box_x+photo_width/2, box_y+height/2+10-j*15, line)
                self.c.restoreState()
                self.pending.append(f'images/{filename}')
                self.markdown.append('**PHOTO PLACEHOLDER:** '+caption+' Expected: '+'; '.join(expected)+'. Target: `images/'+filename+'`.')
            cap = Paragraph(caption, styles['caption'])
            _, ht = cap.wrap(half-18, 100)
            cap.drawOn(self.c, cell_x+9, box_y-5-ht)
        self.y -= grid_height+5

    def finish(self):
        self.footer()
        self.c.save()
        MD.write_text('\n\n'.join(self.markdown)+'\n', encoding='utf-8')
        (METADATA/'lab1_report_manifest.json').write_text(json.dumps({
            'pdf':PDF.name, 'pages':self.page, 'images_used':sorted(set(self.figures)),
            'photo_placeholders':self.pending, 'group':2,
            'authors':[{'name':'Yuan Haotong','student_id':'523370910163'},
                       {'name':'Zhao Tong','student_id':'523370910137'}]
        }, indent=2), encoding='utf-8')
        print(f'Created {PDF.name}: {self.page} pages; {len(set(self.figures))} distinct images; {len(self.pending)} photo placeholders')


r = Report()

# Page 1
r.new()
r.p('ECE4810J Lab 1 Report', 'h1', md='# ECE4810J Lab 1 Report')
r.p('Getting Started with Arty Z7 SoC Development', 'h2')
r.p('Digilent Arty Z7-20  |  Fall 2026  |  Group 2  |  14 October 2026')
r.table(['Name', 'Student ID'], [['Yuan Haotong','523370910163'],['Zhao Tong','523370910137']], [CW*.52,CW*.48])
r.h('1 Overview')
r.p('We built a basic Zynq system, added memory-mapped GPIO peripherals, and integrated custom multiplier and divider IP blocks. The Hello World program produced the expected UART messages. Four individual button tests showed the corresponding LEDs lit. The multiplier returned 6 for inputs 2 and 3, and the divider reported 11 board-level tests with zero failures. The divider simulation log additionally records 272 passing arithmetic cases and interface checks.')
r.p('The four-step GPIO sequence is documented with board photographs, including simultaneous BTN2 and BTN3 presses with LD2 and LD3 lit, and release of all buttons with LD0 through LD3 unlit. The optional FIR filter exercise in Section 5 is not included.')
r.h('Environment')
r.table(['Item','Configuration'],[
    ['Board and device','Arty Z7-20; xc7z020clg400-1'],
    ['Design tools','Vivado 2022.1 and Vitis 2022.1 on Windows'],
    ['Software domain','Standalone application on ps7_cortexa9_0'],
    ['Serial connection','PuTTY; 115200 baud; 8 data bits; no parity; 1 stop bit; no flow control'],
    ['Custom IP clock','100 MHz for the implemented divider design']
], [CW*.31,CW*.69])
r.h('Report contents')
r.table(['Part','Pages'],[
    ['Section 2  Basic Zynq system and Hello World','2'],
    ['Section 3  GPIO design and board photographs','3-5'],
    ['Section 4  Multiplier and divider design and verification','6-10'],
    ['Section 6  Tcl exercises','11'],
    ['Section 7  Post-lab questions and conclusions','12'],
    ['Appendices  GPIO and divider application code','13-14']
], [CW*.82,CW*.18])

# Page 2
r.new('2 Basic Zynq System')
r.p('The Section 2 Vivado design configures the Zynq processing system using the Arty Z7-20 board preset and exposes DDR and fixed I/O. After generating the HDL wrapper and bitstream, the hardware is exported to Vitis. The standalone Hello World application initializes the platform, prints two messages through the PS UART, and then returns. [1]')
r.fig('helloworld.png', 'Figure 1. Hello World application in the Vitis IDE with Build Finished visible.', width=475)
r.p('For autonomous startup, the SD boot image contains the FSBL, platform bitstream and hello_world.elf. The image is placed at the SD card root as BOOT.BIN. The captured COM10 UART output confirms that the application reaches both print statements.', 'body')
r.fig('section2_helloworld_serial_terminal.png', 'Figure 2. Hello World UART output captured with PuTTY.', width=270)
r.code('Hello World\nSuccessfully ran Hello World application', size=9.3)

# Page 3
r.new('3 Zynq System with GPIO Peripherals')
r.p('The PmodIPs design connects the PS M_AXI_GP0 port to an AXI interconnect and two AXI GPIO peripherals. axi_gpio_buttons has a 4-bit input interface at 0x41200000, and axi_gpio_led drives four LEDs at 0x41210000. The application initializes both devices, sets the button direction to 0xF and LED direction to 0x0, then repeatedly writes (button_data &amp; 0xF) to the LEDs. The complete C program is included in Appendix A.')
r.fig('section3_implemented_timing.png', 'Figure 3. Implemented GPIO design. WNS = 3.135 ns; WHS = 0.094 ns; all user-specified timing constraints are met.', width=450)
r.fig('section3_build.png', 'Figure 4. pmod_app compilation completed successfully in Vitis.', width=450)
r.p('Positive setup and hold slack in Figure 3 show that the implemented design satisfies its specified timing constraints. They do not replace functional checks on the board. The loop copies all four input bits, so multiple LEDs can be asserted together; it also writes zero when all buttons are released.', 'small')

# Page 4
r.new('3.1 Individual Button Checks')
r.p('The four photographs show BTN0 through BTN3 pressed individually and the corresponding LD0 through LD3 lit. The other user LEDs are unlit in each photograph. These observations agree with the direct bit mapping implemented by the GPIO application.')
r.grid([
    ('section3_board_btn0_ld0.jpg','(a) BTN0 pressed and LD0 lit.',[]),
    ('section3_board_btn1_ld1.jpg','(b) BTN1 pressed and LD1 lit.',[]),
    ('section3_board_btn2_ld2.jpg','(c) BTN2 pressed and LD2 lit.',[]),
    ('section3_board_btn3_ld3.jpg','(d) BTN3 pressed and LD3 lit.',[])
], height=244, photo_width=183, cell_height=276)
r.p('Figure 5. Individual button-to-LED correspondence on the Arty Z7-20.', 'caption')
r.p('These photographs verify each single-button mapping. The photographs on the next page also document the combined-button and all-released states.', 'small')

# Page 5
r.new('3.2 Button Transition Sequence')
r.p('The lab manual requests a four-step sequence: BTN3 pressed, BTN2 and BTN3 pressed together, BTN2 pressed alone, and all buttons released. [1, p. 17] The photographs below document all four states: LD3 lit, LD2 and LD3 lit together, LD2 lit alone, and all four user LEDs unlit, respectively.')
r.grid([
    ('section3_board_btn3_ld3.jpg','Step 1. BTN3 pressed; LD3 lit.',[]),
    ('section3_board_btn23_ld23.jpg','Step 2. BTN2 and BTN3 pressed; LD2 and LD3 lit.',[]),
    ('section3_board_btn2_ld2.jpg','Step 3. BTN2 pressed; LD2 lit.',[]),
    ('section3_board_idle_leds_off.jpg','Step 4. All buttons released; LD0 through LD3 unlit.',[])
], height=244, photo_width=183, cell_height=276)
r.p('Figure 6. Board photographs documenting all four states of the GPIO sequence.', 'caption')
r.p('The software polls the raw GPIO level and contains no explicit debounce routine. The expected masks are 0x8, 0xC, 0x4 and 0x0, respectively. The photographs confirm simultaneous operation and that the user LEDs return to zero when all buttons are released.', 'small')

# Page 6
r.new('4 Custom AXI IP Blocks')
r.h('4.1 RTL multiplier design')
r.p('The multiplier accepts two unsigned 16-bit operands and produces a registered 32-bit product. The AXI wrapper stores operand a in bits [31:16] and operand b in bits [15:0] of register 0. The read multiplexer returns the multiplier output at register 1. Both registers are accessed through the IP base address 0x43C00000.')
r.table(['Offset','Software operation','Meaning'],[
    ['0x00','Write / read','Packed operands (a << 16) | b'],
    ['0x04','Read','32-bit product from the arithmetic core']
], [CW*.14,CW*.24,CW*.62])
r.p('The core registers a * b on each rising edge of clk. The application writes 0x00020003 to the operand register, reads the result register and prints the values. The read is performed after the AXI write and diagnostic output; this test does not measure arithmetic or end-to-end acceleration latency.', 'small')
r.code('reg [31:0] productReg;\nassign product = productReg;\nalways @(posedge clk) begin\n    productReg <= a * b;\nend', size=9, lang='verilog')
r.fig('section4_multiplier_build.png', 'Figure 7. hello_rtl_multiplier application build completed and produced hello_rtl_multiplier.elf.', width=475)
r.p('The application build console is the evidence of software compilation. System-project icons elsewhere in the IDE are separate from the successful application build shown here.', 'small')

# Page 7
r.new('4.2 Multiplier Results and Resources')
r.fig('section4_utilization.png', 'Figure 8. Resource utilization of the implemented multiplier system.', width=475)
r.table(['Resource','Used','Device capacity','Utilization'],[
    ['Slice LUTs','397','53,200','0.75%'],
    ['Slice registers','569','106,400','0.53%'],
    ['DSP blocks','1','220','0.45%']
], [CW*.37,CW*.17,CW*.24,CW*.22])
r.p('The counts in Figure 8 cover the complete implemented PL system, including the AXI interface, interconnect and reset logic. They should not be interpreted as the cost of the multiplier core alone. Use of one DSP block is consistent with mapping a 16-bit multiplication into dedicated arithmetic hardware. Overall device utilization remains below 1% for the listed resources.')
r.fig('section4_multiplier_serial_terminal.png', 'Figure 9. Multiplier UART test: input register 0x00020003 and result 0x00000006.', width=430)
r.p('The packed input represents a = 2 and b = 3. The returned value is 6, which matches 2 * 3. This is a successful directed board test for that input pair; the captured output does not establish exhaustive correctness or a performance advantage over software.')

# Page 8
r.new('4.3 AXI Divider Design')
r.p('The follow-up IP computes both quotient and remainder for two unsigned 16-bit operands. It uses restoring division and a 32-bit AXI4-Lite register interface at base address 0x43C00000. The divider is integrated into a separate hardware platform so that the multiplier and divider use the same base address in different systems.')
r.table(['Offset','Access','Definition'],[
    ['0x00','Read / write','a in bits [31:16]; b in bits [15:0]; a nonzero byte-strobe write starts an operation'],
    ['0x04','Read only','Unsigned quotient in bits [15:0]; upper bits are zero'],
    ['0x08','Read only','Unsigned remainder in bits [15:0]; upper bits are zero'],
    ['0x0C','Read only','bit 0 BUSY; bit 1 DONE; bit 2 DIVIDE_BY_ZERO']
], [CW*.13,CW*.19,CW*.68])
r.h('Arithmetic and completion')
r.p('For b &gt; 0, each cycle shifts the next dividend bit into a partial remainder, compares it with b, and conditionally subtracts b while generating one quotient bit. The partial remainder is 17 bits wide to retain the shift carry. After 16 iterations, the final outputs satisfy a = quotient * b + remainder and 0 &lt;= remainder &lt; b. At 100 MHz, the iteration phase takes 160 ns; software-visible latency additionally includes register accesses and polling.')
r.code('shifted = {r_work[15:0], q_work[15]};\nsubtract = shifted >= {1\'b0, divisor};\nnext_r = subtract ? shifted - {1\'b0, divisor} : shifted;\nnext_q = {q_work[14:0], subtract};', size=8.8, lang='verilog')
r.p('BUSY is asserted during a normal operation. DONE is retained until a new start or reset, and the output registers retain the previous completed result while the next operation is busy. Software polls until (status &amp; 0x3) == 0x2, then reads the quotient and remainder. A polling limit prevents an indefinite wait; the complete test application is in Appendix B.')
r.h('Interface handling and exceptional inputs')
r.p('The AXI write address and write data are buffered independently, so they can arrive on different cycles. Write byte strobes preserve bytes that are not enabled; an all-zero strobe does not start an operation. Read and write responses remain stable during backpressure. A write to the input register while BUSY, a write to an output register, or an invalid address produces SLVERR. Reset aborts an unfinished operation and clears registers and pending bus state.')
r.p('Division by zero is explicitly defined by this design: quotient = 0xFFFF, remainder = a and status = 0x6 (DONE and DIVIDE_BY_ZERO). This is an error indication, not a mathematical division result. The software checks this convention without executing C division or modulo with a zero divisor.')

# Page 9
r.new('4.4 Divider Build and Board Tests')
r.p('The divider application builds against platform_section4_divider and accesses the IP through its generated register driver. The Vitis console identifies hello_rtl_divider and reports a completed ELF build. The editor in Figure 10 still displays the multiplier starter file; the selected project and build console identify the divider application.')
r.fig('section4_divider_build.png', 'Figure 10. hello_rtl_divider application compilation completed successfully.', width=475)
r.fig('section4_divider_serial_terminal.png', 'Figure 11. Divider UART output: 11 tests and zero failures, including division-by-zero cases.', width=410)
r.p('The board test covers ordinary division, exact division, maximum 16-bit operands, dividend smaller than divisor, zero dividend and zero divisor. All 11 captured cases pass; the detailed values are summarized on the next page.', 'small')

# Page 10
r.new('4.5 Divider Verification and Implementation')
r.table(['a','b','Quotient','Remainder','Status'],[
    ['17','5','3','2','0x2'],['100','7','14','2','0x2'],
    ['65535','255','257','0','0x2'],['65535','1','65535','0','0x2'],
    ['65535','65535','1','0','0x2'],['3','7','0','3','0x2'],
    ['0','7','0','0','0x2'],['32768','3','10922','2','0x2'],
    ['12345','0','65535','12345','0x6'],['0','0','65535','0','0x6'],
    ['42','6','7','0','0x2']
], [CW*.18,CW*.18,CW*.23,CW*.23,CW*.18])
r.p('Table 1. Observed board results transcribed from Figure 11. The zero-divisor rows follow the error convention described in Section 4.3.', 'caption')
r.p('The XSim log records DIVIDER_SIMULATION_PASS for 272 arithmetic cases, including 256 random cases. The testbench also checks AW/W arrival skew, read/write backpressure, partial byte writes, zero strobes, read-only protection, unaligned reads, rejection while busy and reset during division. These simulation checks complement the 11 directed board tests. [4]', 'small')
r.table(['Resource','Entire divider PL system','Divider IP with AXI'],[
    ['LUTs','512 (0.96% of 53,200)','158'],
    ['Flip-flops','631 (0.59% of 106,400)','198'],
    ['DSP blocks','0','0'],['BRAM blocks','0','0']
], [CW*.27,CW*.43,CW*.30])
r.p('Table 2. Routed resource utilization and hierarchical IP counts from the Vivado reports. The iterative shift, compare and subtract implementation uses no DSP blocks or BRAM. The complete-system counts include infrastructure outside the divider IP. [4]', 'caption')
r.table(['Implemented timing metric','Reported result'],[
    ['Clock period / frequency','10.000 ns / 100.000 MHz'],
    ['WNS / WHS / WPWS','4.069 ns / 0.034 ns / 4.020 ns'],
    ['TNS / THS / TPWS','0.000 ns / 0.000 ns / 0.000 ns'],
    ['Failing endpoints','0 for setup, hold and pulse width']
], [CW*.48,CW*.52])
r.p('Table 3. Routed timing summary. All user-specified timing constraints are met. The reported margins apply to the constrained implementation; they are not a measured application speedup. [4]', 'caption')

# Page 11
r.new('6 Tcl Exercises')
r.p('The procedures below implement the three required exercises. avg accepts a list of numbers and returns a floating-point mean, rejecting an empty list. factorial accepts nonnegative integers, with factorial(0) = 1. two-fer has a default filename of main.c; its body is one line and does not use the args keyword. [1, p. 35]')
tcl_source = (SCRIPTS/'lab1_tcl_exercises.tcl').read_text(encoding='utf-8')
tcl_body = '\n'.join(line for line in tcl_source.splitlines() if not line.startswith('#'))
r.code(tcl_body.strip(), size=9, lang='tcl', compact=True)
r.table(['Invocation','Observed output'],[
    ['avg {70 80 50 60}','65.0'],['avg {1 2}','1.5'],
    ['factorial 3','6'],['factorial 0','1'],['factorial 10','3628800'],
    ['two-fer','C source: main.c'],['two-fer lab1-1.c','C source: lab1-1.c']
], [CW*.49,CW*.51])
validation = json.loads((METADATA/'lab1_tcl_validation.json').read_text(encoding='utf-8'))
r.p(f'The code was executed with Tcl {validation["tcl_version"]}. All 12 checks passed, including fractional and signed averages, a one-element list, and rejection of empty averages and invalid factorial inputs. The decimal output 65.0 is numerically equal to the manual example 65. The executable source is provided separately as scripts/lab1_tcl_exercises.tcl.', 'small')

# Page 12
r.new('7 Post Lab Questions')
r.h('7.1 What is a bare metal test')
r.p('A bare-metal test is a program that executes on the processor without a general-purpose operating system. Startup code initializes the execution environment, and the application accesses hardware through memory-mapped registers or board-support drivers. Our standalone Cortex-A9 applications use init_platform, GPIO or custom IP register accesses, and UART output to check basic system behavior. Successful ELF compilation alone is insufficient; the captured board output provides evidence that the application executes on the target.')
r.h('7.2 How the Zynq PS communicates with the IP blocks')
r.p('The Cortex-A9 issues memory-mapped reads and writes to addresses assigned in the Vivado design. The PS M_AXI_GP0 interface sends transactions through the AXI interconnect and protocol conversion logic to the appropriate AXI4-Lite peripheral. The GPIO drivers read button data and write LED data. For the arithmetic IPs, software writes packed operands at base + 0x00 and reads result registers. The divider also exposes a status register so software can wait for DONE before consuming results. UART output returns observations to the PC; it is separate from the PS-to-PL register interface.')
r.h('7.3 Main features of AXI')
r.p('AXI is part of Arm AMBA and provides standard interfaces between system components. AXI4 supports memory-mapped burst transfers, with up to 256 beats for incrementing bursts. AXI4-Lite uses single-beat memory-mapped transactions for control and status registers. AXI4-Stream carries a unidirectional stream without a memory address. AXI4 and AXI4-Lite separate read address (AR), read data (R), write address (AW), write data (W) and write response (B) into five channels. Each channel uses VALID/READY flow control: a transfer is accepted on a rising clock edge when both are asserted. This permits backpressure, and write address and data can arrive separately. Read and write paths can operate independently. The interconnect routes transactions by address and can adapt interface widths, clocks or protocols. In this lab, AXI4-Lite is suitable for the small GPIO and arithmetic register maps. [2]')
r.h('Conclusions')
r.p('The results establish basic standalone execution and UART communication, single-button GPIO mapping, one directed multiplier board result, and correct divider outputs for all captured board cases. Divider simulation additionally exercises arithmetic and interface corner cases, while implementation reports show positive timing margins at 100 MHz. The complete GPIO photograph sequence also confirms simultaneous button operation and that all user LEDs turn off when the buttons are released. No performance comparison with a software-only implementation was measured.')
r.h('References')
r.p('[1] ECE4810J Fall 2026 Lab 1 Manual, Arty Z7-20 version. Repository: Lab1/docs; requirements on pp. 17, 23, 35-36 and 38.', 'small')
r.p('[2] Xilinx, AXI Reference Guide, UG761 v13.1, 7 March 2011, Chapter 1 and Table 3-1. <link href="https://docs.amd.com/api/khub/documents/1_5L5rsU8PJY4UbkoGPAFg/content" color="#000000">Official AMD document</link>.', 'small', md='[2] Xilinx, AXI Reference Guide, UG761 v13.1, 7 March 2011. [Official AMD document](https://docs.amd.com/api/khub/documents/1_5L5rsU8PJY4UbkoGPAFg/content).')
r.p('[3] Repository implementation: pmod_app/src/main.c; rtl_multiplier_1.0; rtl_divider_1.0; section4/lab1-divider.c and tb_rtl_divider.sv, under Lab1.', 'small')
r.p('[4] Vivado and XSim records: section4_divider_utilization.txt, section4_divider_utilization_hierarchical.txt, section4_divider_timing.txt and section4_divider_simulation.txt, under Lab1/report/logs.', 'small')

# Page 13
r.new('Appendix A GPIO Application Code')
r.p('Source: Lab1/vitis_workspace/pmod_app/src/main.c. This is the application used for the Section 3 button-to-LED tests. Blank lines are compacted for layout; executable statements are unchanged.', 'small')
gpio_source = (LAB/'vitis_workspace/pmod_app/src/main.c').read_text(encoding='utf-8')
r.code(gpio_source, size=8.4, leading=10.4, lang='c', compact=True)
r.p('The 0xF mask retains only the four user-button bits. Because the full masked value is written on every loop iteration, simultaneous presses are represented by multiple set bits, and release of all buttons writes zero. No latch or software debounce is added.', 'small')

# Page 14
r.new('Appendix B Divider Application Code')
r.p('Source: Lab1/section4/lab1-divider.c. The application compares the hardware quotient, remainder and status with expected values and prints a total failure count. Blank lines are compacted for layout.', 'small')
divider_source = (LAB/'section4/lab1-divider.c').read_text(encoding='utf-8')
r.code(divider_source, size=7.8, leading=9.6, lang='c', compact=True)

r.finish()
