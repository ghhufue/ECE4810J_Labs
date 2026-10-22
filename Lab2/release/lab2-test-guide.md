# Lab 2 - Arty Z7-20 启动镜像与测试说明

本镜像包含 RTL/HLS 16 位无符号乘法器，以及 RTL 流水线/HLS 两套 32 位 RV32IM ALU（全部 18 种运算）。启动时自动自检，完成后进入串口菜单。

**验证状态：离线仿真、综合、布局布线、ARM 编译和启动镜像校验已通过；开发板暂不在手边，实际 SD 启动与串口输出尚未验证。下文串口输出均为预期结果。**

## 1. 下载与校验

下载此 Release 的 `BOOT.BIN`，可同时下载 `BOOT.sha256`、`manifest.json` 和本测试说明。无需安装 Vivado/Vitis 即可上板运行预编译镜像。

- 开发板：**Digilent Arty Z7-20**，器件 `xc7z020clg400-1`。
- PL 时钟：100 MHz。
- 工具版本：Vivado / Vitis / Vitis HLS 2022.1。
- 镜像大小：**4,313,680 字节**。
- 镜像内容，按顺序：FSBL、FPGA bitstream、ARM 自检/交互应用。
- 此文件用于裸机程序的 SD 启动；PYNQ/Jupyter 使用另行准备的 Linux 系统镜像。

SHA-256：

```text
9f57c42b36ea5f82667ab36efd79304cbb6b2ceaaef4f7b6c0282296e1ca9d08
```

Windows PowerShell 校验：

```powershell
(Get-FileHash -LiteralPath .\BOOT.BIN -Algorithm SHA256).Hash.ToLower()
```

将结果与上面的哈希比较。`manifest.json` 记录了构建输入文件的哈希。

## 2. SD 启动与串口设置

1. 准备 FAT32 格式的 SD 卡，将下载的 `BOOT.BIN` **直接复制到卡的根目录**，保持该文件名。此步骤是复制启动文件，无需将 BIN 当作整盘系统镜像烧录。
2. 开发板断电后，将 **JP4 设置为 SD 启动**，插入 SD 卡。
3. 用板载 USB 连接电脑，选择对应 COM 端口。串口设置为 **115200 baud、8 data bits、无校验、1 stop bit、无流控（8N1）**。
4. 关闭串口工具的本地回显（应用自行回显输入），发送行尾可选 CR 或 CRLF。
5. 先打开串口，再给开发板上电或按复位键，观察启动信息。
6. 如果错过启动输出，等程序进入菜单后输入 `t` 并回车，重新执行完整自检。

## 3. 自动自检：通过标准

预期启动标题：

```text
ECE4810J Lab 2 | Arty Z7-20 | 100 MHz PL
RTL/HLS multipliers + RTL pipelined/HLS RV32IM ALUs
UART: 115200 8N1; SD boot image
```

随后自动测试 100 组乘法操作数，以及每套 ALU 的 7,509 组参考向量。ALU 覆盖全部 18 种操作、除零、有符号溢出、移位量低 5 位截断、乘法高位和无效操作码。

最终成功时必须看到：

```text
MULTIPLIER RESULT: 100 tests, 0 failures
RTL ALU RESULT: 7509 tests, 0 failures
HLS ALU RESULT: 7509 tests, 0 failures
LAB2 SELF-TEST: PASS

Menu: t = self-test, m = 16-bit multiply, a = 32-bit ALU
>
```

中间还会列出操作码 0..17 各自的结果：每种操作 417 组测试，预期均为 `0 failures`。若出现 `FAIL`、`ERROR`、`ALU TEST ABORTED`、非零失败数或持续卡住，应保留完整输出用于定位。

## 4. 交互菜单

每次输入后按回车；完成一次测试后会重新显示菜单。

| 命令 | 功能 |
| --- | --- |
| `t` | 重跑完整自动自检 |
| `m` | 输入两个 0..65535 的操作数，比较 RTL/HLS 16 位乘法结果 |
| `a` | 输入操作码 0..17，再输入两个 32 位操作数，比较 RTL/HLS ALU 结果 |

操作数支持十进制、`0x` 前缀的十六进制；ALU 也支持负十进制数。ALU 输入范围为 `-2147483648..4294967295`，内部按 32 位位模式解释，例如 `-20` 与 `0xffffffec` 等价。十进制数请勿加前导零，程序的 C 自动进制解析会将前导零视为八进制。

### 4.1 乘法示例

依次输入，每行后回车：

```text
m
2
3
```

预期结果：

```text
2 * 3: RTL=0x00000006 HLS=0x00000006 expected=0x00000006 PASS
```

再测试 `65535` 与 `65535`，两套结果都应为 `0xfffe0001`。

### 4.2 ALU 示例

测试有符号除法 `-20 / 3`，依次输入：

```text
a
14
-20
3
```

预期结果为 -6 的 32 位补码：

