# Individual Peer Evaluation

**Evaluator:** Zhao Tong  
**Student ID:** 523370910137  
**Group:** 2

**Partner:** Yuan Haotong  
**Partner Student ID:** 523370910163

Complete this form independently. For each section, describe your own and your partner's actual work and assign each person an integer score from 0 to 5. Each student should submit their own completed evaluation.

| Part | Your work | Your partner's work | Your score (0-5) | Your partner's score (0-5) |
| --- | --- | --- | --- | --- |
| Section 2 | Board-side testing: wrote the Lab 2 BOOT.BIN to the SD card, booted in SD mode and captured the full PuTTY session (100 multiplier pairs plus 7,509 cases for each ALU, all passing) as the on-hardware functional evidence | HLS multiplier and HLS ALU design, C simulation, synthesis and Verilog co-simulation, the combinational RTL ALU baseline, AXI integration, Vivado implementation, the Vitis application and BOOT.BIN packaging | 3 | 5 |
| Section 3 | Board-side testing: set JP4 to SD, verified the boot banner and menu, ran the interactive multiplication cases (2 x 3 and 65535 x 65535) and captured the screenshots | Boot image assembly and packaging of FSBL, bitstream and application, plus the partition and checksum validation of the released image | 5 | 3 |
| Section 4 | Completed the whole PYNQ exercise alone: wrote pynq_z1_v3.1.1.img to a 64 GB card with Rufus in DD mode, wired the board to the PC, enabled Internet Connection Sharing, reached Jupyter at 192.168.137.42:9090 and captured the login, file-browser and BaseOverlay notebook screenshots | No hardware work in this section; contributed the written description and caveats in the report | 5 | 3 |
| Section 5 (optional) | Board-side verification of the pipelined design: signed MUL/DIV/REM cases, divide-by-zero and INT_MIN / -1 boundary cases, all captured from the running SD image | Designed rtl_pipe_alu with a 32-stage restoring divider, the AXI wrapper with busy stalling, integrated it in place of the combinational IP and closed timing at 100 MHz | 3 | 5 |
| Section 6 | Supplied the measured board data used in the answers (routed hierarchical counts, timing margins, serial evidence) and reviewed the numbers against my own captures | Wrote all four post-lab answers and the conclusions section | 3 | 5 |
| Section 7 | Named, organized and committed all board screenshots and the serial log to the group repository under Lab2/report | Compiled the final PDF report, built the evidence index and cross-checked every figure reference | 3 | 5 |


## Additional contribution notes

My partner owned the Vivado, Vitis and Vitis HLS pipeline for Sections 2, 3 and 5, including the HLS multiplier, both ALUs, the pipelined RTL replacement, bitstream generation and boot image packaging, and wrote the report body and all post-lab answers. I owned every hardware-facing task: SD card preparation, boot-mode setup, all serial captures, the interactive and boundary tests on the board, and the entire Section 4 PYNQ bring-up (image writing, network sharing, Jupyter access and notebook execution). I also organized and published the board evidence to the group repository. My partner did not take part in the PYNQ hardware work, and I did not write the post-lab answers; each of us reviewed the other's output before submission.

**Evaluator signature (optional):** Zhao Tong  
**Date (optional):** 23 October 2026

Source: [Lab 2 Manual, Appendix A](../docs/ECE4810J_FA2026_Lab_2_Manual_Arty_Z7-20.pdf). The two evaluators must complete their forms independently; submitting identical evaluation contents incurs a 3-point deduction from the lab total.
