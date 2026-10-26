"""Write the report from actual XML summaries and verified build evidence."""
from pathlib import Path
import html
import json
import shutil
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from PIL import Image as PILImage

LAB=Path(__file__).resolve().parents[1]
OUT=LAB.parent/'output/pdf/Lab3_Report.pdf'
M=json.loads((LAB/'report/hls_metrics.json').read_text())
REF=json.loads((LAB/'logs/reference_metrics.json').read_text())
BOOT=json.loads((LAB/'boot/manifest.json').read_text())
styles=getSampleStyleSheet()
styles['Normal'].fontName='Helvetica'
styles['Normal'].fontSize=9.5
styles['Normal'].leading=14
styles['Normal'].spaceAfter=8
styles['Heading1'].fontSize=18
styles['Heading1'].spaceAfter=12
styles['Heading2'].fontSize=12
styles['Heading2'].spaceBefore=10
styles['Heading2'].spaceAfter=8
styles.add(ParagraphStyle(name='Cell',fontName='Helvetica',fontSize=7.8,leading=10,spaceAfter=0))
styles.add(ParagraphStyle(name='Caption',fontName='Helvetica-Oblique',fontSize=8,leading=11,spaceAfter=10,textColor=colors.HexColor('#42546a')))
story=[];md=[]
def p(text):
    md.append(text+'\n')
    story.append(Paragraph(html.escape(text),styles['Normal']))
def h(text,level=1):
    md.append('#'*level+' '+text+'\n')
    story.append(Paragraph(html.escape(text),styles['Heading1' if level==1 else 'Heading2']))
def table(head,rows,widths=None):
    md.append('| '+' | '.join(head)+' |\n| '+' | '.join(['---']*len(head))+' |')
    for row in rows:md.append('| '+' | '.join(map(str,row))+' |')
    md.append('')
    data=[[Paragraph(html.escape(str(x)),styles['Cell']) for x in row] for row in [head,*rows]]
    if widths:
        scale=539/sum(widths)
        widths=[w*scale for w in widths]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dbe6f1')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f6f9')]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#bcc9d5')),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.extend([t,Spacer(1,10)])
def compare(family):
    rows=[]
    for sol,m in M[family].items():
        rows.append([sol,m['clock_ns'],m['latency_max'],m['interval_max'],m['BRAM_18K'],m['DSP'],m['FF'],m['LUT']])
    table(['Solution','Clock ns','Max cycles','Interval','BRAM18','DSP','FF','LUT'],rows,[112,49,64,58,48,38,49,49])
def page():story.append(PageBreak())
def picture(path,caption,width=470):
    width=min(width,539)
    iw,ih=PILImage.open(path).size
    story.append(Image(str(path),width=width,height=width*ih/iw))
    story.append(Paragraph(html.escape(caption),styles['Caption']))
    rel=Path(__import__('os').path.relpath(path,LAB/'report')).as_posix()
    md.append(f'![{caption}]({rel})\n')

h('ECE4810J - Lab 3')
p('PYNQ Overlays and Optimizing HLS Performance through Pipelining | Arty Z7-20 | 26 October 2026')
p('This report records completed offline implementation and measured tool results. No physical board was available. SD boot, live PYNQ outputs and board photographs remain pending. The user requested a BOOT.BIN for subsequent board testing.')
table(['Item','Completed evidence'],[
    ['Tools and target','Vivado / Vitis / Vitis HLS 2022.1; xc7z020clg400-1; 10 ns target clock'],
    ['Section 2','RGB/YUV conversion; independent reference; five synthesis runs; actual HLS screenshots'],
    ['Section 3','Five DCT solutions; IDCT; 323-block tests; RTL cosimulation; full image recovery'],
    ['Section 5','Answers and board notebooks prepared; full custom Arty overlay built; board execution pending'],
    ['Optional Section 6','128-tap FIR; baseline and pipelined synthesis; golden test; RTL test; host notebook'],
    ['Board image','Matching FSBL, routed bitstream and ARM self-test application packaged and validated']],[110,457])
