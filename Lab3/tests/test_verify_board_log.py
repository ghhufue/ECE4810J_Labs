"""Parser regression fixtures are synthetic and are not board evidence."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_board_log import check_log

REF=json.loads(Path(__file__).with_name('board_expected.json').read_text())
SUMMARY='''ADD RESULT: 36 tests, 0 failures
DCT/IDCT RESULT: 323 blocks, 41344 values, 0 failures
FIR RESULT: 1024 samples, 0 failures
LAB3 SELF-TEST: PASS
'''
MATRICES='Lena top-left block: input, DCT, recovered\n'+''.join(
    '\n'.join(' '.join(map(str,REF[k][r:r+8])) for r in range(0,64,8))+'\n\n'
    for k in ['lena_input','lena_dct','lena_idct'])
history=[0]*128;state=48103;rows=[]
for i in range(1024):
    state=(1664525*state+1013904223)&0xffffffff
    sample=(state>>24)-128
    history=[sample]+history[:-1]
    rows.append(f'{i},{sample},{sum(x*c for x,c in zip(history,REF["fir_coefficients"]))}')
FIR='FIR_CSV_BEGIN\nindex,input,output\n'+'\n'.join(rows)+'\nFIR_CSV_END\n'

class BoardLogChecks(unittest.TestCase):
    def test_summary_only(self):self.assertEqual(check_log(SUMMARY,REF)[0]['status'],'PASS')
    def test_full_session(self):
        report,blocks=check_log(SUMMARY+SUMMARY+MATRICES+FIR,REF,True,True)
        self.assertEqual(report['errors'],[])
        self.assertEqual(len(blocks[0]),1024)
    def test_failure_count(self):self.assertEqual(check_log(SUMMARY.replace('36 tests, 0','36 tests, 1'),REF)[0]['status'],'FAIL')
    def test_timeout(self):self.assertEqual(check_log(SUMMARY+'TIMEOUT at 0x43c00000',REF)[0]['status'],'FAIL')
    def test_wrong_matrix(self):self.assertEqual(check_log(SUMMARY+MATRICES.replace('10172','10173'),REF,True)[0]['status'],'FAIL')
    def test_truncated_csv(self):self.assertEqual(check_log(SUMMARY+FIR.replace('FIR_CSV_END',''),REF,False,True)[0]['status'],'FAIL')
    def test_wrong_fir(self):self.assertEqual(check_log(SUMMARY+FIR.replace('0,96,960','0,96,961'),REF,False,True)[0]['status'],'FAIL')
    def test_missing_required_data(self):self.assertEqual(check_log(SUMMARY,REF,True,True)[0]['status'],'FAIL')
    def test_partial_summary(self):self.assertEqual(check_log(SUMMARY.replace('ADD RESULT: 36 tests, 0 failures',''),REF)[0]['status'],'FAIL')

if __name__=='__main__':unittest.main()
