# Lab 3 - Section 5.5 Answers

> Measured on Digilent Arty Z7-20 (XC7Z020), PYNQ 3.1.1 image `pynq_z1_v3.1.1.img`,
> board IP `192.168.137.42`, Jupyter port 9090.

## 1. Advantages of using an overlay

An overlay bundles a bitstream, its `.hwh` metadata and a set of Python drivers into one
object, so the software side only sees a hardware-independent API. The concrete advantages
we relied on in this lab:

- **Encapsulation of the hardware interface.** `overlay.leds[0].toggle()` or
  `overlay.scalar_add.register_map.a = 3` hides the AXI base addresses, register offsets,
  IP versions and interrupt numbers. Nothing has to be hard-coded in the application.
- **Runtime loadable.** `Overlay("x.bit")` programmes the PL on demand
  (`overlay.download()`), so one SD card / one boot image can host many different hardware
  designs. No rebuild of `BOOT.BIN`, no reinstall of the OS.
- **Reusable and easy to distribute.** One overlay serves many notebooks and applications
  at the same time, and shipping a design only requires `*.bit` + `*.hwh` (+ optional
  Python drivers) instead of a full Vivado project. In this lab the whole Section 5 payload
  was a single `lab3.bit` / `lab3.hwh` pair.
- **Faster iteration and lower entry cost.** The hardware engineer delivers a bitstream; the
  algorithm developer debugs it in Jupyter with Python. Changing the software does not
  trigger a re-synthesis, and changing the hardware does not require a new application.
- **Self-describing hardware.** Because the `.hwh` records IP names, versions, address maps
  and interrupt lines, PYNQ can build `ip_dict`, `interrupt_pins` and `register_map` and
  expose `help()` introspection - that is exactly how the `scalar_add` driver was written in
  Section 5.4, without reading a single line of Verilog.
- **Partial reconfiguration support.** An accelerator inside a reconfigurable region can be
  swapped by downloading a partial bitstream (Section 5.2 switched `gpio_0` between the
  `led_5` and `led_a` personalities). The rest of the static design keeps running, so only
  the region that changes is reloaded.
- **One API for hardware and software implementations.** The same Python-level interface can
  front a PL accelerator or a plain software routine, which makes A/B comparison and fallback
  trivial - Section 5.3 runs `resizer_pl` and `resizer_ps` through the same notebook flow.
- **Portability across boards of the same device.** An overlay built for one board can be
  reused on another carrier with the same FPGA part and the same pinout; the PYNQ-Z1
  bitstreams used in this lab ran unchanged on the Arty Z7-20 (both XC7Z020, identical
  LD0-LD3 / switch / button pins).

## 2. Software vs. hardware acceleration: considerations and tradeoffs

Measured data from Section 5.3, bilinear downscale of one 3840x2160 RGBA frame to
1920x1080:

| Implementation | Notebook cell | Result |
| --- | --- | --- |
| PL accelerator (resizer) | `resizer_pl.ipynb`, `In [13]` | `1 loop, best of 3: 247 ms per loop` |
| Software (Pillow `Image.resize`) | `resizer_ps.ipynb`, `In [7]` | `1.1 s +- 195 us per loop (mean +- std. dev. of 7 runs, 1 loop each)` |

That is roughly **4.5x** for the hardware path - and the 247 ms figure is pessimistic, since
it already contains the DMA transfer of the input and output frames through DRAM.

Points to weigh before moving a kernel into the PL:

1. **Arithmetic intensity and available parallelism.** Hardware pays off when the kernel does
   many independent operations per data element (pixel-wise filtering, convolution, resize).
   A mostly sequential, branch-heavy algorithm gains little.
2. **Data movement cost.** Every frame must cross DDR and the AXI/DMA path. If the kernel is
   memory-bandwidth bound, the accelerator only removes compute time, so the speedup is
   capped by the transfer. This is why the PL measurement above still costs hundreds of
   milliseconds for a 33 MB frame.
3. **Amdahl's law.** Speedup is limited by the fraction of total runtime spent in the
   accelerated part. Only a kernel that dominates the profile justifies the effort.
4. **Operation granularity.** For tiny operations the interface overhead dominates: the
   Section 5.4 scalar add needs a few MMIO accesses (microseconds) and the Python call
   overhead is far larger than the arithmetic itself, so hardware gives no measurable win.
   Hardware wins on throughput, not on trivial call latency.
5. **Latency and determinism.** Real-time or hard-latency paths favour the PL because the
   datapath is fixed and cycle-accurate, whereas Linux + Python scheduling is non-deterministic.
6. **On-chip resources and power.** LUTs, FFs, DSPs and BRAM are finite; a large accelerator
   may not fit, may force a lower clock, or may need more power. Always compare performance
   per watt, not just wall-clock.
7. **Development and verification cost.** RTL/HLS design, verification and timing closure cost
   much more engineering time than a C/Python implementation. Algorithms that change often,
   or that are still being explored, are cheaper to keep in software.
8. **Numerical requirements.** Fixed-point hardware datapaths must be sized for range and
   precision, and bit-exactness against the software reference has to be proven; floating
   point is easier in software.
9. **Flexibility and product lifetime.** Software can be patched in the field; a bitstream
   change means a new release of the whole overlay, and (for partial reconfiguration) a
   compatible static design.

**Rule of thumb used in this lab:** move a kernel to hardware only when it is a dominant,
data-parallel, streaming hot spot whose arithmetic-to-byte ratio is high enough that the
acceleration survives the DMA cost - as the resizer does (247 ms vs 1.1 s). Keep everything
else in software, where it stays flexible and cheap to maintain.
