"""Render a vertical motion reel with synthetic narration and timed text.
Local reels prefer FFmpeg's Flite filter; fallback silently renders text-led scenes when
narration tooling is unavailable so the app still works without crashing.
"""
import argparse, hashlib, json, os, shutil, subprocess, urllib.request, wave
from pathlib import Path
import engine as e
from PIL import Image, ImageDraw
from editorial import reel_layers, text as draw_text, INK, CREAM, RUST

def executable():
    found=os.environ.get('FFMPEG_PATH') or shutil.which('ffmpeg')
    if not found: raise ValueError('Install FFmpeg or set FFMPEG_PATH before rendering the reel.')
    return found

def command(args,cwd):
    res=subprocess.run([executable(),'-hide_banner','-loglevel','error','-y']+args,cwd=cwd,capture_output=True,text=True,timeout=240)
    if res.returncode: raise ValueError(res.stderr[-1000:])

def stamp(seconds):
    ms=round(seconds*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def silent_wav(path, seconds):
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(22050)
        frames = max(1, int(seconds * 22050))
        wav.writeframes(b'\x00' * frames * 2)

def animate_scene(block,pack,index,duration,audio,destination):
    layers=list(reel_layers(block,pack,index))
    words=(block['headline']+' '+block['body']).split()
    chunks=[' '.join(words[i:i+7]) for i in range(0,len(words),7)]
    captions=[]
    for caption in chunks:
        layer=Image.new('RGBA',(1080,1920))
        d=ImageDraw.Draw(layer);d.rounded_rectangle((88,1360,910,1575),radius=18,fill=INK)
        draw_text(d,caption,(120,1395,750,150),43,color=CREAM)
        captions.append(layer)
    args=[executable(),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','pipe:0','-i',str(audio.resolve()),'-vf','format=yuv420p','-t',str(duration),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-af','apad','-shortest',str(destination.resolve())]
    with (destination.parent/'animation-error.log').open('wb') as errors:
        process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=errors)
        try:
            for frame in range(round(duration*24)):
                t=frame/24;canvas=layers[0].copy()
                for layer,delay in [(layers[1],0),(layers[2],.6)]:
                    progress=min(1,max(0,(t-delay)/.65));moving=layer.copy()
                    moving.putalpha(moving.getchannel('A').point(lambda value:round(value*progress)))
                    canvas.alpha_composite(moving,(0,round(44*(1-progress))))
                caption=captions[min(len(captions)-1,int(t/max(duration,.1)*len(captions)))]
                canvas=Image.alpha_composite(canvas,caption)
                d=ImageDraw.Draw(canvas);d.rectangle((88,1640,88+int(812*t/duration),1644),fill=RUST)
                process.stdin.write(canvas.convert('RGB').tobytes())
            process.stdin.close()
            if process.wait(timeout=120):raise ValueError('Motion rendering failed. Check animation-error.log.')
        except Exception:
            process.kill();process.wait();raise


def render_editorial_video(run,neural=False):
    p=e.folder(run);pack=e.read(p/'pack.json');out=p/'assets';e.render(run)
    ffmpeg = executable(); status=e.provider_status(); local_voice = status.get('local_narration_available', False)
    durations=[]; subs=[];start=0
    for i,b in enumerate(pack['reel'],1):
        text=b['headline']+' '+b['body'];(out/f'voice-{i:02}.txt').write_text(text,encoding='utf-8');audio=out/f'voice-{i:02}.wav'
        if neural:
            key=os.environ.get('OPENAI_API_KEY')
            if not key: raise ValueError('OPENAI_API_KEY required for neural narration')
            payload=dict(model='gpt-4o-mini-tts',voice='coral',input=text,response_format='wav',instructions='Warm, calm educational narrator. Clear Indian English pronunciation. Do not impersonate a doctor.')
            req=urllib.request.Request('https://api.openai.com/v1/audio/speech',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=120) as r:audio.write_bytes(r.read())
        elif local_voice:
            command(['-f','lavfi','-i',f'flite=textfile=voice-{i:02}.txt:voice=slt','-ar','24000',audio.name],out)
        else:
            silent_wav(audio, max(2.0, min(8.0, 1.2 + len(text.split()) * 0.18)))
        with wave.open(str(audio)) as wav: duration=wav.getnframes()/wav.getframerate()+.5
        durations.append(duration);subs.append(f'{i}\n{stamp(start)} --> {stamp(start+duration)}\n{text}\n');start+=duration
        animate_scene(b,pack,i-1,duration,audio,out/f'scene-{i:02}.mp4')
    (out/'reel.srt').write_text('\n'.join(subs),encoding='utf-8')
    (out/'concat.txt').write_text('\n'.join(f"file 'scene-{i:02}.mp4'" for i in range(1,len(durations)+1)),encoding='utf-8')
    command(['-f','concat','-safe','0','-i','concat.txt','-i','reel.srt','-map','0:v','-map','0:a','-map','1:0','-c:v','copy','-c:a','copy','-c:s','mov_text','-movflags','+faststart','reel.mp4'],out)
    narration='OpenAI neural synthetic voice' if neural else ('Local Flite synthetic voice (not neural AI)' if local_voice else 'Silent fallback; add FFmpeg with the Flite filter for voiced narration')
    metadata=dict(visual_style='editorial-motion-v2',captions='burned-in phrase captions with approximate timing, plus scene-level SRT',duration_seconds=round(start,2),narration=narration,disclosure='Synthetic narration; not a doctor recording',copy_provenance=pack['provenance'])
    e.write(out/'video.json',metadata)
    manifest=e.read(out/'manifest.json');manifest['files'].update({name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['reel.mp4','reel.srt','video.json','caption.txt']});e.write(out/'manifest.json',manifest)
    e.log(p,'video_rendered',**metadata);return metadata
def render_video(run,neural=False):
    from playful import render_video as render_playful
    return render_playful(run,neural)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('--neural',action='store_true');a=p.parse_args();print(render_video(a.run,a.neural))
