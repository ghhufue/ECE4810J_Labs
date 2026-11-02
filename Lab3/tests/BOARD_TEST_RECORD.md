# Lab 3 上板测试记录

本表供实测后填写；未填写项不代表通过。

| 信息 | 记录 |
| --- | --- |
| 测试日期、测试人 | 2026-11-02，Zhao Tong（Group 2） |
| 板卡型号、硬件版本 | Digilent Arty Z7-20，XC7Z020-1CLG400C（与 PYNQ-Z1 同器件） |
| Release 标签、BOOT.BIN SHA-256 | `lab3-v0.1-hwtest`；BOOT.BIN `d8bbb6ef334717ea2141ec69f2e2cce13124493679193fa3f81ceb271b566f44`（本次未用裸机 SD 启动，见下方未执行项） |
| SD 卡及 FAT32 分区 | 64 GB SD 卡，`pynq_z1_v3.1.1.img` 以 Rufus DD 模式整卡写入 |
| JP4 位置、供电方式 | JP4 = SD（PYNQ 镜像启动）；USB PROG 口供电，USB 以太网线接 PC |
| 串口工具、COM 口、115200/8N1 | 未使用串口（本次全部通过网络访问 Jupyter）；板子地址 `192.168.137.42`，Jupyter 端口 9090 |
| PYNQ / Python / BOARD（如执行） | PYNQ 3.1.1，Python 3.10.4，`CPU: armv7l` |

| 测试项 | 实测结果 / PASS / FAIL / 未执行 | 日志或照片文件 |
| --- | --- | --- |
| 第一次冷启动，三项自检均零失败 | 未执行 | — |
| `t` 重跑自检，仍均零失败 | 未执行 | — |
| `d` 三个 8×8 矩阵逐项核对 | 未执行 | — |
| `f` 1024 行 FIR 数据核对 | 未执行 | — |
| 断电后第二次冷启动 | 未执行 | — |
| 第三次冷启动（建议） | 未执行 | — |
| verify_board_log.py 核对 | 未执行 | — |
| Section 5.1 基础 overlay 和 LED | PASS（`BaseOverlay("base.bit")` 加载成功，LD0 toggle 可见） | `report/screenshots/section5_1_lab3_1_output.png`、`notebooks/lab3_1.ipynb` |
| Section 5.4 加法器结果 7 / 9 / 35 | PASS（`3+4=7`、`4+5=9`、`Driver: 15+20=35`） | `report/screenshots/section5_4_lab3_3_output.png`、`notebooks/lab3_3.ipynb` |
| host_dct.ipynb | 未执行 | — |
| Section 6 host_fir.ipynb 与波形 | 未执行 | — |
| Section 5.2 PR 文件匹配及两张 LED 照片 | PASS（`0x5` = LD2+LD0 亮，`0xA` = LD3+LD1 亮） | `report/screenshots/section5_2_led_0x5.jpg`、`section5_2_led_0xA.jpg`、`section5_2_lab3_2_output.png`、`notebooks/lab3_2.ipynb` |
| Section 5.3 PS/PL resizer 与计时 | PASS（PL `247 ms per loop`，PS `1.1 s ± 195 µs per loop`，约 4.5×） | `report/screenshots/section5_3_resizer_pl.png`、`section5_3_resizer_ps.png` |

异常现象、复现步骤、尝试措施与结果：

```text
1) Overlay.pr_dict 为空，pr_download 抛 AttributeError
   现象：加载 gpio_pr.bit 后 overlay.pr_dict == {}，hierarchy_dict 不含 gpio_0；
        overlay.gpio_0 被解析为 DefaultIP，调用 pr_download 报
        AttributeError: 'DefaultIP' object has no attribute 'download'。
   原因：gpio_pr.hwh 由 Vivado 2018.3 导出，PYNQ 3.1 不再从该格式推导 PR 区域层级。
   措施：改用底层接口 pynq.bitstream.Bitstream(bit_path, partial=True) +
        Device.active_device.get_bitfile_metadata(..., partial=True)，
        由 fpga_manager 以 partial flag 编程；该步骤后面 PYNQ 会读 partial hwh 中的
        PS 条目并抛 KeyError('')，此时 PL 已编程完成，属无害收尾，已显式捕获。
   结果：LED 由 0x5 切到 0xA 正常，见 Section 5.2 的两张实物照片。

2) 板子上网不通
   现象：板子能 ping 通 PC（192.168.137.1），但 ping 8.8.8.8 100% 丢包。
   原因：Windows ICS 共享的「以太网」网卡 IPv4 Forwarding = Disabled。
   措施：重新关闭/开启 WLAN 的 Internet 连接共享，使 Forwarding 变 Enabled。
   结果：ip route 出现 default via 192.168.137.1，curl https://pypi.org 返回 HTTP/2 200。
```

最终结论与仍未完成的项目：

```text
Section 5（30%）已完成并通过上板实测：5.1 / 5.2 / 5.3 / 5.4 均有截图或实物照片，
5.5 的两问文字答案见 report/Section5_5_Answers.md。

仍未完成（本次未执行，不计为通过）：
- Section 2 / 3 的裸机 SD 启动与三项自检（未下载 Release 的 BOOT.BIN 实测）
- host_dct.ipynb
- Section 6（可选）host_fir.ipynb 与波形
```
