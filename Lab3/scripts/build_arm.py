"""Build the ARM application with the BSP generated from this Lab3 XSA."""
from pathlib import Path
import shutil
import subprocess

lab=Path(__file__).resolve().parents[1]
src=lab/'vitis_workspace/lab3_app/src'
out=lab/'vitis_workspace/lab3_app/Debug'
src.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
bsp=lab/'vitis_workspace/lab3_platform/export/lab3_platform/sw/lab3_platform/standalone_ps7_cortexa9_0'
tool=Path('D:/Xilinx/Vitis/2022.1/gnu/aarch32/nt/gcc-arm-none-eabi/bin')
for name in ['platform.c','platform.h','platform_config.h','Xilinx.spec']:
    shutil.copyfile(lab.parent/'Lab1/vitis_workspace/hello_rtl_divider/src'/name,src/name)
for name in ['lab3_app.c','lscript.ld']:
    shutil.copyfile(lab/'software'/name,src/name)
for name in ['dct_vectors.h','fir_coefficients.h']:
    shutil.copyfile(lab/'tests'/name,src/name)
for name in ['dct_accel','fir_accel','add']:
    header=lab/f'build/{name}/solution1/impl/ip/drivers/{name}_v1_0/src/x{name}_hw.h'
    shutil.copyfile(header,src/header.name)
flags=['-mcpu=cortex-a9','-mfpu=vfpv3','-mfloat-abi=hard']
def run(args):
    print(subprocess.list2cmdline([str(x) for x in args]),flush=True)
    subprocess.run([str(x) for x in args],cwd=src,check=True)
objects=[]
for name in ['lab3_app','platform']:
    obj=out/f'{name}.o'
    run([tool/'arm-none-eabi-gcc.exe',*flags,'-std=c11','-O2','-g3','-Wall','-Wextra','-Werror',
        '-I',bsp/'bspinclude/include','-I',src,'-c',src/f'{name}.c','-o',obj])
    objects.append(obj)
run([tool/'arm-none-eabi-gcc.exe',*flags,'-Wl,-build-id=none','-specs=Xilinx.spec',
    '-Wl,-T,'+str(src/'lscript.ld'),'-Wl,-Map,'+str(out/'lab3_app.map'),'-L',bsp/'bsplib/lib',
    '-o',out/'lab3_app.elf',*objects,'-Wl,--start-group','-lxil','-lgcc','-lc','-Wl,--end-group'])
run([tool/'arm-none-eabi-size.exe',out/'lab3_app.elf'])
print('LAB3_ARM_BUILD_PASS')
