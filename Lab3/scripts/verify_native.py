"""Compile the real C implementation and compare against independent NumPy models."""
from pathlib import Path
import ctypes
import json
import os
import subprocess
import numpy as np
from PIL import Image
from prepare_data import LAB, START, basis, transform

BIN=Path('D:/Xilinx/Vitis_HLS/2022.1/tps/win64/msys64/mingw64/bin')
os.environ['PATH']=str(BIN)+os.pathsep+os.environ['PATH']
GCC=BIN/'gcc.exe'
def run(args,cwd):
    p=subprocess.run([str(x) for x in args],cwd=cwd,text=True,capture_output=True)
    print(p.stdout,end='')
    if p.returncode: raise RuntimeError(p.stderr+p.stdout)
    return p.stdout

def main():
    results=[]
    for name in ['dct','yuv']:
        src=START/('yuv_filter' if name=='yuv' else name)
        files=[src/('yuv_filter.c' if name=='yuv' else 'dct.c')]
        if name=='yuv': files.append(src/'image_aux.c')
        exe=LAB/'build'/f'test_{name}.exe'
        run([GCC,'-O2','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-label',
             '-I',src,*files,LAB/'tests'/f'test_{name}.c','-o',exe],src)
        results.append(run([exe],src))
    fir_src=START/'fir'
    fir_exe=LAB/'build/test_fir.exe'
    run([BIN/'g++.exe','-O2','-std=c++11','-Wall','-Wextra','-Werror','-Wno-unused-label',
         fir_src/'fir.cpp',LAB/'tests/test_fir.cpp','-o',fir_exe],fir_src)
    results.append(run([fir_exe],fir_src))
    src=START/'dct'
    dll=LAB/'build/dct_native.dll'
    run([GCC,'-O2','-shared','-std=c11',src/'dct.c','-o',dll],src)
    lib=ctypes.CDLL(str(dll))
    array=ctypes.c_short*64
    gray=np.array(Image.open(START/'lena_gray.bmp'),dtype=np.int64)
    rec=np.empty_like(gray)
    for y in range(0,512,8):
        for x in range(0,512,8):
            a=array(*map(int,gray[y:y+8,x:x+8].ravel())); b=array(); c=array()
            lib.dct(a,b);lib.idct(b,c)
            rec[y:y+8,x:x+8]=np.array(c).reshape(8,8)
    reference=np.array(Image.open(LAB/'images/lena_idct_reference.png'),dtype=np.int64)
    assert np.array_equal(np.clip(rec,0,255),reference)
    Image.fromarray(np.clip(rec,0,255).astype('uint8')).save(LAB/'images/lena_idct_recovered.png')
    rgb=np.loadtxt(START/'yuv_filter/output.dat',dtype='uint8').reshape(512,512,3)
    Image.fromarray(rgb).save(LAB/'images/lena_yuv_recovered.png')
    mse=float(np.mean((rec-gray)**2))
    results.append(f'Full image C DCT/IDCT: 4096 blocks, exact match to NumPy model, MSE={mse:.8f}, PSNR={10*np.log10(255**2/mse):.5f} dB\n')
    (LAB/'logs/native_verification.txt').write_text(''.join(results))
    print(results[-1],end='')

if __name__=='__main__': main()
