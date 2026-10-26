"""Generate reproducible inputs and independent integer reference vectors."""
from pathlib import Path
import json
import numpy as np
from PIL import Image

LAB = Path(__file__).resolve().parents[1]
START = LAB / 'lab3_starter'
def save(path, values):
    np.savetxt(path, np.asarray(values).reshape(-1), fmt='%d')

def basis():
    t = np.cos(np.pi * (2*np.arange(8)[None, :]+1)*np.arange(8)[:, None]/16)/2
    t[0] = 1/np.sqrt(8)
    return t

def transform(blocks, coeff, inverse=False):
    # Work on int64 independently of the C loop implementation.
    if inverse:
        rows = (blocks @ coeff) >> 16
        return (np.einsum('ij,...jk->...ik', coeff.T, rows)) >> 16
    rows = (blocks @ coeff.T + 4096) >> 13
    return (np.einsum('ij,...jk->...ik', coeff, rows) + 4096) >> 13

def yuv_reference(rgb, scales=(128,128,128)):
    matrix = np.array([[66,129,25],[-38,-74,112],[112,-94,-18]], dtype=np.int64)
    yuv = ((rgb.astype(np.int64) @ matrix.T + 128) >> 8) + [16,128,128]
    scaled = (yuv * np.array(scales)) >> 7
    shifted = scaled - [16,128,128]
    inv = np.array([[298,0,409],[298,-100,-208],[298,516,0]], dtype=np.int64)
    return np.clip((shifted @ inv.T + 128) >> 8, 0, 255)

def main():
    rgb = np.array(Image.open(START/'lena_std.tif').convert('RGB'))
    gray = np.array(Image.open(START/'lena_gray.bmp').convert('L'), dtype=np.int64)
    save(START/'yuv_filter/input.dat', rgb)
    save(START/'yuv_filter/output.golden.dat', yuv_reference(rgb))
    t = basis()
    scaled = t * 2**14.5
    coeff = (np.sign(scaled)*np.floor(np.abs(scaled)+0.5)).astype(np.int64)
    (START/'dct/dct_coeff_table.txt').write_text(',\n'.join(
        '{'+', '.join(map(str,row))+'}' for row in coeff)+'\n')
    first = gray[:8,:8]
    forward = transform(first, coeff)
    recover = transform(forward, coeff, True)
    save(START/'dct/input.dat', first)
    save(START/'dct/dct.golden.dat', forward)
    save(START/'dct/idct.golden.dat', recover)
    rng = np.random.default_rng(48103)
    blocks = [np.zeros((8,8),dtype=np.int64),np.full((8,8),255,dtype=np.int64), first]
    for index in range(64):
        impulse = np.zeros((8,8),dtype=np.int64)
        impulse.flat[index]=255
        blocks.append(impulse)
    blocks.extend(rng.integers(0,256,(256,8,8)))
    blocks = np.stack(blocks)
    fwd = transform(blocks, coeff)
    inv = transform(fwd, coeff, True)
    with (LAB/'tests/dct_vectors.h').open('w') as out:
        out.write('#ifndef LAB3_DCT_VECTORS_H\n#define LAB3_DCT_VECTORS_H\n')
        out.write(f'#define DCT_TEST_COUNT {len(blocks)}\n')
        for name,array in [('dct_inputs',blocks),('dct_expected',fwd),('idct_expected',inv)]:
            out.write(f'static const short {name}[DCT_TEST_COUNT][64] = {{\n')
            for block in array:
                out.write('{'+','.join(map(str,block.ravel()))+'},\n')
            out.write('};\n')
        out.write('#endif\n')
    # Full-image reconstruction is later checked against execution of the C code.
    tiles = gray.reshape(64,8,64,8).transpose(0,2,1,3)
    rec = transform(transform(tiles,coeff),coeff,True).transpose(0,2,1,3).reshape(512,512)
    Image.fromarray(np.clip(rec,0,255).astype('uint8')).save(LAB/'images/lena_idct_reference.png')
    metrics={'dct_blocks':len(blocks),'dct_values':int(blocks.size),
             'coefficient_orthogonality_error':float(np.max(np.abs(t@t.T-np.eye(8)))),
             'idct_full_image_max_error':int(np.max(np.abs(rec-gray))),
             'idct_full_image_mse':float(np.mean((rec-gray)**2)),
             'idct_shift':'arithmetic floor >>16, per manual',
             'input_order':'RGB interleaved, raster rows y then columns x'}
    (LAB/'logs/reference_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps(metrics,indent=2))

if __name__=='__main__': main()