h('2.4 - Baseline function metrics',2)
rows=[]
for name,m in M['yuv_baseline_functions'].items():
    rows.append([name,m['clock_ns'],m['latency_max'],m['DSP'],m['BRAM_18K'],m['FF'],m['LUT']])
table(['Function','Clock ns','Worst cycles','DSP','BRAM18','FF','LUT'],rows,[119,61,87,45,65,55,45])
p('TRIPCOUNT affects reporting only. Before adding it, variable-loop latencies are undefined. With the directives, worst-case yuv_filter latency is 4,721,669 cycles. Its hardware resources are unchanged: 768 BRAM18, 7 DSP, 536 FF and 1,247 LUT. yuv_scale is automatically inlined and has no separate baseline function report.')
p('The supplied image_t contains 512 x 512 pixels, so the study uses trip counts 200..512 in each dimension. The manual uses a generic 1920 x 1280 example. These different array sizes and estimates are explicitly distinguished; no sample report values were copied.')
page()
h('2.5-2.6 - YUV optimization')
compare('yuv')
p('solution1 explicitly disables automatic pipelining. solution2 disables inlining of all three processing stages and pipelines the innermost loops with II=1. Its worst-case latency drops from 4,721,669 to 786,473 cycles, approximately a sixfold reduction, while DSP, FF and LUT usage increases.')
p('DATAFLOW with default ping-pong buffers permits overlap across frames. solution3_pipo has nearly the same single-frame latency as solution2, but its interval drops to 262,158 cycles. Whole-frame double buffering raises BRAM18 usage from 768 to 1,536. Both configurations exceed the device capacity of 280 BRAM18 and are synthesis studies only.')
p('The FIFO configuration uses default_channel=fifo and fifo_depth=2. Since accesses are sequential, stages can overlap within a frame. Worst-case latency becomes 262,166 cycles and BRAM18 usage becomes zero. The estimated clock period changes to 7.268 ns. In this run FF and LUT counts increase relative to PIPO, so the manual example claim that all resource types fall is not reproduced. The measured memory reduction is the main benefit.')
p('RGB-to-YUV uses the integer BT.601 studio-range coefficients in the manual. The inverse subtracts 16/128/128 before applying 298/409, 298/-100/-208 and 298/516 coefficients, then clips to 0..255. Conversion uses signed integer intermediates; YUV scaling preserves the starter shift-by-seven behavior for factors 0..128.')
p('The input and output files consistently store RGB triples in raster order: row y, column x, then R/G/B. The starter image_read used the opposite nesting from image_write; this was corrected and tested against a separately generated NumPy reference.')
p('Validation: 4,413,096 channel values pass in native C and HLS C simulation. Tests include the full 512 x 512 image, 1 x 1, 7 x 11 and 200 x 200 dimensions, unity/zero/mixed scales. YUV optimized variants were synthesized; no YUV RTL cosimulation or YUV implementation claim is made.')
picture(LAB/'images/lena_yuv_recovered.png','Figure 1. Actual native C output after unity-scale RGB/YUV/RGB conversion.',210)
page()
h('3.4-3.7 - DCT architecture study')
compare('dct')
p('Section 3.4 Step 4 metrics are the solution1 row: estimated clock 6.508 ns, worst latency 2,450 cycles, 2 DSP, 5 BRAM18, 515 FF and 1,493 LUT. The innermost DCT accumulation loop is explicitly pipelined; the read/write/transpose loops are also pipelined.')
p('solution2 removes the explicit inner-loop pipeline and lets Vitis pipeline the outer DCT loop. The inner multiply loop is unrolled, increasing coefficient access demand. Automatic coefficient ROM partitioning and additional arithmetic reduce latency to 422 cycles, using 16 DSP and 17 BRAM18.')
p('solution3 completely partitions dimension 2 of buf_2d_in and col_inbuf. The increased read bandwidth permits more parallel operations and reduces latency to 360 cycles. Vitis additionally parallelizes row computations; the actual DSP count rises to 96. The memory detail report shows eight banks of each partitioned input buffer. Each small bank uses 16 FF and 2 LUT instead of BRAM.')
p('solution4 adds top-level DATAFLOW. Read, dct_2d and write overlap, with interval 224 cycles and latency 358 cycles. solution5 inlines dct_2d, exposing six dataflow processes. Its interval is 68 cycles and latency is 354 cycles. More ping-pong channels raise BRAM18 from 3 to 5. Top-level latency and initiation interval describe different aspects of performance.')
p('Verilog cosimulation passes solution1 and solution5 against 323 independently generated blocks. The test includes zero, all-255, the Lena corner, all 64 impulse positions and 256 deterministic random blocks. For solution5, the RTL report measures latency 342..451 cycles and interval 65..66 cycles. These simulation values differ from static estimates because of dataflow startup and stalls.')
p('The full board image uses a separate compact AXI DCT/IDCT wrapper with pipelined inner loops. The five study solutions remain available for comparison; their high-throughput resource counts must not be confused with the final compact board system.')
page()
h('3.9 - Fixed-point inverse DCT')
p('The orthonormal basis is T[k,n] = alpha(k) cos(pi (2n+1) k /16), with alpha(0)=1/sqrt(8) and alpha(k>0)=1/2. The generated coefficient table C is round(T * 2^14.5). Each forward 1D pass computes (C*x + 4096) >> 13. Thus two forward passes produce approximately eight times the orthonormal 2D DCT.')
p('The inverse must compensate for this scale: each 1D inverse pass uses C-transpose and an arithmetic shift right by 16. This follows the manual sample, which floors each pass rather than adding a rounding bias. Applying the forward shift of 13 to the inverse would produce an incorrectly scaled image.')
p('The implementation adds idct_1d, idct_2d and idct. The required output.dat contains the 64 recovered pixels of the Lena corner. dct.golden.dat contains forward coefficients and idct.golden.dat contains the independent inverse reference. The test fails on any mismatch in either transform.')
p(f'Native C and independent NumPy models agree for all 41,344 checked transform values. Full-image C processing executes all 4,096 blocks. Compared with the original Lena image, maximum absolute error is {REF["idct_full_image_max_error"]}, MSE is {REF["idct_full_image_mse"]:.8f}, and PSNR is 50.53323 dB. These are algorithm results, not measurements from a board.')
picture(LAB/'images/lena_idct_recovered.png','Figure 2. Full 512 x 512 image recovered by executing the actual C DCT/IDCT block functions.',240)
page()
h('5 - Overlays and board work')
h('5.5.1 - Advantages of overlays',2)
p('An overlay packages FPGA hardware as a reusable library with discoverable metadata and Python drivers. Application developers can call accelerated functions from Python, reuse IP across applications, and reconfigure hardware at runtime. Matching HWH metadata exposes IP names, addresses and registers, reducing dependence on handwritten address constants. Partial reconfiguration can change one supported region while retaining the static design.')
h('5.5.2 - Software versus acceleration',2)
p('Software offers rapid iteration and flexible control flow with low setup cost. Hardware is attractive for regular, parallel, compute-intensive kernels or sustained streaming workloads, where deterministic timing and throughput matter. The choice should consider end-to-end latency, data transfer and launch overhead, batch size, arithmetic precision, BRAM/DSP budget, power, engineering effort and reuse. A small scalar operation may be slower over AXI than on the CPU. The FIR notebook measures host elapsed time, including register transfers, rather than treating HLS kernel cycles as application speedup.')
table(['Section','Prepared','Evidence still needed'],[
    ['5.1','lab3_1.ipynb','Execute BaseOverlay discovery and LED toggle; save real outputs'],
    ['5.2','lab3_2.ipynb with file checks','Arty-specific PR full/partial designs; execute both configurations; two board photographs'],
    ['5.3','Procedure in ON_BOARD.md','Compatible Arty PYNQ/HelloWorld image; run original resizer notebooks; screenshots and measured timing'],
    ['5.4','lab3_3.ipynb; custom Arty bit/hwh','Execute register and AddDriver checks, yielding 7, 9 and 35; save outputs']],[45,170,352])
