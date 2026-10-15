# Minerva's Ark Vol. 5 - build the 12 chapter videos on your Mac

Everything runs locally with `ffmpeg` + Python 3. Nothing is uploaded anywhere.
Each video = title card, chapter narration over slow Ken Burns moves on the painted stills,
then the chapter's Suno song at the end (cover art + title) over the documentary photos.
Video 1 also has the opening note + Proem; video 12 also has the Coda before its song.

## 1. One-time setup

    brew install ffmpeg poppler
    git clone --branch ccr-ceddc1af-04hh6f --single-branch https://github.com/BarneyRumble78/Mr-simpson.git
    cd Mr-simpson/vol5_builder

## 2. Get the source files

- Download the Drive folder **Minerva's Ark / Vol 5 the veteran - polished ASMR** (all 15 `.mp3`,
  the 12 `... - usesuno.com.zip`, the `P*.jpg` stills). Do not use the older "Vol 5 the veteran" folder.
- The two PDFs (`The_Long_Return.pdf`, `Two_Worlds_One_Life.pdf`) are already in this repo at `vol5_builder/pdfs/` - use `--pdfs ./pdfs`.

## 3. Arrange them

    python3 prep.py --drive ~/Downloads/"Vol 5 the veteran - polished ASMR" --pdfs ./pdfs

It should print: 15 narration tracks, 12 songs, 35 painted stills, 30 documentary photos.
If a count is wrong, stop and fix that before building.

## 4. Build

Try one video first (about 15-25 min on an Apple-silicon Mac at 1080p):

    python3 build.py all 2

Then everything (videos 1-12), resumable - re-run the same command if it is interrupted:

    python3 build.py all

Outputs: `work/out/Minervas_Ark_Vol5_NN_<Title>.mp4`  (1920x1080, 24 fps, H.264 + AAC).
Options (environment variables): `RES=720` for a faster/smaller test render, `CRF=18` for higher
quality, `SONG_DB=-3` for the song level relative to the narration (more negative = quieter).

## Notes
- Narration is left untouched (mastered at about -20 LUFS). Songs are brought down 3 dB.
- `YouTube_metadata.txt` in this folder has a title, description, chapter timestamps and tags for each video.
- Video 1 was already rendered at 720p and is in `../vol5_videos/` (3 parts; see `JOIN_PARTS.md`).
  Rebuild it at 1080p with `python3 build.py all 1` if you want it to match the rest.
