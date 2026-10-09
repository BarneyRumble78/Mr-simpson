import json, subprocess, os, sys
import numpy as np
SR=44100
OUT="/home/user/Mr-simpson/audio"; os.makedirs(OUT+"/parts",exist_ok=True)
segs=json.load(open("segs.json"))

def load(p):
    raw=subprocess.run(["ffmpeg","-v","error","-i",p,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,dtype=np.float32).copy()

def trim(x,thr=0.006,pad=int(0.06*SR)):
    idx=np.where(np.abs(x)>thr)[0]
    if len(idx)==0: return x
    a=max(idx[0]-pad,0); b=min(idx[-1]+pad,len(x))
    y=x[a:b].copy(); f=int(0.012*SR)
    y[:f]*=np.linspace(0,1,f); y[-f:]*=np.linspace(1,0,f)
    return y

def silence(s): return np.zeros(int(s*SR),dtype=np.float32)

pieces=[silence(2.0)]; t=2.0
marks=[]   # (name,start)
eleven=twelve=None
prev=None
for sg in segs:
    if sg["kind"]=="heading":
        lvl=sg["level"]
        gap={2:0.5,3:3.5,4:2.8}[lvl]
        if sg["text"].startswith("Twelve"): gap=9.0
    else:
        if prev and prev["kind"]=="heading": gap=1.3
        elif sg["style"]=="close" and len(sg["text"])<60: gap=1.4   # verse lines
        else: gap=0.9
    if prev is None: gap=0
    pieces.append(silence(gap)); t+=gap
    if sg["kind"]=="heading" and sg["level"]==3:
        marks.append((sg["text"],t))
        if sg["text"].startswith("Eleven"): eleven=t
        if sg["text"].startswith("Twelve"): twelve=t
    parts=[]
    for i,f in enumerate(sg["files"]):
        if i: parts.append(silence(0.22))
        parts.append(trim(load(f)))
    a=np.concatenate(parts)
    pieces.append(a); t+=len(a)/SR
    prev=sg
pieces.append(silence(5.0))
voice=np.concatenate(pieces); T=len(voice)/SR; print("voice built",flush=True)
print("duration %.1f min"%(T/60))

# --- atmospheric bed: soft brown-noise room tone + faint airy pink, slow breathing swell.
# Built from a seamless 2-minute loop (circular filtering) and applied block by block.
rng=np.random.default_rng(7)
L=SR*120
def circ(x,fn):
    from numpy.fft import rfft,irfft,rfftfreq
    X=rfft(x); f=rfftfreq(len(x),1/SR); return irfft(X*fn(f),len(x)).astype(np.float32)
w=rng.standard_normal(L)
brown=circ(w,lambda f: 1/np.maximum(f,1.0)*(1-1/(1+(f/25)**4))/(1+(f/350)**4))   # 1/f amplitude = brown, band-limited
brown/=np.std(brown)
pink=circ(rng.standard_normal(L),lambda f: 1/np.sqrt(np.maximum(f,1.0))/(1+(f/1800)**4)*(1-1/(1+(f/60)**4)))
pink/=np.std(pink)
loop=(brown*0.85+pink*0.12).astype(np.float32); loop/=np.std(loop)
loop*=10**(-47/20)      # very low: about -47 dB rms
n=len(voice)
mix=voice
BLK=SR*60
for st in range(0,n,BLK):
    en=min(st+BLK,n); idx=np.arange(st,en)
    tt=idx/SR
    seg=loop[idx%L]
    swell=1+0.18*np.sin(2*np.pi*tt/23)+0.10*np.sin(2*np.pi*tt/9.7+1.3)
    env=np.clip(tt/6,0,1)*np.clip((T-tt)/8,0,1)
    if eleven and twelve:
        a_,b_=eleven-2.0,twelve   # silent through Part Eleven and the long silence before Twelve
        off=np.minimum(np.clip((tt-a_)/3.0,0,1),np.clip((b_-tt)/4.0,0,1))
        env=env*(1-off)
    mix[st:en]+=(seg*swell*env).astype(np.float32)
print("bed mixed",flush=True)

def write_wav(path,x):
    pcm=(np.clip(x,-1,1)*32767).astype(np.int16).tobytes()
    subprocess.run(["ffmpeg","-v","error","-y","-f","s16le","-ar",str(SR),"-ac","1","-i","-",path],input=pcm,check=True)
write_wav("mix_raw.wav",mix)
master="highpass=f=55,acompressor=threshold=-24dB:ratio=2:attack=20:release=300:makeup=2,loudnorm=I=-19:TP=-2:LRA=7"
subprocess.run(["ffmpeg","-v","error","-y","-i","mix_raw.wav","-af",master,"-ar","44100","-b:a","192k",OUT+"/Returned_full_narration.mp3"],check=True)

# per-part files, cut from the mastered file
starts=[(0,"00_Opening_note_and_title")]+[(s,"%02d_%s"%(i+1,nm)) for i,(nm,s) in enumerate(marks)]
import re
for i,(s,nm) in enumerate(starts):
    e=starts[i+1][0] if i+1<len(starts) else T
    # start earlier by the heading's gap so the part's own pause is kept at the head; trim end to before next gap
    nm=re.sub(r"[^A-Za-z0-9]+","_",nm).strip("_")[:50]
    subprocess.run(["ffmpeg","-v","error","-y","-ss","%.2f"%s,"-to","%.2f"%max(e-0.5,s+1),"-i",OUT+"/Returned_full_narration.mp3","-c:a","libmp3lame","-b:a","192k",OUT+"/parts/%s.mp3"%nm],check=True)
json.dump(dict(duration=T,marks=marks),open("marks.json","w"),indent=1)
print("done; Eleven at %.0f, Twelve at %.0f"%(eleven,twelve))
