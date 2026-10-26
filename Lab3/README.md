# Lab 3 - Arty Z7-20 上板测试包

发布版快速使用说明见 `QUICK_START.md`；完整测试顺序、逐项预期数据、截图清单和故障定位见 `ON_BOARD.md`。空白测试记录表位于 `tests/BOARD_TEST_RECORD.md`。

已生成 **`boot/BOOT.BIN`**（FSBL + PL bitstream + ARM 裸机应用）。目标为 **Arty Z7-20 / xc7z020clg400-1**，工具版本 Vivado / Vitis / Vitis HLS 2022.1，PL 时钟 100 MHz。

## SD 卡启动

1. 将 `boot/BOOT.BIN` 复制到 FAT32 格式 SD 卡根目录，保持文件名 `BOOT.BIN`。
2. 开发板断电，将 Arty Z7-20 的 JP4 设为 **SD** 启动，插入 SD 卡。
3. 连接板载 USB UART，串口设为 **115200、8N1、无流控**。
4. 上电或复位。程序自动运行 ADD、DCT/IDCT 和 FIR 自检。
5. 如果错过启动输出，输入 `t` 重跑。命令可直接输入一个字母；回车和换行不会触发测试。

以下是**预期串口输出，尚未在实物上验证**：

```text
ECE4810J LAB3 | Arty Z7-20 | PL 100 MHz
ADD RESULT: 36 tests, 0 failures
DCT/IDCT RESULT: 323 blocks, 41344 values, 0 failures
FIR RESULT: 1024 samples, 0 failures
LAB3 SELF-TEST: PASS
Menu: t=self-test, d=Lena block, f=FIR CSV
```

| 命令 | 功能 |
| --- | --- |
| `t` | 重跑全部测试，逐项输出失败数量 |
| `d` | 打印 Lena 左上角 8×8 原始像素、DCT 系数和 IDCT 恢复结果 |
| `f` | 输出 1024 行 FIR CSV，位于 `FIR_CSV_BEGIN` 与 `FIR_CSV_END` 之间 |

FIR 自检会在样本 512 处清空历史，验证复位后行为。所有等待 `ap_done` 的操作有约 1 秒超时提示。

## 实现与验证

| AXI 外设 | 基地址 | 说明 |
| --- | --- | --- |
| `dct_accel_0` | `0x43C00000` | 8×8 定点 DCT/IDCT；`+0x10` 模式，`+0x100` 输入，`+0x200` 输出；数组每项 32 位，内核使用 16 位数值 |
| `fir_accel_0` | `0x43C10000` | 128 阶 FIR；`+0x10` 输入，`+0x18` 清历史，`+0x20` 输出 |
| `scalar_add` | `0x43C20000` | 无符号 32 位加法，模 2^32；`+0x10` A，`+0x18` B，`+0x20` C；无需写启动位 |

DCT/FIR 的 `+0x00` 为控制寄存器：写 1 启动，轮询 bit 1 完成后再读输出。软件使用导出 IP 的实际寄存器头文件及本次 XSA 生成的 BSP。

已完成的离线验证：

- YUV：4,413,096 个通道值，0 失败；含原图、不同尺寸与缩放因子。
- DCT/IDCT：323 块、41,344 个值，独立 NumPy 定点模型与 C 实现一致；AXI 内核 C/RTL 协同仿真通过。
- 全幅 Lena：实际 C 程序执行 4096 个块，恢复结果与独立模型逐像素一致，最大误差 2，PSNR 50.53323 dB。
- FIR：600 个原始 golden 样本匹配；AXI 内核通过 1024 样本及中途清历史的 C/RTL 校验。
- ADD：36 组 native/HLS C 测试及独立 AXI RTL 仿真通过，包含先地址后数据的写事务。
- 100 MHz 布局布线通过：WNS **+3.387 ns**，WHS **+0.044 ns**；1,650 LUT、1,873 FF、6 DSP、7 BRAM36 tile。
- ARM 程序以 `-Wall -Wextra -Werror` 编译通过；启动头、分区头、ELF 载荷、bitstream 载荷和 XSA 内嵌 bitstream 校验通过。

`logs/` 保留实际验证证据，`boot/manifest.json` 记录构建输入哈希。板卡当前不可用，**实际 SD 启动、DDR 初始化、串口输出和硬件执行待测**。PS/DDR/UART 沿用 Lab 1 的 Arty 配置；Vivado 仍报告继承配置中的 DQS delay 负值提示，需实物确认 DDR 初始化。

## 实验报告与 PYNQ

- `report/Lab3_Report.md` 与 PDF：真实 HLS 综合指标、实验问题回答、GUI 截图和待补项目。
- `lab3_starter/dct/output.dat`：手册 Section 3.9 要求的 **IDCT 恢复值**，64 行；`dct.golden.dat` 为前向参考，名称不同。
- `images/`：YUV 和全图 IDCT 的恢复图。
- `notebooks/lab3_1.ipynb`、`lab3_2.ipynb`、`lab3_3.ipynb`：Section 5；`host_dct.ipynb`、`host_fir.ipynb`：自建 IP 的上板校验。
- `exported/lab3.bit` 与同名 `lab3.hwh`：适用于此 Arty 的完整 PYNQ overlay。

裸机 `BOOT.BIN` 不含 PYNQ Linux/Jupyter。运行 Notebook 时，使用另一张已安装 Arty PYNQ 系统的 SD 卡，将 `notebooks/` 与 `exported/` 保持相邻后复制上板。Notebook 没有伪造输出；上板后 Run All 并保存。

Section 5.2 的局部重配置必须使用 **Arty 专用**的全量/局部 bitstream 和 HWH，本包未生成这些文件。手册链接的 PYNQ-Z1 预编译文件不可直接用于 Arty；`lab3_2.ipynb` 会在缺少匹配文件时停止。Section 5.3 原始 HelloWorld resizer 及其兼容镜像也需在板上运行，本包未替代或伪造结果。

## 重建

从仓库根目录执行：

```powershell
& ./Lab3/scripts/build_all.ps1
```

需本机 `D:/Xilinx/*/2022.1`、Python、NumPy、Pillow，并保留 Lab 1 工程作为 PS/DDR/UART 配置来源。HLS、Vivado、软件工程分别生成在 Lab 3 的 `build/`、`vivado/`、`vitis_workspace/`；脚本会重建这些生成目录。

仅重建 ARM 软件并重打包已有硬件：

```powershell
& ./Lab3/scripts/build_all.ps1 -SkipHls -SkipHardware
```

仅重打包现有构建输入：

```powershell
& ./Lab3/scripts/build_boot.ps1
```

原始起始代码的三个 Tcl 入口也已改为调用相应的 Lab 3 构建脚本。最终报告由 `scripts/create_report.py` 生成，发布包由 `scripts/package_release.py` 生成。
