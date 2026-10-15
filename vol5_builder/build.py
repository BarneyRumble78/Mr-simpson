#!/usr/bin/env python3
"""Minerva's Ark Vol 5 - chapter video builder (runs on a Mac or Linux with ffmpeg).

    python3 build.py all            # shots + final encode for videos 1..12
    python3 build.py all 3 4        # only videos 3 and 4
    python3 build.py shots 2        # just the camera shots for video 2
    python3 build.py finish 2       # mix + encode video 2 (needs its shots)

Environment:  MINERVA_WORK=./work (assets + output)   RES=1080|720 (default 1080)   CRF=20   SONG_DB=-3
Expects the layout made by prep.py (audio/, songs/sNN/, img/, grad.png under MINERVA_WORK).
"""
import glob, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

W = os.path.abspath(os.environ.get('MINERVA_WORK', './work'))
RES = int(os.environ.get('RES', '1080'))
OW, OH = (RES * 16) // 9, RES
SC = RES / 1080.0
CRF = os.environ.get('CRF', '20')
FPS = 24
X = 3.0            # crossfade seconds
SHOT = 48.0        # target shot length (s)
INTRO = 7.0        # narration starts after this
GAP = 4.0          # silence between narration and song
TAIL = 6.0         # after the song ends
SONG_DB = float(os.environ.get('SONG_DB', '-3'))   # songs are mastered ~5 dB hotter than narration


def find_font(*cands):
    for c in cands:
        if os.path.exists(c):
            return c
    raise SystemExit('No serif font found; edit find_font() candidates in build.py')

FONT = find_font('/System/Library/Fonts/Supplemental/Times New Roman.ttf',
                 '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
FONTI = find_font('/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf',
                  '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf',
                  '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
FONTB = find_font('/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf',
                  '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
                  '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf')

CH = {  # n: (word, title, narration track numbers, painted stills)
 1: ('One', 'The Watch', ['02'], ['P01a', 'P01b', 'P01c']),
 2: ('Two', 'The Threshold', ['03'], ['P02a', 'P02b']),
 3: ('Three', 'The One and the Many', ['04'], ['P03a', 'P03b']),
 4: ('Four', 'The Glass', ['05'], ['P04b', 'P04c']),
 5: ('Five', 'The Hour That Will Not Pass', ['06'], ['P05a', 'P05b', 'P05c']),
 6: ('Six', 'Every Perspective at Once', ['07'], ['P06b', 'P06c']),
 7: ('Seven', 'The Next One', ['08'], ['P07a', 'P07b']),
 8: ('Eight', 'The Grey', ['09'], ['P08a', 'P08b']),
 9: ('Nine', 'The Bed in the Olive Tree', ['10'], ['P09a', 'P09b', 'P09c']),
 10: ('Ten', 'The Devouring Face', ['11'], ['P10b', 'P10c', 'P10d']),
 11: ('Eleven', 'Death of the Self', ['12'], ['P11a', 'P11b', 'P11c']),
 12: ('Twelve', 'Reveille', ['13', '14'], ['P12a', 'P12b', 'P12c', 'P12d']),
}
SONGS = {1: 'The Door', 2: 'The Unmarked Line', 3: 'Gone Quiet', 4: 'Third Sheep from the Left',
         5: 'Smoke Over the Fence', 6: 'Still Awake', 7: 'One More', 8: 'Come On, Then',
         9: "It Wasn't You", 10: "Till It's Light", 11: 'Just Tonight', 12: 'Aisle Four'}

# camera moves: (z0, z1, fx0, fy0, fx1, fy1)  focus point as fraction of the frame
MOVES = [
 (1.00, 1.18, .5, .5, .5, .5),     # slow push-in
 (1.22, 1.00, .5, .5, .5, .5),     # reveal: close -> wide
 (1.14, 1.14, .0, .5, 1., .5),     # lateral glide
 (1.14, 1.14, 1., .5, .0, .5),
 (1.00, 1.45, .5, .5, .30, .36),   # push to a detail, upper left
 (1.00, 1.45, .5, .5, .70, .64),   # push to a detail, lower right
 (1.40, 1.00, .30, .62, .5, .5),   # pull out from a detail
 (1.40, 1.00, .72, .38, .5, .5),
 (1.00, 1.40, .5, .5, .66, .34),
 (1.35, 1.10, .35, .35, .6, .6),
]


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if r.returncode:
        raise RuntimeError(' '.join(cmd) + '\n' + r.stdout[-2000:])
    return r.stdout

def dur(p):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).strip())

def esc(t):
    return t.replace('\\', '\\\\').replace("'", "’").replace(':', '\\:').replace('%', '\\%')

def big(still):
    d = f'{W}/big{RES}'
    os.makedirs(d, exist_ok=True)
    out = f'{d}/{still}.jpg'
    if not os.path.exists(out):
        run(['ffmpeg', '-v', 'error', '-y', '-i', f'{W}/img/{still}.jpg', '-vf',
             f'scale={OW * 2}:{OH * 2}:flags=lanczos,unsharp=5:5:0.4', '-q:v', '2', out])
    return out

