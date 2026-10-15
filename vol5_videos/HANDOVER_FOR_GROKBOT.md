# Handover: build the Minerva's Ark Vol. 5 videos on the user's Mac

**Goal:** make 12 YouTube-ready chapter videos (1080p) from the user's Drive files, each ending with its song, and put them on the user's Desktop. Everything runs locally; do not upload anything anywhere.

## Where things are
- Repo: `BarneyRumble78/Mr-simpson`, branch `ccr-ceddc1af-04hh6f` (needs the user's GitHub login if private; never write tokens to files).
- Builder + instructions: `vol5_builder/` (`README.md`, `prep.py`, `build.py`, `YouTube_metadata.txt`).
- Video 1 already rendered at 720p, split in 3 parts in `vol5_videos/` (`JOIN_PARTS.md` explains joining). Videos 2-12 are not built; they come from the Mac run. A cloud render was stopped, nothing else is pending there.

## Inputs the user must have on the Mac
- Drive folder **Minerva's Ark / Vol 5 the veteran - polished ASMR**: 15 narration `.mp3` (00 opening note, 01 Proem, 02-13 chapters One-Twelve, 14 Coda), 12 Suno `*.zip` songs (each has .m4a, .jpeg cover, .txt lyrics), `P*.jpg` painted stills. Do NOT use the older folder "Vol 5 the veteran" (unpolished audio).
- Two PDFs of documentary photos: `The_Long_Return.pdf`, `Two_Worlds_One_Life.pdf` (15 pages each).
- `brew install ffmpeg poppler` (the user already started this).

## Steps
1. `git clone --branch ccr-ceddc1af-04hh6f --single-branch https://github.com/BarneyRumble78/Mr-simpson.git && cd Mr-simpson/vol5_builder`
2. `python3 prep.py --drive <Drive folder> --pdfs <folder with the PDFs>`
   Must report: 15 narration tracks, 12 songs, 35 painted stills, 30 documentary photos. If a count is off, STOP and tell the user which files are missing; do not guess or substitute.
3. Test one video: `python3 build.py all 2`. Report how long it took and check a frame from the song section (cover art bottom-left, song title readable). Compare the file length with `YouTube_metadata.txt` (video 2 should be about 14:13).
4. If good: `python3 build.py all` (resumable; re-run the same command if interrupted). Report percentage progress after each video.
   Options: `RES=720` for faster/smaller, `CRF=18` for higher quality, `SONG_DB=-3` song level vs narration.
5. Outputs are in `work/out/Minervas_Ark_Vol5_NN_<Title>.mp4`. Copy them to `~/Desktop/Minervas_Ark_Vol5/` along with `YouTube_metadata.txt`. Keep `work/` until the user has watched them.

## What the videos should look like (check against this)
- 0-7 s title card (Minerva's Ark / Vol. 5 The Veteran / Chapter name), then narration over slow Ken Burns moves on painted stills with crossfades.
- Narration is untouched (~-20 LUFS); the song follows after a short gap, about 3 dB below the narration, with the cover art + song title for 12 s over documentary photos, then a long fade-out.
- Video 1 also contains the opening note + Proem; video 12 has the Coda before its song.
- Known gaps: P04a, P06a, P10a stills do not exist, so chapters 4, 6 and 10 reuse their other stills.

## Rules
- Don't re-record, change or replace the user's audio or art. Don't make up missing files.
- Don't upload to YouTube or any host; the user will upload.
- If something fails, report the exact error and what you tried; don't claim it worked without checking the output file plays and has the right length.
- Keep status updates short, with percentages.
