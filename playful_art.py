import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import engine as e
C='#F5EBDF';R='#C04E2A';I='#351D1D';B='#E6CBBD';P='#F8F2EB';M='#B58777'
FONT=Path('C:/Windows/Fonts')
FONTS={}
def ft(n,bold=False):
 key=(n,bold)
 if key not in FONTS:FONTS[key]=ImageFont.truetype(str(FONT/('arialbd.ttf' if bold else 'arial.ttf')),int(n)) if FONT.exists() else e.font(int(n))
 return FONTS[key]
def text(d,s,x,y,n=44,color=I,bold=False,width=950,center=False):
 start=y
 for para in s.split('\n'):
  line='';rows=[]
  for word in para.split():
   new=(line+' '+word).strip()
   if d.textlength(new,font=ft(n,bold))>width and line:rows.append(line);line=word
   else:line=new
  rows.append(line)
  for row in rows:
   xx=x+(width-d.textlength(row,font=ft(n,bold)))/2 if center else x
   d.text((xx,y),row,font=ft(n,bold),fill=color);y+=n*1.17
 return y-start

def ease(a,b,t):
 q=max(0,min(1,(t-a)/(b-a)));return q*q*(3-2*q)
def lerp(a,b,t):return a+(b-a)*t

def pill(d,s,x,y,n=25,color=I):
 w=d.textlength(s,font=ft(n,True))+36
 d.rounded_rectangle((x,y,x+w,y+n+24),radius=14,fill=color)
 d.text((x+18,y+9),s,font=ft(n,True),fill=P)

def bubble(im,s,x,y,w=370,h=160,n=42,tail='left'):
 d=ImageDraw.Draw(im)
 d.rounded_rectangle((x,y,x+w,y+h),radius=32,fill=P,outline=I,width=4)
 if tail=='left':d.polygon([(x+45,y+h-3),(x+90,y+h-3),(x+35,y+h+36)],fill=P);d.line([(x+45,y+h),(x+35,y+h+36),(x+90,y+h)],fill=I,width=4)
 else:d.polygon([(x+w-90,y+h-3),(x+w-45,y+h-3),(x+w-35,y+h+36)],fill=P)
 text(d,s,x+20,y+20,n,I,True,w-40,True)

def scale():
 im=Image.new('RGBA',(500,490));d=ImageDraw.Draw(im)
 d.ellipse((45,425,480,483),fill='#351D1D18')
 # Legs and shoes, not body measurements.
 d.line((145,378,133,440),fill=I,width=14);d.line((365,378,375,440),fill=I,width=14)
 d.rounded_rectangle((96,432,159,455),radius=10,fill=I);d.rounded_rectangle((355,432,420,455),radius=10,fill=I)
 d.rounded_rectangle((45,50,455,405),radius=65,fill=M,outline=I,width=5)
 d.rounded_rectangle((45,30,455,380),radius=65,fill=B,outline=I,width=5)
 d.rounded_rectangle((90,65,410,195),radius=25,fill=I)
 text(d,'kg.',100,78,92,P,True,300,True)
 # Proud half-lidded eyes.
 for x in [165,320]:
  d.ellipse((x-23,223,x+23,269),fill=P,outline=I,width=4)
  d.ellipse((x-6,239,x+9,255),fill=I)
  d.line((x-24,235,x+24,235),fill=I,width=5)
 d.arc((205,270,295,325),0,150,fill=I,width=5)
 d.line([(51,225),(12,200),(4,156)],fill=I,width=8)
 d.line([(450,225),(485,200),(493,157)],fill=I,width=8)
 return im
SCALE=scale()

def paper(phase=0,look=1,pose='walk'):
 im=Image.new('RGBA',(340,430));d=ImageDraw.Draw(im)
 stride=math.sin(phase)*25 if pose=='walk' else 0
 d.ellipse((55,385,310,425),fill='#351D1D16')
 d.line((115,315,100+stride,392),fill=I,width=10);d.line((235,315,250-stride,392),fill=I,width=10)
 d.rounded_rectangle((78+stride,380,125+stride,403),radius=9,fill=R)
 d.rounded_rectangle((225-stride,380,273-stride,403),radius=9,fill=R)
 d.polygon([(55,35),(245,35),(290,80),(290,325),(55,325)],fill=P,outline=I,width=4)
 d.polygon([(245,35),(245,80),(290,80)],fill=B,outline=I,width=3)
 for yy,ww in [(83,95),(101,140),(290,140)]:d.line((82,yy,82+ww,yy),fill=M,width=5)
 for xx in [125,220]:
  d.ellipse((xx-24,140,xx+24,188),fill=C,outline=I,width=4)
  d.ellipse((xx-5+look*8,151,xx+8+look*8,169),fill=I)
 d.arc((148,197,203,234),0,180,fill=I,width=5)
 if pose=='push':
  d.line([(57,230),(15,210),(3,170)],fill=I,width=8)
  d.line([(286,230),(325,208),(335,168)],fill=I,width=8)
 else:
  d.line([(55,230),(22,255),(8,237)],fill=I,width=8)
  d.line([(290,230),(319,220),(333,190)],fill=I,width=8)
 return im

