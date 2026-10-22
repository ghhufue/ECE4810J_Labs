# Lab 2 开发工具截图索引

这里的 JPG 均直接保存自真实 HLS、Vivado 或 Vitis 窗口；保留截图工具返回的原始 JPEG 字节，未修改图中内容。

## 使用方式

- 图片文件位于 `images/`，可按下表的用途插入报告；英文图注为建议文案。
- 红色代表 RTL 叶单元，黄色代表对应的 HLS 叶单元；网表图标也显示颜色。
- `baseline_` 图片来自独立的组合版工程；`vivado_` 图片来自发布镜像的流水线版工程。两套系统均包含相同的 HLS ALU、两种乘法器和 PS/AXI 配置。
- ALU 局部放大图是补充图，配合完整 Device 图使用。
- Vitis 截图是实际 IDE Debug 构建（`-O0`）；已发布 BIN 的应用使用 `-O2` 构建。两者使用相同应用源码。截图后已恢复发布版 ELF，并重新核对 BIN 中的载荷。
- 本文件夹不含串口、SD 实物或 PYNQ 截图，这些仍需在开发板上采集。

## 图片与建议图注

| 图片 | 报告用途 | Suggested caption |
| --- | --- | --- |
| [hls_alu_csimulation_pass.jpg](images/hls_alu_csimulation_pass.jpg) | Section 2：C 仿真 | HLS ALU C simulation: all 18 operations tested; 7509 vectors passed. |
| [hls_alu_synthesis_summary.jpg](images/hls_alu_synthesis_summary.jpg) | Section 2：HLS 综合时序和资源 | HLS ALU synthesis summary for xc7z020clg400-1 with a 10 ns clock target. |
| [hls_alu_cosimulation_pass.jpg](images/hls_alu_cosimulation_pass.jpg) | Section 2：C/RTL 协同仿真 | HLS ALU C/RTL co-simulation completed with Pass status using Vivado XSIM. |
| [vivado_multipliers_highlighted.jpg](images/vivado_multipliers_highlighted.jpg) | Section 2：乘法器实现图 | Implemented RTL multiplier (red) and HLS multiplier (yellow) leaf cells. |
| [vivado_alus_highlighted.jpg](images/vivado_alus_highlighted.jpg) | Section 5：流水线 ALU 实现图 | Implemented pipelined RTL ALU (red) and HLS ALU (yellow) leaf cells. |
| [vivado_alus_highlighted_detail.jpg](images/vivado_alus_highlighted_detail.jpg) | 流水线 ALU 局部放大补充图 | Detail of the pipelined RTL ALU (red) and HLS ALU (yellow); use with the full-device view. |
| [vivado_utilization_summary.jpg](images/vivado_utilization_summary.jpg) | 流水线版：资源汇总 | Post-route utilization of the system used by the released boot image. |
| [vivado_design_timing_summary.jpg](images/vivado_design_timing_summary.jpg) | 流水线版：时序汇总 | Post-route timing at 100 MHz: setup WNS 1.979 ns and hold WHS 0.013 ns; all constraints met. |
| [vitis_alu_build_finished.jpg](images/vitis_alu_build_finished.jpg) | Section 2：Vitis IDE 编译完成 | Vitis IDE successfully compiled and linked hello_hls_rtl_alu from the application sources. |
| [baseline_alus_highlighted.jpg](images/baseline_alus_highlighted.jpg) | Section 2：组合 ALU 实现图 | Implemented combinational RTL ALU (red) and HLS ALU (yellow) leaf cells in the separate baseline project. |
| [baseline_utilization_summary.jpg](images/baseline_utilization_summary.jpg) | 组合版：资源汇总 | Post-route utilization of the combinational RTL ALU baseline system. |
| [baseline_design_timing_summary.jpg](images/baseline_design_timing_summary.jpg) | 组合版：时序汇总 | Post-route timing of the combinational RTL ALU baseline at the same 100 MHz target. |

## 同一 100 MHz 目标下的实现对比

以下为整个 PL 系统的布局布线后数据，非单个 ALU 的资源数。

| 指标 | 组合版基线 | 发布镜像的流水线版 |
| --- | ---: | ---: |
| LUT | 5032 | 4414 |
| FF | 2339 | 6598 |
| DSP | 10 | 10 |
| Setup WNS (ns) | -87.707 | +1.979 |
| Hold WHS (ns) | +0.012 | +0.013 |
| 时序约束 | 未满足 | 全部满足 |

## 工程与证据

- 流水线版工程：`Lab2/vivado/lab2/lab2.xpr`；[资源报告](evidence/utilization.txt)、[时序报告](evidence/timing.txt)。
- 组合版工程：`Lab2/vivado/lab2_baseline/lab2_baseline.xpr`；[资源报告](evidence/baseline_utilization.txt)、[时序报告](evidence/baseline_timing.txt)。
- [Vitis 实际构建日志](evidence/vitis_ide_build.txt)。
- [发布镜像一致性核对](evidence/boot_validation.txt)。
- HLS 原始仿真、综合日志也位于 `evidence/`。
- 软件界面构建是编译证据，上板成功与否需以实际串口结果判断。
