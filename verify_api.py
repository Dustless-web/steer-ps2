"""Exercise the real local HTTP app without approving any medical content."""
import base64,json,time,urllib.request,urllib.error
from pathlib import Path
def request(path,data=None):
    r=urllib.request.Request('http://127.0.0.1:8765/api/'+path,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(r,timeout=20) as res:return res.status,json.load(res)
    except urllib.error.HTTPError as err:return err.code,json.load(err)
start=time.perf_counter();status,config=request('status');assert status==200
status,source=request('ingest',{'filename':'resistance-review.pdf','pdf':base64.b64encode(Path('sources/resistance-review.pdf').read_bytes()).decode()});assert status==200 and len(source['pages'])==14
status,loaded=request('run/'+source['id']);assert status==200 and loaded['pack'] is None
ids=json.loads(Path('sample-runs.json').read_text());status,blocked=request('release',{'id':ids['resistance']});assert status==400
report=dict(at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),elapsed_seconds=round(time.perf_counter()-start,2),status='passed',checks=['HTTP status','PDF upload and 14-page extraction','persisted source reload','unapproved release rejected'],ai_configured=config['ai_configured'],upload_run=source['id'],release_rejection=blocked)
Path('verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