p('The manual points to a PYNQ-Z1 partial-reconfiguration example. A common FPGA part does not make bitstreams board-compatible: pin constraints and PS/DDR configuration also matter. This delivery does not include Arty PR bitstreams. The prepared PR notebook stops until board-matched files are supplied. The full lab3 overlay is not a partial-reconfiguration design.')
p('All notebooks are intentionally unexecuted. No board photos, fabricated PYNQ results or synthetic notebook outputs are supplied. BOOT.BIN runs a bare-metal test program; Jupyter requires a separate PYNQ Linux image.')
page()
h('6 - Optional 128-tap FIR')
compare('fir')
p('The FIR implements y[n] = sum(c[k] x[n-k]) for the supplied 128 coefficients. History is initialized to zero and an explicit clear operation supports repeatable board tests. The baseline shares one multiplier and performs the shift/accumulate loop sequentially. Pipelining that loop reduces core latency from 636 to 134 cycles, while increasing FF from 313 to 385 and LUT from 266 to 332; DSP and BRAM18 remain unchanged.')
p('All 600 samples of the provided out.gold.dat match the C implementation exactly. The AXI wrapper passes 1,024 deterministic signed input samples and a midstream history clear in C/RTL cosimulation. host_fir.ipynb loads the full Arty overlay, waits for ap_done with a timeout, validates hardware samples against NumPy convolution, saves board data and plots the input/output. Its results and plots require the board.')
h('SD boot deliverable and validation',2)
table(['Peripheral','Base','Register layout'],[
    ['dct_accel_0','0x43C00000','+0x00 control; +0x10 inverse; +0x100 input; +0x200 output (32-bit words)'],
    ['fir_accel_0','0x43C10000','+0x00 control; +0x10 sample; +0x18 clear; +0x20 result'],
    ['scalar_add','0x43C20000','+0x10 A; +0x18 B; +0x20 C; ap_ctrl_none']],[100,85,382])
