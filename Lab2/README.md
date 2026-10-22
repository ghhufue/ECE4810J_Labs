# Lab 2 - Arty Z7-20 SD 启动镜像

最终交付：`boot/BOOT.BIN`。镜像按启动顺序包含本次硬件平台的 FSBL、PL bitstream 和 ARM 测试应用，与 Lab 1 的交付方式一致。

## 上板步骤

1. 将 `Lab2/boot/BOOT.BIN` 复制到 FAT32 格式 SD 卡的根目录，文件名保持 `BOOT.BIN`。
2. 开发板断电后，将 Arty Z7-20 的 JP4 设为 SD 启动，插入 SD 卡。
3. 连接板载 USB UART，打开对应 COM 端口：**115200 baud、8N1、无流控**。
4. 上电或按复位键。应用先自动测试 RTL/HLS 乘法器，再测试 RTL/HLS ALU，随后进入交互菜单。
5. 如果打开串口时已经错过启动输出，输入 `t` 并回车，可重新执行完整自检。

自动自检成功时，预期输出包括：

```text
MULTIPLIER RESULT: 100 tests, 0 failures
RTL ALU RESULT: 7509 tests, 0 failures
HLS ALU RESULT: 7509 tests, 0 failures
LAB2 SELF-TEST: PASS

Menu: t = self-test, m = 16-bit multiply, a = 32-bit ALU
>
```

以上为**预期串口输出**；当前开发板不在手边，尚未验证实际 SD 启动和串口结果。

菜单命令均输入一个字母并回车：

| 命令 | 功能 |
| --- | --- |
| `t` | 重跑所有自检，逐项显示 18 种操作的测试数量和错误数 |
| `m` | 输入两个 0..65535 的整数，比较 RTL/HLS 16 位乘法结果 |
| `a` | 选择操作码 0..17，再输入两个 32 位操作数，比较 RTL/HLS ALU 结果 |

操作数支持十进制、`0x` 前缀十六进制，以及 ALU 的负十进制数。例如 `-20` 和 `0xffffffec` 表示同一 32 位位模式。输入采用 C 的自动进制识别，前导 `0` 表示八进制，请按普通十进制形式输入。

## 硬件与运算

目标器件 `xc7z020clg400-1`，PL 时钟 100 MHz，工具 Vivado / Vitis / Vitis HLS 2022.1。PS、DDR 和 UART 配置继承 Lab 1 已有的 Arty Z7-20 工程；独立工程位于 `vivado/lab2/lab2.xpr`。

| IP | AXI 基地址 | 作用 |
| --- | --- | --- |
| `rtl_multiplier_0` | `0x43C00000` | Lab 1 的 16 x 16 位无符号 RTL 乘法器 |
| `hls_multiplier_0` | `0x43C10000` | HLS 实现的 16 x 16 位无符号乘法器 |
| `rtl_pipe_alu_0` | `0x43C20000` | RTL 流水线 ALU |
| `hls_alu_0` | `0x43C30000` | HLS 实现的 RV32IM ALU |

| 操作码 | 操作 |
| --- | --- |
| 0..3 | ADD, SUB, SLT, SLTU |
| 4..6 | AND, OR, XOR |
| 7..9 | SLL, SRL, SRA |
| 10..13 | MUL, MULH, MULHSU, MULHU |
| 14..17 | DIV, DIVU, REM, REMU |

移位量只使用 B 的低 5 位。除零时商为 `0xffffffff`、余数为 A。有符号 `INT_MIN / -1` 返回 `0x80000000`，余数为 0；有符号除法向零截断，非零余数符号与被除数一致。无效操作码返回 0。

为满足 100 MHz 时序，启动镜像采用流水线 RTL ALU：简单操作在请求采样周期产生结果，乘法分为乘积寄存与结果选择两步，除法经过 32 级恢复除法流水线再做符号修正。AXI 封装只允许一个未完成运算。`rtl/rtl_alu.sv` 保留 Section 2 的组合参考实现；实际打包进镜像的是 `rtl/rtl_pipe_alu.sv`。

