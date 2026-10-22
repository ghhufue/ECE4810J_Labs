"""Compile with Vitis' ARM GCC and this XSA's BSP, without Eclipse app creation."""
from pathlib import Path
import shutil
import subprocess

lab=Path(__file__).resolve().parents[1]
app=lab/'vitis_workspace/hello_hls_rtl_alu'
src=app/'src'
out=app/'Debug'
src.mkdir(parents=True,exist_ok=True)
out.mkdir(exist_ok=True)
bsp=lab/'vitis_workspace/lab2_platform/export/lab2_platform/sw/lab2_platform/standalone_ps7_cortexa9_0'
tool=Path('D:/Xilinx/Vitis/2022.1/gnu/aarch32/nt/gcc-arm-none-eabi/bin')
gcc=tool/'arm-none-eabi-gcc.exe'
for name in ['platform.c','platform.h','platform_config.h','Xilinx.spec']:
    shutil.copyfile(lab.parent/'Lab1/vitis_workspace/hello_rtl_divider/src'/name,src/name)
for name in ['hls_rtl_alu.c','lscript.ld']:
    shutil.copyfile(lab/'software'/name,src/name)
shutil.copyfile(lab/'tests/alu_vectors.h',src/'alu_vectors.h')
hello=src/'helloworld.c'
if hello.exists(): hello.unlink()
flags=['-mcpu=cortex-a9','-mfpu=vfpv3','-mfloat-abi=hard']
def run(args):
    print(subprocess.list2cmdline([str(x) for x in args]),flush=True)
    subprocess.run([str(x) for x in args],cwd=src,check=True)
objects=[]
for name in ['hls_rtl_alu','platform']:
    obj=out/f'{name}.o'
    run([gcc,*flags,'-std=c11','-O2','-g3','-Wall','-Wextra','-Werror',
         '-I',bsp/'bspinclude/include','-I',src,'-c',src/f'{name}.c','-o',obj])
    objects.append(obj)
elf=out/'hello_hls_rtl_alu.elf'
run([gcc,*flags,'-Wl,-build-id=none','-specs=Xilinx.spec',
     '-Wl,-T,'+str(src/'lscript.ld'),'-Wl,-Map,'+str(out/'hello_hls_rtl_alu.map'),
     '-L',bsp/'bsplib/lib','-o',elf,*objects,'-Wl,--start-group','-lxil','-lgcc','-lc','-Wl,--end-group'])
run([tool/'arm-none-eabi-size.exe',elf])
print('LAB2_ARM_BUILD_PASS',flush=True)
