"""Package the submission without downloaded data or private machine state."""
from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'23115002_submission.zip'
include=['README.md','PLAN_OF_ACTION.md','SUBMISSION.md','DATA_ATTRIBUTION.md','requirements.txt','requirements-lock.txt','reproduce.sh','.gitignore']
files=[ROOT/p for p in include]
for folder in ['src','tools','artifacts','report']:
    files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and not any(part.startswith('qa') for part in p.relative_to(ROOT).parts)]
files=sorted(set(files));manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,'23115002_ACV/'+str(p.relative_to(ROOT)))
    z.writestr('23115002_ACV/SUBMISSION_SHA256.json',json.dumps(manifest,indent=2))
print(OUT,OUT.stat().st_size,'bytes',len(files),'files')
