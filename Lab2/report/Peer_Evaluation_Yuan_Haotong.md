# Individual Peer Evaluation

**Evaluator:** Yuan Haotong  
**Student ID:** 523370910163  
**Group:** 2

**Partner:** Zhao Tong  
**Partner Student ID:** 523370910137

Complete this form independently. For each section, describe your own and your partner's actual work and assign each person an integer score from 0 to 5. Each student should submit their own completed evaluation.

| Part | Your work | Your partner's work | Your score (0-5) | Your partner's score (0-5) |
| --- | --- | --- | --- | --- |
| Section 2 | Built the HLS multiplier and HLS ALU, ran C simulation, synthesis and co-simulation, implemented the combinational RTL ALU baseline, integrated both ALUs over AXI, finished the Vivado implementation, wrote the Vitis application and packaged the boot image | Flashed the boot image to the SD card, ran the board in SD mode and recorded the complete self-test output over the serial terminal | 5 | 4 |
| Section 3 | Assembled the boot image from FSBL, bitstream and application and validated its partition layout and checksum | Configured the boot mode jumper, exercised the interactive multiplier menu on hardware and produced the boot and multiplication captures | 5 | 4 |
| Section 4 | Wrote the PYNQ section text and checked the notebook output against the report claims; performed no board work here | Set up the PYNQ environment end to end: image writing, direct Ethernet connection, connection sharing, Jupyter login and the BaseOverlay notebook run, with address-bar evidence | 1 | 5 |
| Section 5 (optional) | Replaced the combinational RTL ALU with a pipelined version using a 32-stage restoring divider and a busy-stalling AXI wrapper, then closed setup and hold timing at 100 MHz | Verified the pipelined image on the board with signed arithmetic, divide-by-zero and overflow boundary cases | 5 | 4 |
| Section 6 | Researched and wrote all four post-lab answers and the conclusions | Provided the board measurements quoted in the resource and timing comparison, and checked them against the raw captures | 5 | 2 |
| Section 7 | Produced the compiled PDF, the submission evidence index and the final consistency review | Named and archived the screenshot set and the serial log, and pushed all board evidence to the group repository | 5 | 3 |

## Additional contribution notes

I was responsible for the complete hardware and software design flow in Sections 2, 3 and 5: HLS IP authoring and verification, the RTL baselines, AXI integration, implementation and timing closure, boot image packaging, and the report writing including every post-lab answer. My partner was responsible for all physical board work, which covered SD card writing, boot-mode setup, serial capture of the self-test and interactive tests, and the complete Section 4 PYNQ deployment from image flashing through Jupyter notebook execution. He also maintained the evidence repository. The split was deliberate: the design flow requires Vivado and Vitis, which were only available on my machine, while the board and network access were only available on his. Both of us reviewed the other's deliverables before the final submission.

**Evaluator signature (optional):** Yuan Haotong  
**Date (optional):** 23 October 2026

Source: [Lab 2 Manual, Appendix A](../docs/ECE4810J_FA2026_Lab_2_Manual_Arty_Z7-20.pdf). The two evaluators must complete their forms independently; submitting identical evaluation contents incurs a 3-point deduction from the lab total.
