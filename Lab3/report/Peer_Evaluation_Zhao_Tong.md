# Individual Peer Evaluation

**Evaluator:** Zhao Tong  
**Student ID:** 523370910137  
**Group:** 2

**Partner:** Yuan Haotong  
**Partner Student ID:** 523370910163

Complete this form independently. For each section, describe your own and your partner's actual work and assign each person an integer score from 0 to 5. Each student should submit their own completed evaluation.

| Part | Your work | Your partner's work | Your score (0-5) | Your partner's score (0-5) |
| --- | --- | --- | --- | --- |
| Section 2 (35%) | Verification and evidence role: I was not the author of the HLS kernel, but I went through the exported Vitis HLS reports, confirmed that every performance and utilization number quoted in the report matches the stored Comparison and Synthesis Details screenshots, checked that the DATAFLOW experiment and the RTL export were actually produced, and assembled the Section 2 evidence set before submission | RGB-to-YCbCr HLS kernel, the Section 2.4 answers, the Performance/Utilization comparison screenshots, the DATAFLOW directive experiment and the optional RTL export | 3 | 5 |
| Section 3 (35%) | Verification and evidence role: checked that all five DCT solutions exist and produce consistent numbers, matched the memory utilization screenshot to the claim in the report, confirmed that the modified dct.c regenerates output.dat and the recovered image, and packaged this evidence for submission | The five 8x8 DCT solutions, the memory utilization analysis, the comparison report across all five solutions, the modified dct.c and the generated output.dat and recovered image | 3 | 5 |
| Section 5.1 - 5.4 (30%) | All on-board work and the debugging that made it run: wrote the PYNQ 3.1.1 image to a 64 GB SD card, fixed the Windows ICS forwarding so the board could reach PyPI, ran lab3_1 / lab3_3 / resizer_pl / resizer_ps on the board, found that the supplied PR flow could not work on PYNQ 3.1 (empty pr_dict, DefaultIP has no download method) and replaced it with a low-level partial bitstream download, took the two LED photos (0x5 and 0xA), and committed every screenshot to Lab3/report | Provided the exported lab3.bit / lab3.hwh, the notebook skeletons and the repository structure, and packaged the lab3_pynq_test release that supplied all artefacts | 5 | 3 |
| Section 5.5 and board test record | Wrote the two answers using the measured PL 247 ms vs PS 1.1 s figures and filled in Lab3/tests/BOARD_TEST_RECORD.md, including the root cause and the fix for both the partial-reconfiguration and the network problem | Reviewed the answers and the record, and supplied the implementation data used in the comparison | 5 | 3 |
| Report and evidence integration | Named, organised and published all Lab3 board evidence (executed notebooks, screenshots, LED photos, test record) and kept the evidence index and figure references in step with the report | Compiled the Lab3 report, wrote the narrative for Sections 2, 3 and 5 and built the final PDF | 4 | 4 |

## Additional contribution notes

The work split along a design/verification line. My partner owned the Vitis HLS and Vivado pipeline in Sections 2 and 3 (70% of the lab), produced the exported bitstream and the notebook skeletons used in Section 5, and wrote the report body. I owned every hardware-facing task in Section 5, including the two problems that had to be solved before anything could be submitted: the failure of the supplied partial-reconfiguration flow on PYNQ 3.1, which I diagnosed and replaced with a low-level partial bitstream download, and the Windows Internet Connection Sharing fault that kept the board offline. I also reviewed the Sections 2 and 3 deliverables against the stored evidence and did the board-side captures, the 5.5 answers and the board test record. Sections 4 and 6 (the optional IDCT and FIR extensions) were attempted by neither of us and are therefore not scored above. Each of us reviewed the other's output before submission.

**Evaluator signature (optional):** Zhao Tong  
**Date (optional):** 6 November 2026

Source: [Lab 3 Manual](../ECE4810J_FA2026_Lab_3_Manual_Arty_Z7-20.pdf). The two evaluators must complete their forms independently; submitting identical evaluation contents incurs a 3-point deduction from the lab total.
