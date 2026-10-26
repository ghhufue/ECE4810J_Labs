# Lab 3 上板测试指南：步骤、预期结果与取证

适用发布：`lab3-v0.1-hwtest`；板卡：**Arty Z7-20 / xc7z020clg400-1**；日期：2026-10-26。

**状态：本文中的结果均为预期值。当前镜像已通过离线验证，但尚未进行实板测试。完成下列操作并保存真实证据后，才能在报告中写“板上通过”。**

## 1. 测试顺序与准备物品

| 阶段 | 需要做什么 | 成功时得到什么 |
| --- | --- | --- |
| A：裸机 SD 启动 | 校验 BIN、准备 SD、设跳线、串口记录、上电 | 三项自检零失败，出现 `LAB3 SELF-TEST: PASS` |
| B：重复与数据核对 | 运行 `t`、`d`、`f`，再次冷启动 | 重跑仍通过；三个矩阵正确；1024 行 FIR 数据正确 |
| C：PYNQ 自建 IP | 换 PYNQ 系统卡，运行提供的 Notebook | 加法结果 7、9、35；DCT/FIR 参考一致；保存波形 |
| D：补齐课程 Section 5 | 基础 overlay、PR、原始 resizer | Notebook 实际输出、两张 PR 照片、PS/PL 测量结果 |

准备 Arty Z7-20、可靠供电、可传输数据的板载 USB-UART 连接线、专用 FAT32 SD 卡、读卡器和串口终端（PuTTY 或 Vitis 串口终端）。后续 PYNQ 测试需要与 Arty 匹配的系统卡与网络连接。先使用专用裸机测试卡，保留现有 PYNQ 系统卡；不要求为了测试而格式化已有系统卡。

推荐记录目录：

```text
lab3_board_results/
  BOARD_TEST_RECORD.md
  serial_run1.txt
  serial_run2.txt
  selftest.png
  lena_matrices.png
  board_sd_setup.jpg
  uart_check.json
  fir_capture.csv
  pynq/                 # 已执行且带输出的 Notebook
  photos/               # PR 的两张板卡照片
```

空白 `BOARD_TEST_RECORD.md` 随测试包提供。至少填写板卡型号、Release 标签、镜像哈希、JP4 位置、供电方式、串口号和测试日期。

## 2. 下载与完整性检查

从 Release 的 **Assets** 下载 `BOOT.BIN`、`BOOT.sha256`、`manifest.json`，或下载 `lab3_arty_sd_test.zip` 解压。仅运行预编译镜像不需要 Vivado/Vitis。

`BOOT.BIN` 应为 **4,313,672 字节**，SHA-256：

```text
d8bbb6ef334717ea2141ec69f2e2cce13124493679193fa3f81ceb271b566f44
```

Windows PowerShell：

```powershell
(Get-FileHash -LiteralPath .\BOOT.BIN -Algorithm SHA256).Hash.ToLower()
(Get-Item -LiteralPath .\BOOT.BIN).Length
```

Linux：

```bash
sha256sum -c BOOT.sha256
```

大小和哈希必须一致。后续复制到 SD 卡后，可对卡上的文件再次运行校验。

## 3. 裸机 SD 启动：连接与设置