def narr_file(num):
    hits = sorted(glob.glob(f'{W}/audio/{num}_*.mp3'))
    if not hits:
        raise SystemExit(f'missing narration track {num}_*.mp3 in {W}/audio')
    return hits[0]

def plan_sections(n):
    word, title, narr, stills = CH[n]
    files = [narr_file(a) for a in narr]
    if n == 1:
        files = [narr_file('00'), narr_file('01')] + files
    song = glob.glob(f'{W}/songs/s{n:02d}/*.m4a')[0]
    cover = glob.glob(f'{W}/songs/s{n:02d}/*.jp*g')[0]
    return word, title, files, stills, song, cover

def render_shot(args):
    out, still, move, frames = args
    if os.path.exists(out):
        return
    z0, z1, fx0, fy0, fx1, fy1 = MOVES[move]
    q = f'(on/{frames - 1})'
    p = f'(0.65*{q}+0.35*{q}*{q}*(3-2*{q}))'   # gentle ease-in/out
    z = f'({z0}+({z1}-{z0})*{p})'
    fx = f'({fx0}+({fx1}-{fx0})*{p})'
    fy = f'({fy0}+({fy1}-{fy0})*{p})'
    x = f'max(0,min(iw-iw/zoom,{fx}*iw-iw/zoom/2))'
    y = f'max(0,min(ih-ih/zoom,{fy}*ih-ih/zoom/2))'
    vf = (f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={OW}x{OH}:fps={FPS},"
          f"vignette=PI/6:eval=init,format=yuv420p")
    tmp = out + '.part.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-loop', '1', '-i', big(still),
         '-frames:v', str(frames), '-vf', vf, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15',
         '-threads', '2', '-g', '48', '-an', tmp])
    os.replace(tmp, out)     # only a complete shot ever has the final name

def build(n):
    word, title, files, stills, song, cover = plan_sections(n)
    vdir = f'{W}/v{n:02d}'
    os.makedirs(vdir, exist_ok=True)
    nar = f'{vdir}/narr.flac'
    if not os.path.exists(nar):
        inp = []
        for f in files:
            inp += ['-i', f]
        fc = ''.join(f'[{i}]apad=pad_dur=2.5[a{i}];' for i in range(len(files)))
        fc += ''.join(f'[a{i}]' for i in range(len(files))) + f'concat=n={len(files)}:v=0:a=1[o]'
        run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', fc, '-map', '[o]', nar])
    piece = [dur(f) + 2.5 for f in files]
    N = sum(piece) - 2.5
    S = dur(song)
    s0 = INTRO + N + GAP
    T = s0 + S + TAIL

    secs = []   # (duration, [stills])
    if n == 1:
        proem_len = piece[0] + piece[1]
        secs.append((INTRO + proem_len, ['P00']))
        secs.append((N - proem_len + GAP, stills))
    else:
        secs.append((INTRO + N + GAP, stills))
    lo, hi = int((n - 1) * 30 / 12), int(n * 30 / 12)           # documentary photos for the song
    secs.append((S + TAIL, [f'ph{i + 1:02d}' for i in range(lo, hi)]))
    k = (T - X) / sum(d for d, _ in secs)
    shots, mv, ptr = [], 0, 0
    for d, st in secs:
        d *= k
        cnt = max(1, round(d / SHOT))
        L = d / cnt
        for i in range(cnt):
            shots.append((st[ptr % len(st)], mv % len(MOVES), L))
            ptr += 1
            mv += 3 if mv % 2 == 0 else 1
    starts, t = [], 0.0
    for _, _, L in shots:
        starts.append(t)
        t += L
    jobs = [(f'{vdir}/shot{i:02d}.mp4', still, move, round((L + X) * FPS))
            for i, (still, move, L) in enumerate(shots)]
    json.dump(dict(n=n, T=T, N=N, S=S, s0=s0, INTRO=INTRO, piece=piece, shots=len(shots)),
              open(f'{vdir}/meta.json', 'w'))
    return dict(word=word, title=title, files=files, song=song, cover=cover, nar=nar, vdir=vdir,
                shots=shots, starts=starts, jobs=jobs, T=T, N=N, S=S, s0=s0, piece=piece)

