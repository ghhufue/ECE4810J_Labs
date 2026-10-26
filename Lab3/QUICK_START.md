# Lab 3：Arty Z7-20 镜像使用说明

本发布为 **待实板验证的测试版**。已完成离线仿真、100 MHz 布局布线、ARM 编译和启动镜像结构校验；当前未取得板上运行结果。

## 下载文件

- `BOOT.BIN`：裸机 SD 启动镜像，包含 FSBL、bitstream 和自检应用。
- `BOOT.sha256`、`manifest.json`：镜像校验信息。
- `lab3_arty_sd_test.zip`：镜像、说明和串口日志核对工具的组合包。
- `lab3-test-guide.md`：完整上板测试步骤、预期结果、截图清单及问题定位。
- `lab3_board_test_tools.zip`：日志核对脚本、固定参考数据和空白测试记录表。
- `lab3_pynq_test.zip`：后续 PYNQ 测试所需的 `.bit/.hwh`、Notebook 和输入数据。

无需安装 Vivado/Vitis 即可运行预编译的裸机镜像。仅支持 **Arty Z7-20 / xc7z020clg400-1**。

## 启动

1. 下载后核对 `BOOT.BIN` 的 SHA-256：

   ```powershell
   (Get-FileHash -LiteralPath .\BOOT.BIN -Algorithm SHA256).Hash.ToLower()
   ```

   应为 `d8bbb6ef334717ea2141ec69f2e2cce13124493679193fa3f81ceb271b566f44`，文件大小为 **4,313,672 字节**。
2. 准备专用 FAT32 SD 卡，将 `BOOT.BIN` **复制到根目录**。这是复制启动文件，不是将 BIN 作为整盘镜像烧录。保留原有 PYNQ 系统卡用于后续 Notebook 测试。
3. 板卡断电，将 **JP4 设为 SD**，插入 SD 卡，按实际供电方式设置电源选择跳线。
4. 使用可传输数据的 USB 线连接板载 USB-JTAG/UART 接口。在串口工具选择对应 COM 口，设置 **115200、8N1、无流控、本地回显关闭**，开启文本日志保存。
5. 先打开串口，再给板卡上电。若更改过启动跳线，重新断电上电，以重新采样启动模式。

## 通过标准

以下为**预期输出，不能作为实测截图**：

```text
ADD RESULT: 36 tests, 0 failures
DCT/IDCT RESULT: 323 blocks, 41344 values, 0 failures
FIR RESULT: 1024 samples, 0 failures
LAB3 SELF-TEST: PASS
```

| 命令 | 做什么 | 应得到什么 |
| --- | --- | --- |
| `t` | 重跑全部自检 | 再次输出上述四行，均为零失败 |
| `d` | 打印 Lena 的 8×8 输入、DCT、IDCT 三个矩阵 | IDCT 第一行为 `159 159 159 158 160 155 160 158`；完整值见测试指南 |
| `f` | 输出 FIR 测试数据 | `FIR_CSV_BEGIN` / `FIR_CSV_END` 之间有表头和 1024 行，首行 `0,96,960` |

命令输入一个小写字母即可，无需回车。若终端追加回车/换行，程序会重新显示菜单，不会增加一次测试。

**此裸机 BIN 不含 PYNQ Linux/Jupyter。** Section 5 和 FIR Notebook 需切换到与 Arty 匹配的 PYNQ 系统卡；详见 `lab3-test-guide.md`。
