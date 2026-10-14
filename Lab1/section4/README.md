# Section 4 AXI-Lite 除法器

目标平台：Arty Z7-20，Vivado / Vitis 2022.1。独立工程保留原乘法器平台的 Zynq PS、DDR 和 UART 配置。

## 后续上板测试

1. 将 `Lab1/boot/section4-divider-BOOT.bin` 复制到 FAT32 格式 SD 卡的根目录，并重命名为 `BOOT.BIN`。
2. 在开发板断电时，把启动模式跳线设置为 SD 启动，插入 SD 卡。
3. 连接板载 USB UART，在串口工具或 Vitis Serial Terminal 中选择对应 COM 端口：115200 波特率、8 数据位、无校验、1 停止位、无流控。
4. 打开串口后上电或按复位按钮。程序自动运行 11 项测试，最后预期显示 `RESULT: 11 tests, 0 failures`。
5. 保存真实串口截图。当前仿真和编译结果不能替代板级串口截图。

BOOT 镜像按顺序包含本次硬件平台生成的 FSBL、除法器 bitstream 和 `hello_rtl_divider.elf`。

## 寄存器接口

基地址 `0x43C00000`，两个输入均为 16 位无符号整数。写输入寄存器即启动；普通运算需要 16 个 PL 时钟周期。

| 偏移 | 访问 | 定义 |
| --- | --- | --- |
| `0x00` | 读写 | `[31:16]` 被除数 a，`[15:0]` 除数 b；支持 WSTRB 字节写，零 WSTRB 不启动 |
| `0x04` | 只读 | 商，低 16 位有效，高 16 位为零 |
| `0x08` | 只读 | 余数，低 16 位有效，高 16 位为零 |
| `0x0C` | 只读 | bit 0 BUSY，bit 1 DONE，bit 2 DIVIDE_BY_ZERO |

DONE 保持到下一次启动或复位。软件必须等到 `BUSY=0, DONE=1` 再读结果；运算期间输出保留上次结果。忙时写输入返回 AXI SLVERR，并保留原运算。写只读寄存器或访问非对齐地址也返回 SLVERR。复位清空输入、输出、状态和未完成的总线事务。

除数为零时：商 `0xFFFF`、余数为被除数、状态 `0x6`，这是本设计明确定义的错误结果。软件避免对零执行 C 语言 `/` 和 `%`。

## 设计与验证

`rtl_divider.v` 使用逐位恢复除法，每周期移位、比较并减法，同时产生商和余数。AXI 写地址和写数据分别缓冲，读写响应在主机等待期间保持稳定。

`tb_rtl_divider.sv` 验证 272 项算术运算（含 256 项随机输入），并检查分离的 AW/W 到达、B/R 响应等待、字节写、零字节使能、只读保护、非对齐访问、忙时拒绝以及运算中复位。

真实验证记录见 `Lab1/report/logs/section4_divider_*.txt`；资源和时序报告由实现后的 Vivado 工程生成。无开发板时不能验证 SD 启动、DDR 初始化和真实串口输出。

本次实现结果：整个 PL 设计使用 512 LUT、631 FF；其中带 AXI 接口的除法器 IP 使用 158 LUT、198 FF，DSP 和 BRAM 均为零。100 MHz PL 时钟下，布线后 WNS 为 +4.069 ns，WHS 为 +0.034 ns，建立、保持和脉宽约束均满足。

PS 配置沿用原项目，Vivado 仍提示 DDR 第 2、3 通道的 DQS 到时钟延迟参数为负值（-0.009、-0.033）。这来自原板卡配置，本次构建成功；实际 DDR 初始化和 SD 启动仍需板级验证。

## 工程与重建

- Vivado 工程：`Lab1/vivado/section4_divider/lab1_section4_divider.xpr`。
- IP：`Lab1/vivado/ip_repo/rtl_divider_1.0/`。
- 导出硬件：`Lab1/exported/platform_section4_divider.xsa`。
- Vitis 平台与应用：`Lab1/vitis_workspace/platform_section4_divider`、`hello_rtl_divider`。
- 软件源代码：`Lab1/section4/lab1-divider.c`。

在仓库根目录 PowerShell 中执行：

```powershell
python Lab1/section4/create_divider_ip.py
& ./Lab1/section4/run_simulation.ps1
& D:/Xilinx/Vivado/2022.1/bin/vivado.bat -mode batch -source Lab1/section4/build_hardware.tcl
& D:/Xilinx/Vitis/2022.1/bin/xsct.bat Lab1/section4/build_software.tcl
& ./Lab1/section4/build_boot.ps1
```

硬件脚本会覆盖本任务生成的除法器工程。软件脚本可重建已有软件工程；更换 XSA 后，应先在 Vitis 中更新硬件平台，或使用独立的全新工作区重建。

实验要求的资源报告已由脚本导出；Vitis IDE 编译完成截图需在 IDE 打开并构建 `hello_rtl_divider` 后截取，串口截图需连接开发板运行后截取。
