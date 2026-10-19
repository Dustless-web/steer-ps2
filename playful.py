"""Paper-aware comic layouts and continuous, sound-optional research animations."""
import math,json,hashlib,subprocess,wave,struct
from pathlib import Path
from PIL import Image,ImageDraw
import engine as e
import playful_art as a
from creative import infer

VERSION='playful-v1'
def plan(pack):return pack.get('creative') or infer(pack)

def fit(d,value,box,size=90,bold=True,color=a.R):
 x,y,w,h=box
 for n in range(size,min(26,size)-1,-2):
  rows=[]
  for para in value.split('\n'):rows+=e.wrap(d,para,a.ft(n,bold),w)
  if len(rows)*n*1.17<=h and all(d.textlength(row,font=a.ft(n,bold))<=w for row in rows):break
 else:raise ValueError('Copy does not fit the playful layout. Shorten this headline or body.')
 for row in rows:d.text((x,y),row,font=a.ft(n,bold),fill=color);y+=n*1.17
 return y

def dotted(d,start,end):
 x,y=start;xx,yy=end;dist=math.hypot(xx-x,yy-y)
 for i in range(0,int(dist),26):
  t=i/max(dist,1);u=min(1,(i+10)/max(dist,1));d.line((x+(xx-x)*t,y+(yy-y)*t,x+(xx-x)*u,y+(yy-y)*u),fill=a.M,width=5)

def world(im,pack,progress,t=0,compact=False):
 c=plan(pack);family=c['story_type'];w,h=im.size;d=ImageDraw.Draw(im)
 y=860 if h==1350 else 740 if h==1080 else 1200
 scale=(.55 if h==1080 else .73) if compact else 1
 phase=a.ease(.06,.27,progress)*(1-a.ease(.91,1,progress))
 hero=a.prop(c['hero_prop']);extras=[a.prop(k) for k in c['supporting_props']]
 char=a.character(c['character'],t*8,-1)
 # Actors and props share a continuous set; coordinates vary by research design.
 hx=a.lerp(520,185,phase);hs=a.lerp(570,310,phase)*scale
 a.place(im,hero,hx,y+math.sin(t*2)*6,hs,-4+math.sin(t)*2)
 actorx=a.lerp(1180,850,a.ease(0,.2,progress));actorx=a.lerp(actorx,1180,a.ease(.92,1,progress))
 a.place(im,char,actorx,y+100-abs(math.sin(t*5))*9,340*scale,math.sin(t*2)*3)
 if phase>.02:
  if family=='comparison':
   for j,obj in enumerate(extras if len(extras)==2 else [extras[0],hero]):
    a.place(im,obj,390+j*285,y-130+(1-phase)*350,245*scale,math.sin(t+j)*3)
   dotted(d,(480,y+70),(590,y+70))
  elif family=='association':
   # Dots connect co-observed objects without a directional causal arrow.
   p1=(370,y-130+math.sin(t)*20);p2=(700,y-90+math.cos(t)*20)
   dotted(d,p1,p2);a.place(im,extras[0],*p1,240*scale);a.place(im,hero,*p2,220*scale)
   a.place(im,a.GLASS,535+math.sin(t)*100,y+40,170*scale,10)
  elif family=='timeline':
   points=[(330,y-90),(530,y-150),(730,y-90)]
   for u,v in zip(points,points[1:]):dotted(d,u,v)
   for x,yy in points:d.ellipse((x-12,yy-12,x+12,yy+12),fill=a.R)
   track=(progress*2)%1;a.place(im,extras[0],330+400*track,y-220,200*scale,0)
  elif family=='mechanism':
   a.place(im,extras[0],550,y-100,330*scale,math.sin(t)*5)
   a.place(im,a.GLASS,560+math.sin(t*1.3)*100,y-90+math.cos(t*1.3)*70,230*scale,math.sin(t)*15)
  elif family=='review':
   for j in range(3):a.place(im,a.prop('book'),365+j*125,y-100+math.sin(t+j)*10,220*scale,(j-1)*12)
   a.place(im,a.GLASS,550+math.sin(t)*100,y-70,230*scale,-10)
  elif family=='methods':
   a.place(im,extras[0],500,y-60,330*scale,math.sin(t)*4)
   a.place(im,a.prop('chip'),620,y-230+math.sin(t*2)*25,170*scale,math.sin(t)*9)
  elif family=='qualitative':
   for j in range(3):
    x=330+j*145;yy=y-160+math.sin(t+j)*25
    d.rounded_rectangle((x-45,yy-45,x+70,yy+35),radius=25,fill=a.P,outline=a.I,width=3)
    for dot in range(3):d.ellipse((x-20+dot*24,yy-8,x-12+dot*24,yy),fill=a.M)
   a.place(im,extras[0],540,y+60,220*scale)
  else:
   a.place(im,a.prop('question'),540,y-90,300*scale,math.sin(t)*6)
   a.place(im,a.GLASS,530+math.sin(t)*120,y+40,180*scale,-15)