def magnifier():
 im=Image.new('RGBA',(270,310));d=ImageDraw.Draw(im)
 d.line((168,190,240,278),fill=I,width=32);d.line((168,190,240,278),fill=R,width=20)
 d.ellipse((15,10,217,212),fill='#F8F2EB35',outline=I,width=13)
 d.arc((35,30,195,190),190,260,fill=P,width=10)
 return im
GLASS=magnifier()

def tray(label,band=False):
 im=Image.new('RGBA',(460,400));d=ImageDraw.Draw(im)
 d.ellipse((15,310,445,390),fill=B)
 d.ellipse((25,285,435,365),fill=P,outline=I,width=5)
 # Plain plate as editorial shorthand for the dietary intervention; no specific food prescription.
 d.ellipse((85,160,350,315),fill=C,outline=I,width=5);d.ellipse((115,180,320,290),outline=M,width=4)
 # Identical illustrated meals in both arms; food is not presented as absent.
 d.ellipse((143,198,272,272),fill=B,outline=M,width=3)
 for xx,yy in [(170,221),(211,241),(239,218),(190,253)]:d.ellipse((xx,yy,xx+5,yy+4),fill=M)
 if band:
  d.rounded_rectangle((95,55,350,165),radius=45,outline=R,width=20)
  d.line((125,75,320,145),fill=R,width=10)
 else:
  d.line((125,90,145,150),fill=I,width=7);d.line((178,80,185,145),fill=I,width=7)
 text(d,label,10,332,27,I,True,440,True)
 return im
TRAYS=[tray('Diet alone'),tray('Diet + resistance exercise',True)]

def place(im,obj,cx,cy,w,angle=0):
 obj=obj.resize((round(w),round(obj.height*w/obj.width)),Image.Resampling.LANCZOS)
 if angle:obj=obj.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 im.alpha_composite(obj,(round(cx-obj.width/2),round(cy-obj.height/2)))

def backdrop(w=1080,h=1920):
 im=Image.new('RGBA',(w,h),C);d=ImageDraw.Draw(im)
 d.ellipse((-250,h*.55,w+250,h*1.05),fill='#EFDFD0')
 d.line((0,h*.77,w,h*.77),fill=M,width=3)
 return im