p('The ARM application automatically checks 36 add vectors, 323 DCT/IDCT blocks and 1,024 FIR samples. UART commands t, d and f rerun tests, print the Lena block and dump FIR CSV respectively. DCT/FIR completion waits have a one-second timeout. The actual generated HLS register headers and XSA-derived BSP are used to compile the application.')
p('Routed system at 100 MHz: WNS +3.387 ns, WHS +0.044 ns; all timing constraints met. Utilization is 1,650 LUT, 1,873 FF, 6 DSP and 7 BRAM36 tiles. The hardware inherits Lab 1 Arty PS/DDR/UART settings; inherited negative DDR DQS delay warnings still require physical DDR initialization testing.')
p(f'BOOT.BIN size: {BOOT["image"]["bytes"]:,} bytes. Validation checks boot and partition headers, ARM ELF load segments, the PL payload byte swap and the XSA-embedded bitstream. SHA-256: {BOOT["image"]["sha256"]}')
p('The application compiles with -Wall -Wextra -Werror. Build, timing, simulation, boot validation and input hashes are preserved in logs/ and boot/manifest.json. Physical SD boot remains unverified.')
page()
h('Reproduction and evidence index')
p('Run scripts/build_all.ps1 from the repository root using the installed D:/Xilinx 2022.1 tools. Python requires NumPy and Pillow. The script generates independent data, tests native implementations, builds all HLS studies and AXI IP, tests the add AXI RTL, builds Vivado hardware, generates the BSP/FSBL/application and validates the boot image. Lab 1 is required as the inherited board configuration source.')
p('For software-only changes, use -SkipHls -SkipHardware. To repack already-built inputs, use scripts/build_boot.ps1. scripts/summarize_reports.py extracts metrics from actual Vitis XML. screenshots/ contains original GUI captures; the following appendix reproduces them without replacing values or drawing substitute tool interfaces.')
p('Vitis 2022.1 autogenerated cosimulation of the ap_ctrl_none add IP fails because its generated testbench references ap_done. The delivered add core is instead checked by tests/test_add_axi.v, which drives the real AXI interface, separates AW/W arrival and verifies all 36 vectors. DCT and FIR use normal HLS Verilog cosimulation and pass.')
p('Vivado can create a nonempty D:/dev/null text file on Windows; HLS make then attempts to include it. The rebuild helper preserves and clears this file only if its content matches the known [Patcher] log format. It stops for unrecognized content. The delivered synthesis and simulation evidence is retained independently of this environment workaround.')
table(['Required output','Location'],[
    ['Section 2 comparisons and answers','report/yuv_comparison.csv; report/hls_metrics.json; screenshots/yuv_*.jpg'],
    ['Section 3 comparisons and memory','report/dct_comparison.csv; screenshots/dct_*.jpg'],
    ['Section 3.9 code and output','lab3_starter/dct/dct.c and output.dat'],
    ['Recovered images','images/lena_yuv_recovered.png; images/lena_idct_recovered.png'],
    ['Notebook sources','notebooks/lab3_1.ipynb; lab3_2.ipynb; lab3_3.ipynb; host_fir.ipynb'],
    ['Board test image and metadata','boot/BOOT.BIN; boot/manifest.json; exported/lab3.bit and lab3.hwh'],
    ['Real simulation evidence','logs/native_verification.txt; logs/cosim/; logs/add_axi_simulation.txt'],
    ['Timing and boot validation','logs/timing.txt; logs/utilization.txt; logs/boot_validation.txt']],[160,407])