```text
DIV A=0xffffffec B=0x00000003 RTL=0xfffffffa HLS=0xfffffffa MATCH
```

`MATCH` 表示 RTL/HLS 两路一致；还应与下表的期望值核对，确认结果正确。

### 4.3 全部 18 种操作的手动测试

每行测试都先输入 `a`，再依次输入操作码、A、B。两路结果都应等于“预期结果”，并显示 `MATCH`。

| 操作码 | 操作 | A | B | 预期结果（十六进制） |
| --- | --- | --- | --- | --- |
| 0 | ADD | 20 | 5 | `0x00000019` |
| 1 | SUB | 20 | 5 | `0x0000000f` |
| 2 | SLT（有符号） | -20 | 5 | `0x00000001` |
| 3 | SLTU（无符号） | -20 | 5 | `0x00000000` |
| 4 | AND | 0xf0 | 0x0f | `0x00000000` |
| 5 | OR | 0xf0 | 0x0f | `0x000000ff` |
| 6 | XOR | 0xaa | 0xff | `0x00000055` |
| 7 | SLL | 1 | 33 | `0x00000002` |
| 8 | SRL | 0x80000000 | 31 | `0x00000001` |
| 9 | SRA | 0x80000000 | 31 | `0xffffffff` |
| 10 | MUL（低 32 位） | -20 | 5 | `0xffffff9c` |
| 11 | MULH（signed x signed 高位） | -20 | 5 | `0xffffffff` |
| 12 | MULHSU（signed x unsigned 高位） | -20 | 0xffffffff | `0xffffffec` |
| 13 | MULHU（unsigned x unsigned 高位） | 0xffffffff | 0xffffffff | `0xfffffffe` |
| 14 | DIV（有符号） | -20 | 3 | `0xfffffffa` |
| 15 | DIVU（无符号） | 0xffffffff | 3 | `0x55555555` |
| 16 | REM（有符号） | -20 | 3 | `0xfffffffe` |
| 17 | REMU（无符号） | 0xffffffff | 3 | `0x00000000` |

补充边界测试：

| 操作码 | A | B | 预期结果 | 含义 |
| --- | --- | --- | --- | --- |
| 14 或 15 | 123 | 0 | `0xffffffff` | 除零的商 |
| 16 或 17 | 123 | 0 | `0x0000007b` | 除零的余数保留 A |
| 14 | 0x80000000 | -1 | `0x80000000` | 有符号除法溢出 |
| 16 | 0x80000000 | -1 | `0x00000000` | 溢出情况下的余数 |

## 5. 上板测试需要记录哪些报告图片

以下清单依据实验手册 Section 2.5、3、5、7 整理。图片分组和文件名是便于采集、整理报告的建议。**先完成自动自检和 SD 交互乘法两组记录，再补充流水线乘除法与边界测试。** 实际约需 3-5 张清晰的串口截图，具体张数随窗口大小调整。

### 5.1 截图清单与报告对应关系

| 建议文件名 | 如何获取 | 截图必须拍到的内容 | 用于报告哪一部分 |
| --- | --- | --- | --- |
| `lab2_sd_boot.png` | JP4 设为 SD，先打开串口，再重新上电；本次启动不要通过 JTAG 下载应用 | 三行启动标题、`MULTIPLIER RESULT: 100 tests, 0 failures`；若能同屏，保留菜单或后续自检结果 | Section 3：SD 启动过程；Section 2：两套乘法器的上板自检 |
| `lab2_alu_selftest.png` | 等待开机自检，或在菜单输入 `t` 并回车 | 操作码 0..17 的完整统计，每种操作 `417 tests, 0 failures`；两套 ALU 各 `7509 tests, 0 failures`，以及 `LAB2 SELF-TEST: PASS` | Section 2：全部 18 种 ALU 操作的板级验证；Section 5：流水线 ALU 功能证据 |
| `lab2_sd_interactive_multiplier.png` | 输入 `m`，测试 A=2、B=3；再次输入 `m`，测试 A=65535、B=65535 | 输入提示、实际输入、RTL/HLS 两路结果及 `PASS`；两组结果分别为 `0x00000006`、`0xfffe0001` | Section 3：SD 启动后的交互输入；Section 2：RTL/HLS 乘法器结果比较 |
| `lab2_pipe_alu_mul_div_rem.png`（建议补充） | 每次输入 `a`，测试 MUL（10，-20，5）、DIV（14，-20，3）、REM（16，-20，3） | 操作名称、A/B、RTL/HLS 两路结果及 `MATCH`；结果依次为 `0xffffff9c`、`0xfffffffa`、`0xfffffffe` | Section 5：流水线乘法、除法与余数验证 |
| `lab2_alu_boundary.png`（建议补充） | 输入 `a`，测试除零（14，123，0）、除零余数（16，123，0）、有符号溢出（14，0x80000000，-1） | 输入与两路结果；预期依次为 `0xffffffff`、`0x0000007b`、`0x80000000`，并显示 `MATCH` | ALU 特殊情况的补充验证 |

