"""Package only deliverables and evidence, excluding generated tool workspaces."""
from pathlib import Path
import hashlib
import json
import zipfile

LAB=Path(__file__).resolve().parents[1]
release=LAB/'release'
release.mkdir(exist_ok=True)

def pack(path, entries):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for source,target in sorted(entries,key=lambda x:x[1]):
            z.write(source,target)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
    return {'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    boot=LAB/'boot/BOOT.BIN'
    manifest=json.loads((LAB/'boot/manifest.json').read_text())
    assert hashlib.sha256(boot.read_bytes()).hexdigest()==manifest['image']['sha256']
    tools_entries=[(LAB/'scripts/verify_board_log.py','verify_board_log.py'),
        (LAB/'tests/board_expected.json','board_expected.json'),
        (LAB/'tests/BOARD_TEST_RECORD.md','BOARD_TEST_RECORD.md')]
    summaries=[pack(release/'lab3_board_test_tools.zip',tools_entries)]
    sd_entries=[(boot,'BOOT.BIN'),(LAB/'boot/BOOT.sha256','BOOT.sha256'),
        (LAB/'boot/manifest.json','manifest.json'),(LAB/'QUICK_START.md','README.md'),
        (LAB/'ON_BOARD.md','lab3-test-guide.md'),(LAB/'tests/BOARD_TEST_RECORD.md','BOARD_TEST_RECORD.md')]
    sd_entries.extend((source,'tools/'+target) for source,target in tools_entries if target!='BOARD_TEST_RECORD.md')
    # BOOT.BIN is at the archive root for direct copying to a FAT32 card.
    summaries.append(pack(release/'lab3_arty_sd_test.zip',sd_entries))
    pynq_entries=[(LAB/'exported'/name,'exported/'+name) for name in ['lab3.bit','lab3.hwh']]
    pynq_entries.extend((p,'notebooks/'+p.name) for p in (LAB/'notebooks').iterdir() if p.is_file())
    pynq_entries.extend([(LAB/'ON_BOARD.md','lab3-test-guide.md'),(LAB/'QUICK_START.md','README.md')])
    summaries.append(pack(release/'lab3_pynq_test.zip',pynq_entries))
    entries=[]
    for folder in ['boot','exported','hls','software','tests','scripts','notebooks','images','report','logs','lab3_starter']:
        for source in (LAB/folder).rglob('*'):
            if not source.is_file():continue
            if any(part in {'__pycache__','pdf_preview','.ipynb_checkpoints'} for part in source.parts):continue
            if source.suffix in {'.o','.exe','.pyc','.log','.jou','.wdb','.wcfg'}:continue
            entries.append((source,'Lab3/'+source.relative_to(LAB).as_posix()))
    for name in ['README.md','ON_BOARD.md','QUICK_START.md','.gitignore']:
        entries.append((LAB/name,'Lab3/'+name))
    summaries.append(pack(release/'lab3_sources_and_evidence.zip',entries))
    (release/'manifest.json').write_text(json.dumps(summaries,indent=2)+'\n')
    print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
