#!/usr/bin/env python3
"""Arrange the downloaded Drive files + the two PDFs into the layout build.py expects.

    python3 prep.py --drive ~/Downloads/"Vol 5 the veteran - polished ASMR" --pdfs ~/Downloads

--drive : folder with the 15 narration .mp3, the 12 Suno .zip song files and the P*.jpg stills
--pdfs  : folder with The_Long_Return.pdf and Two_Worlds_One_Life.pdf
Needs ffmpeg and poppler (brew install ffmpeg poppler).
"""
import argparse, glob, os, re, shutil, subprocess, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('--drive', required=True)
ap.add_argument('--pdfs', required=True)
ap.add_argument('--work', default=os.environ.get('MINERVA_WORK', './work'))
a = ap.parse_args()
W = os.path.abspath(a.work)
for d in ('audio', 'songs', 'img'):
    os.makedirs(f'{W}/{d}', exist_ok=True)

# narration: 00_Opening_note_and_title.mp3 ... 14_Coda_*.mp3 (keep names, build.py matches on the 2-digit prefix)
n = 0
for f in sorted(glob.glob(f'{a.drive}/**/*.mp3', recursive=True)):
    if re.match(r'\d\d_', os.path.basename(f)):
        shutil.copy(f, f'{W}/audio/'); n += 1
print('narration tracks:', n, '(expect 15)')

# songs: "01 The Door v2 - usesuno.com (1).zip" -> songs/s01/
n = 0
for z in sorted(glob.glob(f'{a.drive}/**/*.zip', recursive=True)):
    m = re.match(r'(\d\d) ', os.path.basename(z))
    if m:
        d = f'{W}/songs/s{m.group(1)}'
        os.makedirs(d, exist_ok=True)
        zipfile.ZipFile(z).extractall(d); n += 1
print('songs:', n, '(expect 12)')

# painted stills: "P01a-one_the-watch.jpg" -> img/P01a.jpg  ("P00-proem_living-hinge.jpg" -> P00.jpg)
n = 0
for f in sorted(glob.glob(f'{a.drive}/**/P[0-9][0-9]*.jpg', recursive=True)):
    key = os.path.basename(f).split('-')[0]
    shutil.copy(f, f'{W}/img/{key}.jpg'); n += 1
print('painted stills:', n, '(expect 35)')

# documentary photos from the PDFs (15 pages each, 1376x768): ph01..ph30, watermark corner cropped off
tmp = f'{W}/_pdfpages'
os.makedirs(tmp, exist_ok=True)
idx = 0
for key in ('Long_Return', 'Two_Worlds'):
    pdf = sorted(glob.glob(f'{a.pdfs}/*{key}*.pdf'))[0]
    pre = f'{tmp}/{key}'
    subprocess.run(['pdftoppm', '-r', '72', '-png', pdf, pre], check=True)
    for p in sorted(glob.glob(f'{pre}-*.png')):
        idx += 1
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-vf', 'crop=1316:740:0:0', '-q:v', '2',
                        f'{W}/img/ph{idx:02d}.jpg'], check=True)
shutil.rmtree(tmp)
print('documentary photos:', idx, '(expect 30)')

# dark gradient used behind the song title
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1920x1080,format=rgba',
                '-vf', "geq=r=0:g=0:b=0:a='255*0.72*pow(clip((Y/H-0.55)/0.45,0,1),2)*(3-2*clip((Y/H-0.55)/0.45,0,1))'",
                '-frames:v', '1', f'{W}/grad.png'], check=True)
print('done ->', W)
