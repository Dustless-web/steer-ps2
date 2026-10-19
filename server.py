"""Loopback-only application server. No cloud deployment/authentication claims."""
import base64, json, mimetypes, os, tempfile, threading, uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, unquote
import engine

PORT=int(os.environ.get('PORT','8765'))
LOCK=threading.Lock()
JOBS={}
JOB_DIR=engine.ROOT/'logs'/'jobs'
JOB_DIR.mkdir(parents=True,exist_ok=True)
for saved in JOB_DIR.glob('*.json'):
    try:
        previous=engine.read(saved)
        if previous.get('status')=='running':
            previous.update(status='failed',error='Server restarted during generation. Your saved copy remains available; rebuild assets or retry generation.')
        JOBS[previous['id']]=previous
    except (ValueError,KeyError):
        pass

def save_job(job):
    engine.write(JOB_DIR/(job['id']+'.json'),job)

def snapshot(run):
    p=engine.folder(run)
    result={name:engine.read(p/(name+'.json')) if (p/(name+'.json')).exists() else None for name in ['source','pack','validation','review']}
    m=p/'assets'/'manifest.json'
    result['manifest']=engine.read(m) if m.exists() else None
    pack,r,manifest=result['pack'],result['review'],result['manifest']
    from creative import infer,STORIES,CHARACTERS,PROPS
    result['creative']=pack.get('creative') or infer(pack) if pack else None
    result['creative_catalog']={'story_type':STORIES,'character':CHARACTERS,'hero_prop':PROPS,'supporting_props':PROPS}
    result['video']=engine.read(p/'assets'/'video.json') if (p/'assets'/'video.json').exists() else None
    result['release_ready']=bool(pack and r and manifest and manifest['pack_version']==pack['version'] and r.get('version')==pack['version'] and r.get('final_assets') and r.get('reviewer') and r.get('asset_digest')==engine.digest(manifest) and set(r.get('decisions',{}))=={c['id'] for c in pack['claims']} and all(v=='approve' for v in r['decisions'].values()))
    return result

def work(job):
    try:
        if job['kind']=='pipeline':
            job['stage']='Generating evidence-linked copy...'
            engine.generate(job['run'])
        job['stage']='Choosing paper-specific artwork and rendering the playful story...'
        save_job(job)
        from video import render_video
        render_video(job['run'],False)
        job.update(status='done',stage='Content ready')
    except Exception as e:
        job.update(status='failed',error=str(e)[:500])
    finally:
        save_job(job)
        LOCK.release()