def overlays(n, P):
    word, title = P['word'], P['title']
    s0 = P['s0']
    parts = []

    def card(t0, t1, lines):
        a = (f"if(lt(t,{t0}),0,if(lt(t,{t0 + 1.2}),(t-{t0})/1.2,"
             f"if(lt(t,{t1 - 1.2}),1,if(lt(t,{t1}),({t1}-t)/1.2,0))))")
        for text, font, size, y, *xx in lines:
            size = int(size * SC)
            xe = xx[0] if xx else '(w-text_w)/2'
            parts.append(f"drawtext=fontfile={font}:text='{esc(text)}':fontsize={size}:fontcolor=0xF3E9D2:"
                         f"alpha='{a}':x={xe}:y={y}:shadowcolor=black@0.7:shadowx=2:shadowy=2")
    parts.append("drawbox=x=0:y=0:w=iw:h=ih:color=black@0.38:t=fill:enable='between(t,0,6.6)'")
    card(0.6, 6.6, [("M I N E R V A ’ S   A R K", FONT, 30, 'h*0.30'),
                    ("Vol. 5  ·  The Veteran", FONTI, 40, 'h*0.36'),
                    (f"Chapter {word}", FONTI, 52, 'h*0.50'),
                    (title, FONTB, 78, 'h*0.57')])
    if n == 12:
        coda = INTRO + P['piece'][0]
        card(coda, coda + 6, [("Coda", FONTI, 44, 'h*0.44'),
                              ("The Going Down of the Sun", FONTB, 64, 'h*0.51')])
    a0 = s0 + 1.0
    sx = str(int(440 * SC))
    card(a0, a0 + 12, [("♪  the song", FONTI, 34, 'h*0.745', sx),
                       (SONGS[n], FONTB, 66, 'h*0.80', sx)])
    return ','.join(parts)

def finish(n, P):
    vdir = P['vdir']
    out = f'{W}/out/Minervas_Ark_Vol5_{n:02d}_{P["title"].replace(" ", "_")}.mp4'
    os.makedirs(f'{W}/out', exist_ok=True)
    if os.path.exists(out):
        return out
    shots = P['shots']
    inp = []
    for i in range(len(shots)):
        inp += ['-i', f'{vdir}/shot{i:02d}.mp4']
    ia = len(shots)
    T, s0 = P['T'], P['s0']
    inp += ['-i', P['nar'], '-i', P['song']]
    for img in (P['cover'], f'{W}/grad.png'):   # looped so alpha fades have frames to act on
        inp += ['-loop', '1', '-framerate', str(FPS), '-t', f'{T:.3f}', '-i', img]
    fc, last = '', '[0:v]'
    for i in range(1, len(shots)):
        lab = f'[x{i}]'
        fc += f"{last}[{i}:v]xfade=transition=fade:duration={X}:offset={P['starts'][i]:.4f}{lab};"
        last = lab
    cov, mx, my = int(300 * SC), int(80 * SC), int(70 * SC)
    fc += (f"[{ia + 3}:v]scale={OW}:{OH},format=rgba,fade=t=in:st={s0 + 0.6}:d=1.2:alpha=1,"
           f"fade=t=out:st={s0 + 11.8}:d=1.2:alpha=1[gr];"
           f"{last}[gr]overlay=0:0:eof_action=pass[g];"
           f"[g]{overlays(n, P)}[t];"
           f"[{ia + 2}:v]scale={cov}:{cov},format=rgba,fade=t=in:st={s0 + 1}:d=1.2:alpha=1,"
           f"fade=t=out:st={s0 + 11.8}:d=1.2:alpha=1[cv];"
           f"[t][cv]overlay=x={mx}:y=H-h-{my}:eof_action=pass[tv];"
           f"[tv]fade=t=in:st=0:d=1.5,fade=t=out:st={T - 4}:d=4,format=yuv420p[v];")
    nar_ms, s_ms = int(INTRO * 1000), int(s0 * 1000)
    fc += (f"[{ia}:a]afade=t=in:st=0:d=1.5,adelay={nar_ms}|{nar_ms}[na];"
           f"[{ia + 1}:a]volume={SONG_DB}dB,afade=t=in:st=0:d=3,afade=t=out:st={P['S'] - 7}:d=7,"
           f"adelay={s_ms}|{s_ms}[sa];"
           f"[na][sa]amix=inputs=2:normalize=0:duration=longest,atrim=0:{T},alimiter=limit=0.95[a]")
    tmp = out[:-4] + '.part.mp4'
    run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', fc, '-map', '[v]', '-map', '[a]',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', CRF, '-profile:v', 'high',
         '-pix_fmt', 'yuv420p', '-r', str(FPS), '-g', '48', '-movflags', '+faststart',
         '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', f'{T:.3f}', tmp])
    os.replace(tmp, out)
    return out


if __name__ == '__main__':
    mode = sys.argv[1]
    vids = [int(a) for a in sys.argv[2:]] or list(range(1, 13))
    workers = max(2, (os.cpu_count() or 4) // 2)
    for n in vids:
        P = build(n)
        if mode in ('shots', 'all'):
            todo = [j for j in P['jobs'] if not os.path.exists(j[0])]
            print(f'video {n:02d}: {len(P["jobs"]) - len(todo)}/{len(P["jobs"])} shots already done, rendering {len(todo)}', flush=True)
            with ThreadPoolExecutor(workers) as ex:
                for i, _ in enumerate(ex.map(render_shot, todo), 1):
                    print(f'  video {n:02d} shots {len(P["jobs"]) - len(todo) + i}/{len(P["jobs"])}', flush=True)
        if mode in ('finish', 'all'):
            print(f'video {n:02d}: encoding ...', flush=True)
            print('  ->', finish(n, P), flush=True)