p('Primary references: the provided ECE4810J Fall 2026 Lab 3 Arty manual, sections 2, 3, 5 and 6; official PYNQ 2.7 Overlay Tutorial at https://pynq.readthedocs.io/en/v2.7.0/overlay_design_methodology/overlay_tutorial.html; Xilinx/PYNQ-HelloWorld repository; yunqu/partial_reconfig_example repository linked by the manual. PYNQ execution details must be checked against the installed board image.')
for filename,caption in [
    ('yuv_all_comparison.jpg','A1. Actual HLS comparison of baseline, pipelined, PIPO and FIFO YUV solutions.'),
    ('yuv_pipo_details.jpg','A2. Actual DATAFLOW synthesis details with full-frame ping-pong buffers.'),
    ('yuv_fifo_details.jpg','A3. Actual DATAFLOW synthesis details with FIFO channels.'),
    ('dct_five_solutions.jpg','A4. Actual HLS report comparison for all five DCT solutions.'),
    ('dct_partition_memory.jpg','A5. Actual solution3 memory detail after complete partitioning.')]:
    page();h('Appendix - HLS GUI evidence');picture(LAB/'report/screenshots'/filename,caption,567)

def footer(canvas,doc):
    canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#566779'))
    canvas.drawString(34,25,'ECE4810J Lab 3 | Offline evidence; physical board tests pending')
    canvas.drawRightString(A4[0]-34,25,str(doc.page));canvas.restoreState()

OUT.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=28,leftMargin=28,topMargin=30,bottomMargin=42,
    title='ECE4810J Lab 3 - Arty Z7-20',author='Lab 3 implementation')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(LAB/'report/Lab3_Report.md').write_text('\n'.join(md),encoding='utf-8')
shutil.copyfile(OUT,LAB/'report/Lab3_Report.pdf')
print(OUT)