1. 将 `BOOT.BIN` **复制到 FAT32 SD 卡根目录**，保持名称。此 BIN 是 Zynq 启动文件，不是需要按整盘镜像写入的 Linux 系统镜像；裸机运行不需要 `image.ub`、网络或 Jupyter。
2. 开发板断电，将 **JP4 设为 SD**，插卡。电源选择跳线按实际 USB/外接供电设置。板卡跳线及供电方式可核对 [Digilent 的 Arty Z7-20 启动说明](https://github.com/Digilent/Petalinux-Arty-Z7-20#run-the-pre-built-image-from-sd)；该链接中的 Linux 文件列表不适用于本裸机包。
3. 使用板载 **USB-JTAG/UART** 口连接电脑，选实际出现的 COM 端口。不要将 USB Host 口当作电脑串口连接口。
4. 设置 **115200 baud、8 data bits、无校验、1 stop bit、无流控**；关闭终端本地回显，程序会自行回显输入。
5. 开启原始文本日志记录，例如 PuTTY 的 Session → Logging → All session output，指定 `serial_run1.txt`。如所用版本菜单不同，使用其保存全部串口输出的功能。
6. **先打开串口，再给板卡上电**。若刚更改过 JP4，执行完整断电再上电，以重新采样启动模式；不要只依赖 PL 编程/复位按钮。
7. 拍摄一张能看清板卡型号、SD 卡、USB 连接和 JP4 的照片，作为 SD 启动方式的辅助证据。本文应用没有设计固定 LED 成功提示，以串口与数据核对为准。

### 3.1 自动自检的预期结果

启动后应出现：

```text
ECE4810J LAB3 | Arty Z7-20 | PL 100 MHz
DCT/IDCT 0x43c00000, FIR 0x43c10000, ADD 0x43c20000
```

地址中的十六进制字母大小写不影响核对。可能存在 FSBL 额外输出，不作为失败条件。

随后应包含以下四行。三项测试的显示顺序不是通过条件，但每项数量、失败数与最后总结必须正确：

```text
ADD RESULT: 36 tests, 0 failures
DCT/IDCT RESULT: 323 blocks, 41344 values, 0 failures
FIR RESULT: 1024 samples, 0 failures
LAB3 SELF-TEST: PASS
```

之后应进入：

```text
Menu: t=self-test, d=Lena block, f=FIR CSV
>
```

通过标准：三项测试数量正确、全部 `0 failures`、总结为 `PASS`，且没有 `TIMEOUT` 或 `DCT mismatch`。仅看到启动标题不能算通过；标题中的板卡和频率是程序固定文字，也不能独立证明实际启动方式。

截图 `selftest.png` 应包含三项 RESULT、PASS 和终端窗口/端口信息。完整日志应从上电前开始记录。若一屏放不下，可保存两张连续截图，避免缺少某一项统计。

### 3.2 `t`：重复自检

在 `>` 提示后输入一个小写 `t`，无需回车。应再次完成 36 组加法、323 块 DCT/IDCT、1024 个 FIR 样本，仍为零失败和 PASS。FIR 自检开始时清历史，并在第 512 个样本处再次清历史，重复运行不应受前次数据影响。

若终端发送了 CR/CRLF，应用可能额外回显空行和菜单，不算失败。若错过最初启动输出，可用 `t` 重跑，但仍需另一次冷启动日志证明 SD 启动。

## 4. 手动数据测试：`d` 和 `f`

### 4.1 `d`：Lena 的三个 8×8 矩阵

输入 `d`，应先出现 `Lena top-left block: input, DCT, recovered`，随后依次打印输入、DCT、IDCT 三个矩阵。下面是从本次固定输入和独立参考文件整理出的**完整预期值**：

输入矩阵：

```text
160 160 160 159 161 156 161 159
161 160 159 159 161 155 161 159
160 161 160 158 161 156 162 159
161 161 159 159 161 156 161 159
160 160 160 159 161 156 162 159
162 162 157 154 159 159 157 159
159 159 162 157 159 161 158 155
157 157 155 155 157 158 155 157
```

DCT 矩阵：

```text
10172 30 23 11 0 -12 -33 47
47 0 5 -26 20 20 -39 28
-36 -6 -14 4 -3 -2 19 -11
17 9 6 6 -5 -6 7 1
-10 -12 -5 -11 14 6 -11 -1
15 10 -15 1 -18 3 11 2
-13 -4 22 6 3 -21 -3 -7
12 -5 -20 -13 -14 16 1 12
```

IDCT 恢复矩阵：

```text
159 159 159 158 160 155 160 158
161 159 158 159 161 155 161 159
160 160 159 157 160 155 161 158
161 161 159 158 160 156 160 158
159 159 160 158 160 156 161 158
162 162 157 154 158 159 157 158
159 158 162 157 158 161 157 154
156 156 154 155 157 157 155 157
```

逐项匹配参考值才算通过。前向 DCT 使用课程定点缩放，DC 系数为 `10172`，不能拿它直接与未缩放的浮点 DCT 比较。IDCT 使用手册的逐级截断，不要求与输入完全相等；本角块相对输入的最大绝对误差应为 1。整幅 Lena 的离线最大误差为 2，这是另一项离线结果，不能替代本板块的逐项核对。

保留 `lena_matrices.png` 及完整文本。不要仅凭恢复矩阵“看起来相近”判断正确。

### 4.2 `f`：1024 个 FIR 输入/输出

输入 `f`。完整输出应由两条标记包围，标记中间有表头和 **1024 行**数据，索引从 0 到 1023：

```text
FIR_CSV_BEGIN
index,input,output
0,96,960
1,-26,796
2,-41,360
3,-60,-569
4,-23,-1261
5,65,-957
6,4,-791
7,-40,-730
... 此处仅省略展示，实际输出应连续到索引 1023 ...
FIR_CSV_END
```

以上省略号不是应用输出。完整通过标准：索引连续、输入与固定种子 PRNG 一致、128 阶卷积的每个输出都正确，末尾标记存在，程序返回菜单。此命令开始前清一次历史，**中间不清零**；与自检中第 512 点处清历史的序列不能混为同一段结果。Notebook 则使用随附的 600 点原始输入，也不是这里的 1024 点序列。

### 4.3 自动核对真实串口日志

运行完启动自检、`t`、`d`、`f` 后关闭日志文件。解压 `lab3_board_test_tools.zip`，使脚本与 `board_expected.json` 位于同一目录，使用 Python 3（核对本身只需标准库）：

```powershell
python .\verify_board_log.py .\serial_run1.txt --require-dct --require-fir --output-dir .\board_results
```

SD 组合包中的脚本位于 `tools/`，可用：

```powershell
python .\tools\verify_board_log.py .\serial_run1.txt --require-dct --require-fir --output-dir .\board_results
```

预期程序退出码为 0，输出 JSON 中 `status` 为 `PASS`、`errors` 为 `[]`。生成 `uart_check.json`；若整份日志通过，还会将最后一段真实 FIR 数据导出为 `fir_capture.csv`。只检查启动日志时省略 `--require-dct --require-fir`。核对器会拒绝任何失败、超时、不完整自检或数据不匹配；若失败后已排除问题，另开新日志记录复测，保留旧日志。

脚本只验证给定文本，**不能证明文本来自真实板卡、镜像哈希正确或确实采用 SD 启动**；这些仍需操作记录与原始截图支持。

### 4.4 冷启动复测

在日志已保存后断电，再打开新的日志并上电。建议至少测试两次冷启动，记录第二次为 `serial_run2.txt`；有条件可做第三次。每次必须三项零失败。若只在部分上电时失败，不能标记为稳定通过，应保留供电方式、卡片信息和每次日志排查 DDR/启动链路。

## 5. PYNQ 测试：切换另一张系统卡

裸机镜像没有 Linux 或 Jupyter。使用与 **Arty Z7-20** 匹配的 PYNQ 系统卡启动。下载并解压 Release 的 `lab3_pynq_test.zip`，将 `notebooks/`、`exported/` 两个目录保持相邻，复制到 `/home/xilinx/jupyter_notebooks/lab3/`，使 Notebook 中的 `../exported/lab3.bit` 能找到 `.bit` 与同名 `.hwh`。不要用裸机测试卡中的 BOOT.BIN 覆盖 PYNQ 系统卡的启动文件。

1. 运行 `lab3_1.ipynb`，保存 `BaseOverlay`、LED 和 video 帮助输出。观察 LD0 切换；不同镜像可能不提供同一 video 层级，按实际输出说明。
2. 运行 `lab3_3.ipynb`，保存寄存器映射和结果 `7`、`9`、`35`。这是本次为 Arty 构建的 `scalar_add`，同一完整 overlay 还含 DCT 和 FIR。
3. 运行 `host_dct.ipynb`，保存 DCT/IDCT PASS 与恢复矩阵。
4. 运行 `host_fir.ipynb`，它会先清零历史，再读取随附的 600 个输入，与 NumPy 卷积逐项比较，并生成 `fir_board_output.dat` 和 `fir_board_plot.png`。保留真实图与 Notebook 输出，作为 Section 6 的上板证据。
5. 每次切换 overlay 后，重新创建相应 Python 驱动对象；旧对象不再代表当前 PL 配置。

| Notebook | 应得到的实际结果 | 保存内容 |
| --- | --- | --- |
| `lab3_1.ipynb` | overlay 已加载；帮助输出包含实际 IP；LD0 状态改变 | 带真实输出的 Notebook，LED 观察记录；video 层级不存在时保留实际提示 |
| `lab3_3.ipynb` | 寄存器/直接访问结果为 7、9；AddDriver 结果为 35 | 寄存器映射、三个结果和 Notebook |
| `host_dct.ipynb` | 无断言错误，输出 `DCT/IDCT PASS`；恢复矩阵与第 4.1 节一致 | Notebook 和恢复矩阵 |
| `host_fir.ipynb` | 无断言错误，输出 `FIR PASS: 600 samples`；两幅输入/输出曲线 | Notebook、`fir_board_output.dat`、`fir_board_plot.png`；实际主机耗时 |

对每份 Notebook 执行 Run All 后保存，保留代码、输出和错误信息。截图应看清 Notebook 名称、相关单元和输出；如课程要求浏览器地址栏，也一并保留。FIR 的 host elapsed 包含 MMIO 和 Python 开销，不能用来代表 HLS 内核每周期吞吐率。

## 6. 课程 Section 5.2：PR 文件与两张照片

当前 `lab3.bit` 是完整设计，不含重配置区域。`lab3_2.ipynb` 需要在 `notebooks/partial_reconfig/` 中提供六个文件：

```text
gpio_pr.bit  gpio_pr.hwh
led_5.bit    led_5.hwh
led_a.bit    led_a.hwh
```

这些文件必须来自 **Arty Z7-20 专用**的、接口一致的完整/局部重配置工程，并暴露 `gpio_0` 层级。手册中的仓库提供 PYNQ-Z1 示例，不能因 FPGA 型号相同而直接加载到 Arty。未找到或重新构建这些板卡匹配文件前，该 Notebook 会停止。

准备完成后分别加载 `led_5` 与 `led_a`，保存真实输出，并拍摄两张不同 LED 模式的板卡照片。局部重配置输出与照片没有离线替代品。

## 7. 课程 Section 5.3：PS/PL 原始 resizer

先记录 `BOARD`、PYNQ 包版本、Python 版本。手册指定的 PYNQ-HelloWorld 示例对应 PYNQ 2.7 环境；应使用支持当前 Arty 镜像的版本。原始源码见 [Xilinx/PYNQ-HelloWorld](https://github.com/Xilinx/PYNQ-HelloWorld)。确认版本和板卡支持后，按其 README 安装，并按手册交付官方 Notebook：

```bash
sudo pip3 install pynq-helloworld --no-build-isolation
pynq get-notebooks pynq-helloworld -p .
```

运行原始 `resizer_pl.ipynb` 和 `resizer_ps.ipynb`，保留所有输出及截图。报告实际的 PS/PL 时间、图像大小、输出是否相同，并说明是否包含 DMA、数据搬运和初始化。不要用 HLS 的内核时钟估计替代端到端测量。若当前包不提供 Arty bitstream，需选择课程支持的 Arty 镜像/版本或先为 Arty 重建示例，不能加载其他板卡的文件。

## 8. 异常现象与处理顺序

| 现象 | 先检查什么 | 需要保留什么 |
| --- | --- | --- |
| 电脑找不到串口 | USB 线是否能传数据、是否连接板载 USB-JTAG/UART 口、驱动与实际 COM 口；关闭占用串口的其他程序 | 设备管理器端口信息、接线照片 |
| 串口完全无输出 | 串口是否先打开；JP4 是否为 SD；专用卡 FAT32、根目录 BOOT.BIN 名称和哈希；更换已知可用卡或供电后冷启动 | 本次镜像哈希、卡片/供电/跳线信息；不要仅以无输出判断 FPGA 算法错误 |
| 出现乱码 | 115200 / 8N1 / 无流控是否一致 | 原始日志和终端设置截图 |
| 只看到标题或卡住 | 是否仍在运行；是否有 TIMEOUT；重新冷启动并完整捕获。已知继承 DDR DQS delay 提示需实物排查 | 从最早一行开始的日志，不只截最后一屏 |
| `TIMEOUT at 0x43c00000` | DCT/IDCT IP 无法完成；先确认仍在运行本次完整镜像，再看是否稳定复现 | 基地址、此前结果、镜像哈希；0x43c10000 对应 FIR |
| 非零 failures 或 DCT mismatch | 核对镜像；保留首次失败块/索引；冷启动复测，不把 FAIL 改写为 PASS | 整份原始日志及失败截图 |
| `f` CSV 少于 1024 行或没有末尾标记 | 是否已记录完整输出、终端缓冲/日志是否截断；另开日志单独复测 | 不完整原始文件和复测文件 |
| PYNQ 找不到 bit/HWH | 解压后目录相邻、同名 `.bit/.hwh` 都存在，Notebook 路径正确 | 文件列表、错误单元、PYNQ 版本 |
| PYNQ 访问异常、超时或无法导入 | 是否为 Arty 匹配镜像；重新创建 overlay/驱动；核对安装包版本，不假定其他板卡设计可用 | `BOARD`、Python/PYNQ 版本、完整错误输出 |
| PR Notebook 提示缺文件 | 当前发布没有 Arty 专用 PR 设计；应准备匹配设计后再执行 | 记录为未执行，不算已完成 Section 5.2 |

## 9. 完成标准与证据清单

| 项目 | 当前状态 |
| --- | --- |
| YUV/DCT/FIR 代码、输入、参考和仿真 | 已完成 |
| HLS 比较和内存截图、实验问题回答 | 已完成 |
| IDCT `output.dat` 与完整恢复图 | 已完成 |
| BOOT.BIN、bit/hwh、时序及镜像校验 | 已完成离线验证 |
| SD 启动与裸机串口自检 | 待实物验证 |
| Section 5.1 / 5.4 Notebook 的真实输出 | 待运行保存 |
| Section 5.2 Arty PR 设计与两张照片 | 待准备专用设计并上板 |
| Section 5.3 两个原始 resizer 的输出截图 | 待上板 |
| Section 6 FIR 上板波形与 Notebook 输出 | 待上板 |
| Peer evaluation | 根据实际分工本人填写，不自动编造 |

参考：[PYNQ 2.7 官方 Overlay Tutorial](https://pynq.readthedocs.io/en/v2.7.0/overlay_design_methodology/overlay_tutorial.html)、[手册所链接的 PR 示例](https://github.com/yunqu/partial_reconfig_example)。
