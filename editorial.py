"""Steer editorial artwork and independently animated reel layers."""
from PIL import Image, ImageDraw
import engine as e
CREAM='#F5EBDF';RUST='#C04E2A';INK='#351D1D';CLAY='#946B5B';BLUSH='#E6CBBD';PAPER='#F8F2EB'

def text(d,value,box,size=64,serif=False,italic=False,color=INK):
    x,y,w,h=box
    for n in range(size,21,-2):
        f=e.font(n,serif,italic);lines=e.wrap(d,value,f,w);step=int(n*1.28)
        if len(lines)*step<=h and all(d.textlength(line,font=f)<=w for line in lines):break
    else:raise ValueError('Copy exceeds editorial layout; shorten the text.')
    for line in lines:d.text((x,y),line,font=f,fill=color);y+=step
    return y

def motif(d,x,y,w,kind=0):
    # Abstract editorial line art, never a data chart or a medical diagram.
    if kind%3==0:
        for offset in [0,35,70]:d.rounded_rectangle((x+offset,y+offset,x+w-70+offset,y+w*.55+offset),radius=16,outline=CLAY,width=3)
        d.line((x+55,y+80,x+w-105,y+80),fill=RUST,width=6)
        d.line((x+55,y+110,x+w-150,y+110),fill=BLUSH,width=6)
    elif kind%3==1:
        for offset in range(0,100,22):d.arc((x+offset,y,x+w,y+w-offset),20,310,fill=RUST,width=3)
        d.ellipse((x+w*.43,y+w*.43,x+w*.57,y+w*.57),fill=BLUSH)
    else:
        for i in range(3):
            xx=x+i*w/3;d.ellipse((xx,y+i*30,xx+85,y+85+i*30),outline=CLAY,width=3)
        d.line((x+40,y+150,x+w-40,y+150),fill=BLUSH,width=3)

def footer(d,w,h,block,pack,number):
    d.line((76,h-168,w-76,h-168),fill=BLUSH,width=2)
    refs=[c for c in pack['claims'] if c['id'] in block['claim_ids']]
    citation=' · '.join(f"{c['id']} / p.{c['page']}" for c in refs) or 'An invitation to reflect'
    text(d,citation,(76,h-148,w-152,30),22,color=CLAY)
    d.text((76,h-100),'steerclub.com',font=e.font(25),fill=INK)
    d.text((76,h-57),'Review draft · clinician approval required',font=e.font(18),fill=CLAY)
    d.text((w-140,h-100),number,font=e.font(25),fill=RUST)

def render_card(block,path,size,index,source,pack):
    w,h=size
    if h>1500:
        base,title,body=reel_layers(block,pack,int(index.split('/')[0])-1)
        base=Image.alpha_composite(Image.alpha_composite(base,title),body);base.convert('RGB').save(path);return
    im=Image.new('RGB',size,CREAM);d=ImageDraw.Draw(im)
    n=int(index.split('/')[0])-1 if '/' in index else 2
    total=len(pack['carousel']);role='A field note' if h==1080 else ['The question','The context','The finding','The caveat','Take it with you'][min(n,4)]
    d.text((76,48),'steer',font=e.font(48,True),fill=RUST)
    d.text((76,132),'fieldnotes / '+role.lower(),font=e.font(22),fill=CLAY)
    if h==1080:
        text(d,block['headline'],(76,215,720,250),76,True,True,RUST)
        d.rounded_rectangle((76,510,1004,830),radius=24,fill=PAPER,outline=BLUSH,width=2)
        text(d,block['body'],(115,550,840,240),39)
    elif n==0:
        text(d,block['headline'],(76,240,900,350),92,True,True,RUST)
        motif(d,650,650,300,1)
        text(d,block['body'],(76,760,560,330),40)
        d.text((76,650),'A closer look at the research',font=e.font(23),fill=CLAY)
    elif n==total-1:
        motif(d,76,240,310,2)
        text(d,block['headline'],(76,480,900,280),80,True,True,RUST)
        text(d,block['body'],(76,810,850,280),40)
    elif n%3==1:
        d.text((76,220),f'{n+1:02}',font=e.font(130,True),fill=BLUSH)
        text(d,block['headline'],(280,245,700,290),68,True,False,RUST)
        d.rounded_rectangle((76,610,1004,1090),radius=22,fill=PAPER,outline=BLUSH,width=2)
        d.text((115,650),'Read this in context',font=e.font(23),fill=CLAY)
        text(d,block['body'],(115,720,840,320),43)
    elif n%3==2:
        text(d,block['headline'],(76,240,900,330),84,True,True,RUST)
        d.line((76,660,76,1070),fill=RUST,width=7)
        text(d,block['body'],(125,700,800,360),46)
    else:
        text(d,block['headline'],(76,240,900,280),76,True,False,RUST)
        d.rounded_rectangle((76,590,1004,1090),radius=22,fill=BLUSH)
        d.text((115,630),'What this does — and does not — tell us',font=e.font(24),fill=INK)
        text(d,block['body'],(115,720,820,310),42)
    footer(d,w,h,block,pack,f'{n+1:02}' if h!=1080 else '01')
    im.save(path)

def reel_layers(block,pack,n):
    size=(1080,1920);base=Image.new('RGBA',size,CREAM);title=Image.new('RGBA',size);body=Image.new('RGBA',size)
    d=ImageDraw.Draw(base);d.text((88,150),'steer',font=e.font(52,True),fill=RUST)
    labels=['A question worth asking','Inside the research','Keep the context','A note to take with you']
    d.text((88,245),labels[min(n,3)],font=e.font(25),fill=CLAY)
    motif(d,700,1050,250,n)
    d.line((88,1650,900,1650),fill=BLUSH,width=2)
    d.text((88,1695),'steerclub.com',font=e.font(26),fill=INK)
    d.text((88,1745),'Review draft · synthetic narration',font=e.font(20),fill=CLAY)
    text(ImageDraw.Draw(title),block['headline'],(88,360,820,400),90,True,n%2==0,RUST)
    bd=ImageDraw.Draw(body);bd.rounded_rectangle((88,850,910,1200),radius=22,fill=PAPER,outline=BLUSH,width=2)
    text(bd,block['body'],(125,895,740,260),42)
    refs=[c for c in pack['claims'] if c['id'] in block['claim_ids']]
    text(bd,' · '.join(f"{c['id']} / PDF p.{c['page']}" for c in refs) or 'Editorial invitation',(88,1250,810,65),23,color=CLAY)
    return base,title,body
