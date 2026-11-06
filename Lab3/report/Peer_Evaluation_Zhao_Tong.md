# Individual Peer Evaluation

**Evaluator:** Zhao Tong  
**Student ID:** 523370910137  
**Group:** 2

**Partner:** Yuan Haotong  
**Partner Student ID:** 523370910163

Complete this form independently. For each section, describe your own and your partner's actual work and assign each person an integer score from 0 to 5. Each student should submit their own completed evaluation.

| Part | Your work | Your partner's work | Your score (0-5) | Your partner's score (0-5) |
| --- | --- | --- | --- | --- |
| Section 2 | Reviewed the exported HLS reports, checked the reported performance and utilization figures against the stored screenshots, and assembled the section evidence | RGB-to-YCbCr kernel, C simulation and synthesis, the 2.4 answers, the comparison screenshots, the DATAFLOW experiment and the RTL export | 3 | 5 |
| Section 3 | Checked the five DCT solutions and their utilization evidence, confirmed output.dat and the recovered image, and packaged the deliverables | The five DCT solutions, memory utilization analysis, the five-way comparison report, dct.c, output.dat and the recovered image | 3 | 5 |
| Section 5 | Board work: SD image and board setup, ran lab3_1 / lab3_3 / resizer_pl / resizer_ps on the board, and took both LED photos | Exported lab3.bit / lab3.hwh, wrote the notebook skeletons, and packaged the lab3_pynq_test release | 5 | 3 |
| Board troubleshooting and debugging | Fixed the two faults that blocked the submission: traced the board's lost Internet access to a disabled IPv4 forwarding on the shared Ethernet adapter and repaired the sharing, and traced the failing partial-reconfiguration flow to the Vivado 2018.3 metadata that PYNQ 3.1 no longer parses (empty pr_dict, DefaultIP has no download method) and replaced it with a low-level partial bitstream download | Supplied the PR bitstreams and notebook skeletons, and reviewed the findings before they went into the report | 5 | 2 |
| Section 5.5 | Wrote both answers from the measured 247 ms (PL) and 1.1 s (PS) results, and completed BOARD_TEST_RECORD.md | Reviewed the answers and supplied the implementation data | 5 | 3 |
| Report and evidence | Published the executed notebooks, screenshots, LED photos and test record to the repository | Compiled the report, wrote the narrative and built the final PDF | 4 | 4 |

**Additional notes:** My partner covered the HLS/Vivado design and the report; I covered all board work, the on-board troubleshooting and the evidence. Sections 4 and 6 were not attempted by either of us.

**Evaluator signature (optional):** Zhao Tong  
**Date (optional):** 6 November 2026

Source: [Lab 3 Manual](../ECE4810J_FA2026_Lab_3_Manual_Arty_Z7-20.pdf). The two evaluators must complete their forms independently; submitting identical evaluation contents incurs a 3-point deduction from the lab total.
