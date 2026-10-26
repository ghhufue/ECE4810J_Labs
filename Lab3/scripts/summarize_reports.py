"""Extract values directly from Vitis XML; never copy reference screenshot numbers."""
from pathlib import Path
import csv
import json
import shutil
import xml.etree.ElementTree as ET

LAB=Path(__file__).resolve().parents[1]
def metrics(path):
    root=ET.parse(path).getroot()
    def get(p):
        text=root.findtext(p)
        if text is None:return None
        try:return int(text)
        except ValueError:
            try:return float(text)
            except ValueError:return text
    prefix='PerformanceEstimates/'
    values={'clock_ns':get(prefix+'SummaryOfTimingAnalysis/EstimatedClockPeriod'),
        'latency_min':get(prefix+'SummaryOfOverallLatency/Best-caseLatency'),
        'latency_max':get(prefix+'SummaryOfOverallLatency/Worst-caseLatency'),
        'interval_max':get(prefix+'SummaryOfOverallLatency/Interval-max')}
    values.update({key:get('AreaEstimates/Resources/'+key) for key in ['BRAM_18K','DSP','FF','LUT']})
    return values

def main():
    all_metrics={}
    for family,top in [('yuv','yuv_filter'),('dct','dct'),('fir','fir')]:
        all_metrics[family]={}
        for path in sorted((LAB/'logs'/family).glob(f'*/{top}_csynth.xml')):
            all_metrics[family][path.parent.name]=metrics(path)
        rows=[{'solution':sol,**m} for sol,m in all_metrics[family].items()]
        with (LAB/'report'/f'{family}_comparison.csv').open('w',newline='') as out:
            writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    all_metrics['yuv_baseline_functions']={}
    for name in ['yuv_filter','rgb2yuv_1','yuv2rgb_1']:
        all_metrics['yuv_baseline_functions'][name]=metrics(LAB/f'logs/yuv/solution1/{name}_csynth.xml')
    for family,sols in [('dct.prj',['solution1','solution5']),('dct_accel',['solution1']),('fir_accel',['solution1'])]:
        top=family.replace('.prj','')
        for sol in sols:
            dest=LAB/'logs/cosim'/top/sol;dest.mkdir(parents=True,exist_ok=True)
            for source in (LAB/f'build/{family}/{sol}/sim/report').glob('*.rpt'):
                shutil.copyfile(source,dest/source.name)
    (LAB/'report/hls_metrics.json').write_text(json.dumps(all_metrics,indent=2)+'\n')
    for family in ['yuv','dct','fir']:
        print(family, json.dumps(all_metrics[family]))

if __name__=='__main__':main()