# Original, bounded prop library. Labels describe objects, not scientific results.
ICONS={}
def prop(kind):
 if kind in ICONS:return ICONS[kind].copy()
 if kind=='scale':return SCALE.copy()
 if kind=='plate':
  im=Image.new('RGBA',(500,500));d=ImageDraw.Draw(im)
  d.ellipse((35,130,465,390),fill=P,outline=I,width=6);d.ellipse((75,155,425,360),outline=M,width=4)
  d.ellipse((145,200,345,320),fill=B,outline=M,width=3)
  return im
 if kind=='book':
  im=paper(0,1,'still');return im
 im=Image.new('RGBA',(500,500));d=ImageDraw.Draw(im)
 d.ellipse((70,420,440,470),fill='#351D1D16')
 if kind=='band':
  d.rounded_rectangle((65,120,435,350),radius=90,outline=R,width=35);d.line((105,155,395,320),fill=R,width=24)
 elif kind=='clock':
  d.ellipse((65,60,435,430),fill=P,outline=I,width=9)
  for n in range(12):
   a=n*math.pi/6;d.line((250+155*math.sin(a),245-155*math.cos(a),250+170*math.sin(a),245-170*math.cos(a)),fill=M,width=6)
  d.line([(250,115),(250,245),(345,295)],fill=R,width=15);d.ellipse((235,230,265,260),fill=I)
 elif kind=='heart':
  points=[]
  for n in range(121):
   t=n*math.pi/60;points.append((250+11*16*math.sin(t)**3,240-11*(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))))
  d.polygon(points,fill=R,outline=I,width=7)
 elif kind in ['leaf','water']:
  if kind=='water':d.polygon([(250,55),(105,270),(130,380),(250,425),(370,380),(395,270)],fill=B,outline=I,width=6)
  else:
   d.line([(250,420),(250,150)],fill=I,width=10)
   d.ellipse((70,130,250,285),fill=M,outline=I,width=5);d.ellipse((245,60,420,235),fill=B,outline=I,width=5)
   d.line([(120,180),(250,280),(360,130)],fill=I,width=5)
 elif kind=='chip':
  d.rounded_rectangle((100,100,400,400),radius=35,fill=B,outline=I,width=8)
  d.rounded_rectangle((155,155,345,345),radius=10,fill=P,outline=R,width=7)
  for n in [150,200,250,300,350]:
   for a,b in [((n,50),(n,100)),((n,400),(n,450)),((50,n),(100,n)),((400,n),(450,n))]:d.line((a,b),fill=I,width=9)
 elif kind=='flask':
  d.polygon([(195,60),(305,60),(305,200),(425,380),(400,430),(100,430),(75,380),(195,200)],fill=P,outline=I,width=7)
  d.polygon([(142,300),(358,300),(410,380),(390,414),(110,414),(90,380)],fill=B)
  for x,y in [(180,350),(270,390),(300,325)]:d.ellipse((x,y,x+20,y+20),fill=R)
 elif kind=='cell':
  d.ellipse((55,75,445,425),fill=B,outline=I,width=8);d.ellipse((185,180,315,310),fill=P,outline=R,width=7)
  for x,y in [(130,150),(345,200),(135,320),(330,340)]:d.rounded_rectangle((x,y,x+35,y+16),radius=8,fill=M)
 elif kind=='brain':
  for x,y in [(100,150),(155,90),(230,100),(305,120),(335,200),(290,285),(205,300),(125,250)]:d.ellipse((x-40,y-40,x+110,y+110),fill=B,outline=I,width=5)
  d.line((250,100,250,360),fill=R,width=7)
 elif kind=='network':
  pts=[(250,80),(80,220),(420,220),(150,400),(350,400)]
  for a,b in [(0,1),(0,2),(1,3),(2,4),(1,2),(3,4)]:d.line((pts[a],pts[b]),fill=M,width=6)
  for x,y in pts:d.ellipse((x-32,y-32,x+32,y+32),fill=P,outline=I,width=6)
 elif kind=='thermometer':
  d.rounded_rectangle((210,60,290,365),radius=40,fill=P,outline=I,width=7);d.ellipse((170,300,330,460),fill=B,outline=I,width=7)
  d.line((250,180,250,370),fill=R,width=22);d.ellipse((205,330,295,420),fill=R)
 elif kind=='cloud':
  for x,y,r in [(125,215,75),(210,160,100),(330,210,90)]:d.ellipse((x-r,y-r,x+r,y+r),fill=P,outline=I,width=5)
  d.rounded_rectangle((70,210,420,310),radius=35,fill=P)
  for x in [130,250,370]:d.line((x,350,x-15,410),fill=R,width=10)
 else:
  d.ellipse((65,55,435,425),fill=P,outline=I,width=7);text(d,'?',80,80,270,R,True,340,True)
 ICONS[kind]=im
 return im.copy()

def character(kind,phase=0,look=1):
 if kind=='paper':return paper(phase,look)
 if kind=='magnifier':
  im=GLASS.copy();d=ImageDraw.Draw(im)
  for x in [85,145]:d.ellipse((x,80,x+13,97),fill=I)
  d.arc((90,106,145,142),0,180,fill=I,width=4)
  return im
 if kind=='robot':
  im=Image.new('RGBA',(340,430));d=ImageDraw.Draw(im)
  for x in [100,240]:d.line((x,315,x+math.sin(phase)*12,390),fill=I,width=14)
  d.rounded_rectangle((55,95,285,335),radius=25,fill=B,outline=I,width=6)
  d.rounded_rectangle((75,130,265,240),radius=18,fill=P,outline=I,width=5)
  for x in [120,210]:d.ellipse((x-13,165,x+13,191),fill=R)
  d.line((145,212,195,212),fill=I,width=5);d.line((170,95,170,48),fill=I,width=6);d.ellipse((155,23,185,53),fill=R)
  d.line((55,245,15,205),fill=I,width=8);d.line((285,245,325,205),fill=I,width=8)
  return im
 im=prop('leaf');d=ImageDraw.Draw(im)
 for x in [295,345]:d.ellipse((x,135,x+14,153),fill=I)
 d.arc((300,165,353,200),0,180,fill=I,width=4)
 return im