自动自检的乘法器总结位于 18 项 ALU 统计之前；可用第一张图保存乘法器总结，用第二张图保存 18 项统计及最后三行 ALU/总测试总结。若一屏放不下，将自检图分为 `_1.png`、`_2.png`，保证统计行和总结可读且完整。**无需为了截图而把 18 种操作各截一张；但应保留全部 18 项统计和最终总结。**

### 5.2 采集与写图注时的注意事项

- Section 2 的交付要求写明使用 **Vitis Serial Terminal**；Section 3 允许 Vitis Serial Terminal 或 PuTTY。优先使用 Vitis 串口终端采集，串口设置为 115200、8N1、无流控。
- 串口截图应保留终端窗口标题或端口信息，正文清晰可读。建议同时保存完整串口文本日志，便于报告整理和问题定位。
- Section 3 的图注写明：**JP4 为 SD 启动，重新上电，程序从 SD 卡运行，未通过 JTAG 下载应用**。启动标题中的 `SD boot image` 是程序固定文字，实际启动方式应通过上述操作确认。
- 可额外拍一张能看清 SD 卡、USB 连接和 JP4 位置的板卡照片作辅助说明；手册明确要求的 Section 3 交付物是串口截图，实物照片属于补充。
- 当前镜像使用 **RTL 流水线 ALU + HLS ALU**，图注应如实标注。自动测试截图可为多个部分提供证据，但需说明这些结果来自同一合并应用；组合版与流水线版的资源/时序比较仍需分别取得相应设计的实现报告。
- 示例图注：`图 X. Arty Z7-20 从 SD 卡启动后，RTL/HLS ALU 全部 18 种操作的自检结果，两套 ALU 各完成 7509 组测试且失败数为 0。` 仅在实测输出确实如此时使用该图注。
- 出现非零失败数、`FAIL`、`ERROR` 或卡住时，也应保存原始记录并排查；不要将说明中的预期输出制作成实验结果图。

### 5.3 完整报告还需另外采集的图片

本 BIN 能产生上表的串口运行记录。完整 Lab 报告还需要从开发工具或 PYNQ 环境采集：

- **Vitis HLS**：ALU 的 C Simulation 成功日志、含时序与资源估计的 Synthesis Summary、Cosimulation Report 的 Pass。
- **Vivado**：分别高亮 RTL/HLS 乘法器、RTL/HLS ALU 的 Implemented Device 图，以及 Utilization Summary 和 Design Timing Summary；流水线加分项还需与 Section 2 组合版结果比较。
- **Vitis IDE**：ALU 应用编译完成界面。当前命令行 ARM GCC 的编译记录可作辅助证据，不能直接当作 Vitis IDE 界面截图。
- **PYNQ**：Jupyter Notebook 页面，必须包含浏览器地址栏；需要另外启动 PYNQ Linux 系统采集。

### 5.4 常见问题定位

- 全无输出：核对 COM 端口、USB 连接、供电、JP4、FAT32、文件是否位于根目录并命名为 `BOOT.BIN`，然后在串口已打开时复位。
- 输出乱码：核对 115200、8N1、无流控。
- 只有输入回显，没有预期启动信息：复位重新捕获启动输出，或在菜单状态输入 `t`；应用输出和终端本地回显应避免重复。
- 显示 `ERROR: HLS ... timeout`、`FAIL` 或卡住：保存从启动起的完整输出，核对镜像 SHA-256，然后重新上电复测。

## 6. 已通过的离线检查与已知限制

- HLS ALU：7,509 组 C 仿真和 C/RTL 协同仿真通过；HLS 乘法器：356 组测试通过。
- RTL 组合 ALU 和流水线 ALU：各 7,509 组测试通过；复位中断检查通过。
- AXI 封装：7,509 组测试，以及独立 AW/W、B/R 反压、字节使能、非法访问、忙时拒绝与复位检查通过。
- 100 MHz 布局布线时序通过：WNS `+1.979 ns`、WHS `+0.013 ns`；使用 4,414 LUT、6,598 FF、10 DSP、0 BRAM、0 latch。
- ARM GCC 使用 `-Wall -Wextra -Werror` 编译通过；镜像分区头、FSBL/应用载荷、PL 配置载荷及 XSA 内嵌 bitstream 一致性校验通过。
- PS/DDR/UART 配置继承 Lab 1。Vivado 保留原配置中 DDR DQS delay 第 2、3 通道为负值的提示（`-0.009`、`-0.033`）；实际 DDR 初始化和 SD 启动需要实板确认。
- **本发布尚未经过实板验证，不能将上述预期串口输出作为已经取得的实验截图。**

本次发布上传预编译镜像、校验信息和测试说明。Lab 2 源码目前保存在本地工作区，Release 标签对应仓库现有提交；GitHub 自动生成的 `Source code` 压缩包尚不包含本次 Lab 2 实现。
