# Lab 3 - Arty Z7-20 上板测试版

包含可直接复制到 FAT32 SD 卡根目录的 `BOOT.BIN`（FSBL + bitstream + ARM 自检程序），用于验证 32 位加法器、8×8 DCT/IDCT 和 128 阶 FIR。

**验证状态：离线仿真、100 MHz 布局布线、ARM 编译及启动镜像校验通过；实际 SD 启动、DDR 初始化、串口自检与 PYNQ 运行尚待板卡验证。本文输出是预期结果。**

## 建议下载

- [SD 测试组合包](https://github.com/ghhufue/ECE4810J_Labs/releases/download/lab3-v0.1-hwtest/lab3_arty_sd_test.zip)：镜像、说明、参考数据、空白测试记录表及日志核对脚本。
- [快速使用说明](https://github.com/ghhufue/ECE4810J_Labs/releases/download/lab3-v0.1-hwtest/lab3-usage.md) · [完整上板测试指南](https://github.com/ghhufue/ECE4810J_Labs/releases/download/lab3-v0.1-hwtest/lab3-test-guide.md)
- [PYNQ 测试包](https://github.com/ghhufue/ECE4810J_Labs/releases/download/lab3-v0.1-hwtest/lab3_pynq_test.zip)：单独使用 Arty PYNQ 系统卡时所需的完整 overlay、Notebook 和输入数据。

也可单独下载 `BOOT.BIN`、`BOOT.sha256`、`manifest.json`。`SHA256SUMS` 覆盖所有运行包与测试文档；`release-info.json` 记录发布来源与验证状态。

## 裸机启动步骤

1. 目标板卡为 **Digilent Arty Z7-20 / xc7z020clg400-1**。
2. 校验下载文件：镜像为 **4,313,672 字节**，SHA-256 为：

   ```text
   d8bbb6ef334717ea2141ec69f2e2cce13124493679193fa3f81ceb271b566f44
   ```

   PowerShell：`(Get-FileHash -LiteralPath .\BOOT.BIN -Algorithm SHA256).Hash.ToLower()`。
3. 将 `BOOT.BIN` 复制到专用 FAT32 SD 卡根目录，保持文件名；不用把 BIN 当作整盘镜像烧录。
4. 开发板断电，将 **JP4 设为 SD**，插卡，选择与实际连接相符的供电方式。
5. 连接板载 USB-JTAG/UART，串口设为 **115200、8N1、无流控**。先打开串口日志，再给开发板上电。
6. 等待自检结束。通过时应包含：

   ```text
   ADD RESULT: 36 tests, 0 failures
   DCT/IDCT RESULT: 323 blocks, 41344 values, 0 failures
   FIR RESULT: 1024 samples, 0 failures
   LAB3 SELF-TEST: PASS
   ```

## 交互与下一步测试

| 输入 | 操作 | 通过标准 |
| --- | --- | --- |
| `t` | 再次运行全部自检 | 三项数量正确，全部零失败，最后 PASS |
| `d` | 打印 Lena 输入、DCT、IDCT 三个 8×8 矩阵 | 与完整指南的 192 个参考值一致 |
| `f` | 输出 FIR CSV | 标记之间 1024 行；首行 `0,96,960`，全部卷积值匹配 |

输入一个小写字母即可，无需回车。测试指南还提供冷启动复测、需要保存的日志/截图/照片、PYNQ 各 Notebook 的预期结果、故障定位与待补项目。

可用提供的 `verify_board_log.py` 核对保存的日志：

```powershell
python .\tools\verify_board_log.py .\serial_run1.txt --require-dct --require-fir --output-dir .\board_results
```

预期输出 `status: PASS`、`errors: []`；仅核对文本内容，真实运行来源及 SD 启动方式需由原始日志和实物记录支持。

## PYNQ 与课程交付范围

- 裸机 BIN 不包含 Linux/Jupyter。PYNQ 测试需另一张与 Arty 匹配的系统卡；不要覆盖现有 PYNQ 卡的启动文件。
- 自建完整 overlay 可用于加法器、DCT 和 FIR Notebook。Section 5.1 / 5.4 的真实输出以及 Section 6 的实际波形需上板采集。
- 当前发布不含 Arty 专用局部重配置设计；Section 5.2 仍需匹配的全量/局部 bitstream 与 HWH，以及两张真实 LED 照片。手册指向的 PYNQ-Z1 文件不能直接代替 Arty 文件。
- Section 5.3 原始 PS/PL resizer 仍需在兼容的 Arty PYNQ 环境运行并保存截图和实际计时。

离线实现时序：100 MHz，WNS +3.387 ns、WHS +0.044 ns。PS/DDR/UART 继承 Lab 1，已有 DDR DQS delay 提示仍需实物初始化测试。

Release 标签基于仓库现有提交；Lab 3 实现仍位于本地工作区。GitHub 自动生成的 `Source code` 压缩包不包含本次 Lab 3 实现，**请从 Assets 下载测试文件**。
