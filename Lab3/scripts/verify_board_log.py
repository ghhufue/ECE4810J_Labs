"""Check a real board UART log. This program does not communicate with the board."""
import argparse
import csv
import json
from pathlib import Path
import re

def check_log(text, expected, require_dct=False, require_fir=False):
    errors=[]
    checks={}
    summaries={
        'add':r'ADD RESULT: (\d+) tests, (\d+) failures',
        'dct_idct':r'DCT/IDCT RESULT: (\d+) blocks, (\d+) values, (\d+) failures',
        'fir':r'FIR RESULT: (\d+) samples, (\d+) failures'}
    expected_counts={'add':(36,0),'dct_idct':(323,41344,0),'fir':(1024,0)}
    for name,pattern in summaries.items():
        matches=[tuple(map(int,m)) for m in re.findall(pattern,text)]
        checks[name+'_summaries']=len(matches)
        if not matches:errors.append('Missing '+name+' self-test summary')
        if any(m!=expected_counts[name] for m in matches):errors.append('Unexpected '+name+' count or nonzero failures')
    results=re.findall(r'LAB3 SELF-TEST: (PASS|FAIL)',text)
    checks['selftest_runs']=len(results)
    if not results or any(r!='PASS' for r in results):errors.append('Missing PASS or a self-test failed')
    if len({checks[n+'_summaries'] for n in summaries}|{len(results)})!=1:
        errors.append('Incomplete self-test output: summary counts do not agree')
    if re.search(r'TIMEOUT|DCT mismatch',text):errors.append('Timeout or mismatch present in UART log')

    matrices=[]
    marker='Lena top-left block: input, DCT, recovered'
    for tail in text.split(marker)[1:]:
        values=[]
        for line in tail.splitlines():
            line=line.strip()
            if re.fullmatch(r'-?\d+(?:\s+-?\d+)*',line):
                values.extend(map(int,line.split()))
                if len(values)>=192:break
            elif values and line and not re.match(r'^-?\d',line):break
        reference=sum([expected[n] for n in ['lena_input','lena_dct','lena_idct']],[])
        if values!=reference:errors.append('Lena matrix mismatch or incomplete d output')
        matrices.append(values)
    checks['lena_dumps']=len(matrices)
    if require_dct and not matrices:errors.append('Missing required d command matrix output')

    blocks=[]
    beginnings=text.count('FIR_CSV_BEGIN')
    for chunk in re.findall(r'FIR_CSV_BEGIN\s*(.*?)\s*FIR_CSV_END',text,re.S):
        try:
            reader=csv.reader(chunk.splitlines())
            if next(reader)!=['index','input','output']:raise ValueError('header')
            rows=[list(map(int,row)) for row in reader if row]
            history=[0]*128
            state=48103
            reference=[]
            for i in range(1024):
                state=(1664525*state+1013904223)&0xffffffff
                sample=(state>>24)-128
                history=[sample]+history[:-1]
                reference.append([i,sample,sum(x*c for x,c in zip(history,expected['fir_coefficients']))])
            if rows!=reference:errors.append('FIR CSV mismatch: expected exactly 1024 deterministic input/output rows')
            blocks.append(rows)
        except (ValueError,StopIteration):errors.append('Invalid FIR CSV block')
    checks['fir_csv_blocks']=len(blocks)
    if beginnings!=len(blocks):errors.append('Incomplete or invalid FIR CSV dump')
    if require_fir and not blocks:errors.append('Missing required f command CSV output')
    return {'status':'FAIL' if errors else 'PASS','checks':checks,'errors':errors},blocks

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path)
    local=Path(__file__).with_name('board_expected.json')
    parser.add_argument('--expected',type=Path,default=local if local.exists() else Path(__file__).resolve().parents[1]/'tests/board_expected.json')
    parser.add_argument('--output-dir',type=Path,default=Path('board_results'))
    parser.add_argument('--require-dct',action='store_true')
    parser.add_argument('--require-fir',action='store_true')
    args=parser.parse_args()
    expected=json.loads(args.expected.read_text(encoding='utf-8'))
    report,blocks=check_log(args.log.read_text(encoding='utf-8-sig',errors='replace'),expected,args.require_dct,args.require_fir)
    report['log_file']=str(args.log.resolve())
    report['expected_boot_sha256']=expected['boot_sha256']
    report['scope']='UART content verification only; verify the SD image hash and boot mode separately'
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'uart_check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    # Export captured values only after the entire log passes.
    if report['status']=='PASS' and blocks:
        with (args.output_dir/'fir_capture.csv').open('w',newline='') as out:
            writer=csv.writer(out);writer.writerow(['index','input','output']);writer.writerows(blocks[-1])
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