RTL ALU 四个寄存器分别是 `+0x00` A、`+0x04` B、`+0x08` 操作码、`+0x0c` 只读结果。写操作码的最低字节即启动；结果读取会等待运算完成。AXI 写地址与写数据独立接收，支持字节写，忙时写入及非法地址返回 SLVERR。零字节使能不会启动运算。

## 已完成的离线验证

- 独立 Python 整数模型生成 7,509 组向量：417 组操作数覆盖全部 18 种操作，加 3 组无效操作码。
- HLS ALU 的 C 仿真、C/RTL 协同仿真均通过全部 7,509 组向量；HLS 乘法器通过 356 组向量。
- RTL 组合版与流水线版各通过 7,509 组向量，复位中断运算检查通过。
- AXI 封装通过 7,509 组向量，以及分离 AW/W 到达、B/R 反压、字节写、零字节使能、忙时拒绝、访问错误与复位检查。
- 布局布线后 100 MHz 时序通过：WNS `+1.979 ns`、WHS `+0.013 ns`，无时序违例；4,414 LUT、6,598 FF、10 DSP、0 BRAM、0 latch。
- ARM 应用、FSBL 和启动镜像的最终构建结果见 `logs/`；镜像结构和分区头校验结果见 `logs/boot_validation.txt`，输入文件哈希见 `boot/manifest.json`。

应用使用 Vitis 自带的 ARM GCC、当前 XSA 生成的 BSP 和 FSBL 构建；启用 `-Wall -Wextra -Werror`，编译通过。构建脚本直接调用该工具链，避免本机 Vitis 2022.1 的命令行应用模板创建停滞。已核对镜像中的 FSBL/应用 ELF 载荷、PL 配置载荷，以及 XSA 内嵌 bitstream 与实际构建文件一致。

PS 配置继承 Lab 1 的 DDR DQS delay 设置，Vivado 仍提示第 2、3 通道的负值 `-0.009`、`-0.033`。本次构建及 PL 时序通过，实际 DDR 初始化和 SD 启动需上板确认。

## 文件与重建

| 路径 | 内容 |
| --- | --- |
| `boot/BOOT.BIN` | 可复制到 SD 卡根目录的启动镜像 |
| `boot/BOOT.sha256` | 镜像 SHA-256 |
| `boot/lab2.bif` | Bootgen 分区配置 |
| `boot/manifest.json` | 镜像信息和匹配构建输入的哈希 |
| `exported/lab2.xsa` | 含 bitstream 的硬件导出文件 |
| `software/hls_rtl_alu.c` | 自检和交互程序 |
| `hls/` | HLS 源代码与测试平台 |
| `rtl/` | RTL 源代码与 AXI 实现 |
| `tests/` | 独立参考向量和 RTL/AXI 测试平台 |
| `logs/` | 实际构建、仿真、资源和时序记录 |

从仓库根目录在 PowerShell 中完整重建：

```powershell
& ./Lab2/scripts/build_all.ps1
```

脚本使用本机 `D:/Xilinx/*/2022.1` 工具与 PATH 中的 Python，依次生成向量、打包 IP、RTL/AXI 仿真、HLS 仿真/综合/协同仿真/IP 导出、Vivado bitstream/XSA、Vitis 软件/FSBL、Bootgen 镜像并校验。完整重建会覆盖 Lab 2 生成的工程和镜像。

仅修改软件后，复用已验证硬件：

```powershell
& ./Lab2/scripts/build_all.ps1 -SkipHls -SkipHardware
```

只重新打包已有构建输入：

```powershell
& ./Lab2/scripts/build_boot.ps1
```

本次交付以 SD 启动 `.bin` 为目标。PYNQ Linux 镜像、Jupyter 操作、实物截图及完整实验报告不包含在此启动镜像中。
