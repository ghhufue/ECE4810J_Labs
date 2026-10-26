"""Author board notebooks without inventing outputs from unavailable hardware."""
from pathlib import Path
import ast
import json
import numpy as np
from prepare_data import LAB, START

def md(text): return {'cell_type':'markdown','metadata':{},'source':text.splitlines(True)}
def code(text):
    ast.parse(text)
    return {'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':text.splitlines(True)}
def notebook(name,cells):
    doc={'nbformat':4,'nbformat_minor':4,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.10'},'lab3_execution':'Pending: board unavailable'},'cells':cells}
    (LAB/'notebooks'/name).write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def main():
    notebook('lab3_1.ipynb',[
        md('# Lab 3.1 - Base overlay\nRun on the Arty Z7-20 PYNQ image. Outputs are intentionally empty until execution on the board.'),
        code('import os, platform, pynq\nprint("Board:", os.environ.get("BOARD"), "PYNQ:", pynq.__version__, "CPU:", platform.machine())'),
        code('from pynq.overlays.base import BaseOverlay\nbase_overlay = BaseOverlay("base.bit")\nassert base_overlay.is_loaded()\nhelp(base_overlay)'),
        code('help(base_overlay.leds)\nbase_overlay.leds[0].toggle()\nprint("LD0 toggled; verify on the board.")'),
        code('if hasattr(base_overlay, "video"):\n    help(base_overlay.video)\nelse:\n    print("This board image exposes no video hierarchy.")')])
    notebook('lab3_2.ipynb',[
        md('# Lab 3.2 - Partial reconfiguration\nRequires a full design and two partial bitstreams built for **Arty Z7-20**, with matching HWH metadata. The manual links PYNQ-Z1 files; do not load those onto Arty. This delivery contains a full overlay only, not partial configurations. Place board-matched PR files in `partial_reconfig/` when available.'),
        code('from pathlib import Path\nfrom pynq import Overlay\nfrom pprint import pprint\nfolder = Path("partial_reconfig")\nrequired = [folder/name for name in ["gpio_pr.bit", "gpio_pr.hwh", "led_5.bit", "led_5.hwh", "led_a.bit", "led_a.hwh"]]\nassert all(p.exists() for p in required), "Provide Arty-specific full and partial files before running."'),
        code('overlay = Overlay(str(folder/"gpio_pr.bit"))\noverlay.download()\npprint(overlay.interrupt_pins)\npprint(overlay.pr_dict)'),
        code('assert "gpio_0" in overlay.pr_dict\noverlay.pr_download("gpio_0", str(folder/"led_5.bit"))\nprint("Capture a real board photo of LED pattern 0x5 now.")'),
        code('overlay.pr_download("gpio_0", str(folder/"led_a.bit"))\nprint("Capture a second real board photo of LED pattern 0xA now.")')])
    notebook('lab3_3.ipynb',[
        md('# Lab 3.3 - Custom Arty overlay and driver\nStart a PYNQ Linux SD image, then copy this `notebooks/` directory beside `exported/`. Loading `lab3.bit` replaces the PL configuration. The separate bare-metal BOOT.BIN does not run Jupyter.'),
        code('from pynq import Overlay, DefaultIP\nfrom pathlib import Path\nbit = Path("../exported/lab3.bit")\nassert bit.exists() and bit.with_suffix(".hwh").exists()\noverlay = Overlay(str(bit))\nprint(overlay.ip_dict)\nassert overlay.is_loaded()'),
        code('add_ip = overlay.scalar_add\nprint(add_ip.register_map)\nadd_ip.register_map.a = 3\nadd_ip.register_map.b = 4\nassert int(add_ip.register_map.c) == 7\nprint("3 + 4 =", int(add_ip.register_map.c))\nadd_ip.write(0x10, 4)\nadd_ip.write(0x18, 5)\nassert add_ip.read(0x20) == 9\nprint("4 + 5 =", add_ip.read(0x20))'),
        code('class AddDriver(DefaultIP):\n    bindto = ["xilinx.com:hls:add:1.0"]\n    def __init__(self, description):\n        super().__init__(description=description)\n    def add(self, a, b):\n        self.write(0x10, a & 0xffffffff)\n        self.write(0x18, b & 0xffffffff)\n        return self.read(0x20)\n\noverlay = Overlay(str(bit))\nresult = overlay.scalar_add.add(15, 20)\nassert result == 35\nprint("Driver: 15 + 20 =", result)')])
    coeff=[int(v) for v in (LAB/'tests/fir_coefficients.h').read_text().split(',')]
    notebook('host_fir.ipynb',[
        md('# Optional 128-tap FIR on Arty\nResults and plots below are generated only by a real board run. The reference uses the supplied 128 coefficients. AXI word transfer overhead is included in elapsed host time.'),
        code('import time\nimport numpy as np\nimport matplotlib.pyplot as plt\nfrom pynq import Overlay\noverlay = Overlay("../exported/lab3.bit")\nfir_ip = overlay.fir_accel_0\nprint(fir_ip.register_map)'),
        code('def step(sample, clear=0):\n    fir_ip.write(0x10, int(sample) & 0xffffffff)\n    fir_ip.write(0x18, int(clear))\n    fir_ip.write(0, 1)\n    deadline = time.monotonic() + 1\n    while not (fir_ip.read(0) & 2):\n        if time.monotonic() > deadline:\n            raise TimeoutError("FIR ap_done timeout")\n    value = fir_ip.read(0x20)\n    return value if value < 2**31 else value - 2**32'),
        code(f'coefficients = np.array({coeff!r}, dtype=np.int64)\nassert len(coefficients) == 128\nsignal = np.loadtxt("fir_input.dat", dtype=np.int64)\nstep(0, clear=1)\nstart = time.perf_counter()\nfiltered = np.array([step(int(x)) for x in signal], dtype=np.int64)\nelapsed = time.perf_counter() - start\nexpected = np.convolve(signal, coefficients)[:len(signal)]\nnp.testing.assert_array_equal(filtered, expected)\nprint(f"FIR PASS: {{len(signal)}} samples, host elapsed {{elapsed:.6f}} s")\nnp.savetxt("fir_board_output.dat", filtered, fmt="%d")'),
        code('fig, axes = plt.subplots(2, 1, sharex=True, figsize=(10,6))\naxes[0].plot(signal); axes[0].set_ylabel("Input")\naxes[1].plot(filtered); axes[1].set_ylabel("128-tap output"); axes[1].set_xlabel("Sample")\nfig.tight_layout(); fig.savefig("fir_board_plot.png", dpi=180)\nplt.show()')])
    import shutil
    shutil.copyfile(START/'fir/input.dat', LAB/'notebooks/fir_input.dat')
    np.savez(LAB/'notebooks/dct_reference.npz',input=np.loadtxt(START/'dct/input.dat',dtype=np.int32),
        forward=np.loadtxt(START/'dct/dct.golden.dat',dtype=np.int32),inverse=np.loadtxt(START/'dct/idct.golden.dat',dtype=np.int32))
    notebook('host_dct.ipynb',[
        md('# DCT/IDCT on Arty\nUses the exact fixed-point reference generated from the supplied Lena block.'),
        code('import time\nimport numpy as np\nfrom pynq import Overlay\noverlay = Overlay("../exported/lab3.bit")\nip = overlay.dct_accel_0\nreference = np.load("dct_reference.npz")\nprint(ip.register_map)'),
        code('def transform(data, inverse=0):\n    for i,x in enumerate(data):\n        ip.write(0x100+4*i, int(x) & 0xffffffff)\n    ip.write(0x10, inverse)\n    ip.write(0, 1)\n    deadline = time.monotonic()+1\n    while not (ip.read(0) & 2):\n        if time.monotonic()>deadline:\n            raise TimeoutError("DCT ap_done timeout")\n    result = np.array([ip.read(0x200+4*i) for i in range(64)],dtype=np.uint32).view(np.int32)\n    return result\nforward = transform(reference["input"])\nrecovered = transform(forward, 1)\nnp.testing.assert_array_equal(forward, reference["forward"])\nnp.testing.assert_array_equal(recovered, reference["inverse"])\nprint("DCT/IDCT PASS")\nprint(recovered.reshape(8,8))')])
    print('Created 5 notebooks; all code cells parse; hardware execution pending.')

if __name__=='__main__': main()