class Handler(BaseHTTPRequestHandler):
    def send(self,status,value,kind='application/json'):
        raw=json.dumps(value,ensure_ascii=False).encode() if kind=='application/json' else value
        self.send_response(status); self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store'); self.end_headers();self.wfile.write(raw)
    def serve_file(self,path):
        size=path.stat().st_size
        start,end=0,size-1
        partial=False
        requested=self.headers.get('Range')
        if requested:
            import re
            match=re.fullmatch(r'bytes=(\d*)-(\d*)',requested)
            if not match or not any(match.groups()):
                return self.send(416,{'error':'Invalid byte range'})
            a,b=match.groups()
            if a:
                start=int(a);end=min(int(b),end) if b else end
            else:
                start=max(0,size-int(b))
            if start>end or start>=size:
                self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return
            partial=True
        self.send_response(206 if partial else 200)
        self.send_header('Content-Type',mimetypes.guess_type(str(path))[0] or 'application/octet-stream')
        self.send_header('Content-Length',str(end-start+1))
        self.send_header('Accept-Ranges','bytes')
        self.send_header('Cache-Control','no-cache')
        self.send_header('X-Content-Type-Options','nosniff')
        if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        with path.open('rb') as stream:
            stream.seek(start);remaining=end-start+1
            while remaining>0:
                chunk=stream.read(min(65536,remaining))
                if not chunk:break
                try:self.wfile.write(chunk)
                except (BrokenPipeError,ConnectionResetError):break
                remaining-=len(chunk)

    def allowed(self):
        return self.headers.get('Host') in [f'127.0.0.1:{PORT}',f'localhost:{PORT}'] and self.headers.get('Origin') in [None,f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}']
    def do_GET(self):
        if not self.allowed(): return self.send(403,{'error':'Local origin required'})
        path=unquote(urlsplit(self.path).path)
        try:
            if path=='/api/status': return self.send(200,dict(**engine.provider_status(),reviewer_auth='local trusted operator; not verified clinician identity'))
            if path=='/api/runs':
                items=[]
                for p in sorted(engine.RUNS.glob('*/source.json'),key=lambda p:p.stat().st_mtime,reverse=True):
                    x=snapshot(p.parent.name); pack=x['pack']
                    items.append(dict(id=p.parent.name,filename=x['source']['filename'],title=pack.get('title') if pack else None,stage='Approved' if x['release_ready'] else 'Awaiting review' if pack else 'Source extracted'))
                return self.send(200,items)
            if path=='/api/jobs': return self.send(200,[j for j in JOBS.values() if j['status']=='running'])
            if path.startswith('/api/jobs/'):
                job=JOBS.get(path.split('/')[-1])
                return self.send(200,job) if job else self.send(404,{'error':'Job not found. The server may have restarted; open your saved paper to continue.'})
            if path.startswith('/api/run/'):
                return self.send(200,snapshot(path.split('/')[-1]))
            if path.startswith('/runs/'):
                bits=path.strip('/').split('/'); p=engine.folder(bits[1]); rel='/'.join(bits[2:]); candidate=(p/rel).resolve()
                if p.resolve() not in candidate.parents or candidate.suffix not in ['.png','.mp4','.wav','.txt','.zip','.pdf','.json']: return self.send(403,{'error':'File not allowed'})
            else:
                if path in ['/engine.html','/index.html']:
                    self.send_response(302);self.send_header('Location','/');self.end_headers();return
                if path=='/': path='/index.html'
                if path.strip('/') not in ['index.html','app.css','app.js']: return self.send(404,{'error':'Not found'})
                candidate=engine.ROOT/path.strip('/')
            if candidate.name=='approved-review-package.zip' and not snapshot(bits[1])['release_ready']: return self.send(403,{'error':'Package is no longer approved. Review the current content.'})
            self.serve_file(candidate)
        except (ValueError,FileNotFoundError,IndexError): self.send(404,{'error':'Not found'})
    def do_POST(self):
        if not self.allowed(): return self.send(403,{'error':'Local origin required'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<36*1024*1024: return self.send(413,{'error':'Request too large or empty'})
            data=json.loads(self.rfile.read(size)); path=urlsplit(self.path).path
            if path=='/api/jobs':
                engine.folder(data['id'])
                if data.get('kind') not in ['pipeline','assets']: raise ValueError('Unknown job type')
                if not LOCK.acquire(blocking=False): return self.send(409,{'error':'A content job is already running. Wait for it to finish.'})
                job=dict(id=uuid.uuid4().hex,run=data['id'],kind=data['kind'],status='running',stage='Preparing content...')
                JOBS[job['id']]=job
                save_job(job)
                threading.Thread(target=work,args=(job,),daemon=True).start()
                return self.send(202,job)
            if not LOCK.acquire(blocking=False): return self.send(409,{'error':'A content job is running. Wait before changing or exporting content.'})
            self.mutation_locked=True
            if path=='/api/ingest':
                raw=base64.b64decode(data['pdf'],validate=True)
                with tempfile.TemporaryDirectory(prefix='steer-upload-',dir=engine.ROOT) as temp:
                    f=Path(temp)/'upload.pdf';f.write_bytes(raw); result=engine.ingest(f)
                p=engine.folder(result['id']); result['filename']=Path(data.get('filename','upload.pdf')).name;engine.write(p/'source.json',result)
            elif path=='/api/generate': result=engine.generate(data['id'])
            elif path=='/api/render': result=engine.render(data['id'])
            elif path=='/api/video':
                from video import render_video
                if data.get('neural'): raise ValueError('The playful style uses sound effects and does not require narration.')
                result=render_video(data['id'],bool(data.get('neural',False)))
            elif path=='/api/edit':
                p=engine.folder(data['id']); current=engine.read(p/'pack.json')
                if data['version']!=current['version']: raise ValueError('Content changed; reload first')
                result=engine.save_pack(data['id'],data['pack'])
            elif path=='/api/review': result=engine.review(data['id'],data['review'])
            elif path=='/api/release': result=engine.release(data['id'])
            else: return self.send(404,{'error':'Unknown operation'})
            self.send(200,result)
        except Exception as e:
            # Never return upstream request bodies or credentials.
            self.send(400,{'error':str(e)[:500]})
        finally:
            if getattr(self,'mutation_locked',False):
                self.mutation_locked=False
                LOCK.release()
if __name__=='__main__':
    engine.RUNS.mkdir(exist_ok=True)
    print(f'Steer engine: http://127.0.0.1:{PORT}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
