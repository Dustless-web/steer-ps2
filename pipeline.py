"""Batch orchestration: PDFs -> extraction -> live AI -> images -> optional reel."""
import argparse,json,time
from pathlib import Path
import engine
from video import render_video
p=argparse.ArgumentParser();p.add_argument('pdfs',nargs='+');p.add_argument('--video',choices=['none','local','neural'],default='none');a=p.parse_args()
if len(a.pdfs)>5:p.error('At most five PDFs per batch')
results=[]
for pdf in a.pdfs:
    started=time.perf_counter();run=None
    try:
        run=engine.ingest(pdf)['id'];engine.generate(run);engine.render(run)
        if a.video!='none':render_video(run,a.video=='neural')
        results.append(dict(file=pdf,run=run,status='awaiting_clinician',seconds=round(time.perf_counter()-started,2)))
    except Exception as err:results.append(dict(file=pdf,run=run,status='blocked',error=str(err)))
engine.write(engine.ROOT/'batch-result.json',results);print(json.dumps(results,indent=2))