def footer(im,block,pack,number):
 d=ImageDraw.Draw(im);h=im.height;d.rectangle((0,h-118,1080,h),fill=a.C)
 refs=[c for c in pack['claims'] if c['id'] in block.get('claim_ids',[])]
 line=' · '.join(f"{c['id']}/p.{c['page']}" for c in refs) or 'Editorial question'
 fit(d,line,(64,h-105,940,35),21,False,a.M)
 d.text((64,h-60),'steerclub.com',font=a.ft(23,True),fill=a.I)
 d.text((410,h-55),'Illustration · review draft',font=a.ft(18),fill=a.M)
 d.text((955,h-60),number,font=a.ft(23,True),fill=a.R)

def text_layer(block,size):
 im=a.backdrop(*size);d=ImageDraw.Draw(im);w,h=size
 d.text((64,54 if h<1500 else 90),'steer',font=e.font(43,True),fill=a.R)
 if h==1920:
  y=fit(d,block['headline'],(64,230,952,300),98)
  fit(d,block.get('body',''),(64,y+25,952,260),41,False,a.I)
 elif h==1350:
  y=fit(d,block['headline'],(64,160,952,245),99)
  fit(d,block.get('body',''),(64,y+18,952,190),36,False,a.I)
 else:
  y=fit(d,block['headline'],(64,145,952,200),79)
  fit(d,block.get('body',''),(64,y+12,952,165),33,False,a.I)
 return im

_TEXT_LAYERS={}
def frame(pack,block,progress,t=0,size=(1080,1920),number=''):
 key=(block['headline'],block.get('body',''),size)
 if key not in _TEXT_LAYERS:
  if len(_TEXT_LAYERS)>=64:_TEXT_LAYERS.clear()
  _TEXT_LAYERS[key]=text_layer(block,size)
 im=_TEXT_LAYERS[key].copy()
 world(im,pack,progress,t,compact=size[1]<1920)
 footer(im,block,pack,number)
 return im.convert('RGB')

def render_card(block,path,size,index,source,pack):
 if size[1]==1080:n=2;total=5
 else:n=int(index.split('/')[0])-1;total=len(pack['reel'] if size[1]>1500 else pack['carousel'])
 progress=(n+.55)/total
 frame(pack,block,progress,t=progress*20,size=size,number=f'{n+1:02}').save(path)

def sound(path,duration,cuts):
 rate=24000;out=bytearray()
 for i in range(round(duration*rate)):
  t=i/rate;v=0
  for j,start in enumerate(cuts):
   z=t-start
   if 0<=z<.18:v+=.13*math.sin(2*math.pi*((330+j*55)*z-90*z*z))*math.exp(-z*22)
  out.extend(struct.pack('<h',int(max(-1,min(1,v))*32767)))
 with wave.open(str(path),'wb') as wav:wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(out)

def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def render_video(run,neural=False):
 if neural:raise ValueError('The playful style uses optional sound effects, not narration.')
 from video import executable
 e.render(run);p=e.folder(run);pack=e.read(p/'pack.json');out=p/'assets'
 blocks=pack['reel'];durations=[max(4.5,2+len((b['headline']+' '+b['body']).split())*.34) for b in blocks]
 cuts=[];elapsed=0;subs=[]
 for b,length in zip(blocks,durations):
  cuts.append(elapsed);subs.append(f'{len(cuts)}\n{stamp(elapsed)} --> {stamp(elapsed+length)}\n{b["headline"]}\n{b["body"]}\n');elapsed+=length
 total=elapsed;sound(out/'playful-sfx.wav',total,cuts)
 args=[executable(),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','pipe:0','-i',str((out/'playful-sfx.wav').resolve()),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart','-shortest',str((out/'playful-pending.mp4').resolve())]
 with (out/'animation-error.log').open('wb') as log:
  proc=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
  try:
   for i in range(math.ceil(total*24)):
    t=i/24;which=max(j for j,start in enumerate(cuts) if start<=t)
    proc.stdin.write(frame(pack,blocks[which],min(1,t/total),t,number=f'{which+1:02}').tobytes())
   proc.stdin.close()
   if proc.wait(timeout=120):raise ValueError('Animation encoding failed; see animation-error.log')
  except Exception:proc.kill();proc.wait();raise
 (out/'playful-pending.mp4').replace(out/'reel.mp4')
 (out/'reel.srt').write_text('\n'.join(subs),encoding='utf-8')
 metadata=dict(visual_style=VERSION,creative=pack['creative'],duration_seconds=round(total,2),narration='None',audio='Original synthetic sound effects; works muted',disclosure='Conceptual illustration, not simulated outcomes',captions='On-screen copy; SRT timings follow each story beat',copy_provenance=pack.get('provenance',{}))
 e.write(out/'video.json',metadata);e.write(out/'creative.json',pack['creative'])
 manifest=e.read(out/'manifest.json');manifest['files'].update({name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['reel.mp4','reel.srt','video.json','creative.json']});e.write(out/'manifest.json',manifest)
 e.log(p,'video_rendered',visual_style=VERSION,duration_seconds=round(total,2),story_type=pack['creative']['story_type'])
 return metadata
