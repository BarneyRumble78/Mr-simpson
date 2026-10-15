# Handover: fetch the Minerva's Ark Vol. 5 videos

**Task:** download the finished videos from this GitHub repo branch to the user's Mac desktop, join the parts, and check them.

- Repo: `BarneyRumble78/Mr-simpson` (https://github.com/BarneyRumble78/Mr-simpson)
- Branch: `ccr-ceddc1af-04hh6f`
- Folder: `vol5_videos/`
- If the repo is private, the user must give you access first (they are signed in on their Mac; `gh auth login` or an existing git credential is fine). Do not ask for or store tokens in files.

## What is in the folder
12 videos, one per chapter, 1280x720, 24 fps, H.264 + AAC. Each ends with the chapter's song.
GitHub caps files at 100 MB, so each video is split into `..._part1.mp4`, `..._part2.mp4`, ...
(each part plays on its own). Videos are pushed one at a time as they finish rendering, so
some may not be there yet; check the folder listing and the last commit message before you start.

| # | Name stem | Contents |
|---|-----------|----------|
| 01 | `Minervas_Ark_Vol5_01_The_Watch` | Opening note, Proem, Ch. One, song "The Door" |
| 02 | `Minervas_Ark_Vol5_02_The_Threshold` | Ch. Two, song "The Unmarked Line" |
| 03 | `Minervas_Ark_Vol5_03_The_One_and_the_Many` | Ch. Three, song "Gone Quiet" |
| 04 | `Minervas_Ark_Vol5_04_The_Glass` | Ch. Four, song "Third Sheep from the Left" |
| 05 | `Minervas_Ark_Vol5_05_The_Hour_That_Will_Not_Pass` | Ch. Five, song "Smoke Over the Fence" |
| 06 | `Minervas_Ark_Vol5_06_Every_Perspective_at_Once` | Ch. Six, song "Still Awake" |
| 07 | `Minervas_Ark_Vol5_07_The_Next_One` | Ch. Seven, song "One More" |
| 08 | `Minervas_Ark_Vol5_08_The_Grey` | Ch. Eight, song "Come On, Then" |
| 09 | `Minervas_Ark_Vol5_09_The_Bed_in_the_Olive_Tree` | Ch. Nine, song "It Wasn't You" |
| 10 | `Minervas_Ark_Vol5_10_The_Devouring_Face` | Ch. Ten, song "Till It's Light" |
| 11 | `Minervas_Ark_Vol5_11_Death_of_the_Self` | Ch. Eleven, song "Just Tonight" |
| 12 | `Minervas_Ark_Vol5_12_Reveille` | Ch. Twelve, Coda, song "Aisle Four" |

Also in the folder (once the run finishes): `YouTube_metadata.txt` (titles, descriptions, chapter
timestamps, tags) and `NN_*.jpg` thumbnails (1280x720).

## Steps
1. Get the files (needs `git` and `ffmpeg`; `brew install ffmpeg` if missing):

       cd ~/Desktop
       git clone --branch ccr-ceddc1af-04hh6f --single-branch --depth 1 https://github.com/BarneyRumble78/Mr-simpson.git minerva_tmp
       cd minerva_tmp/vol5_videos && ls -la

2. Join the parts into one file per video (instant, no re-encode):

       for v in $(ls *_part1.mp4 | sed 's/_part1.mp4//'); do
         ls ${v}_part*.mp4 | sort -V | sed "s/^/file '/;s/\$/'/" > list.txt
         ffmpeg -f concat -safe 0 -i list.txt -c copy ${v}.mp4
       done
       rm -f list.txt

3. Move the joined videos, thumbnails and `YouTube_metadata.txt` to `~/Desktop/Minervas_Ark_Vol5/`.
   Do not delete the `_partN` files until the checks below pass.

4. Check each joined video:
   - `ffprobe -v error -show_entries format=duration -of csv=p=0 FILE.mp4` should match the length in `YouTube_metadata.txt` (within 1 s).
   - It opens and plays through the part joins with no jump or audio gap.
   - If a video is missing parts, report which ones. Do not fabricate or re-render anything.

## Notes
- These are the user's own unreleased recordings: keep them local, do not upload anywhere other than the user's own YouTube channel when they ask you to.
- To re-pull later videos: `git pull` inside the cloned folder, then repeat step 2.
- The videos were rendered at 720p at the user's request (lower quality, to get them out sooner).
