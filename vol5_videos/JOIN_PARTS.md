# Joining the video parts

Videos are split into `_part1.mp4`, `_part2.mp4`, ... (each plays on its own) because GitHub caps files at 100 MB.
To make one file per video (instant, no re-encode; needs ffmpeg), run in this folder:

    for v in $(ls *_part1.mp4 | sed 's/_part1.mp4//'); do
      ls ${v}_part*.mp4 | sort -V | sed "s/^/file '/;s/$/'/" > list.txt
      ffmpeg -f concat -safe 0 -i list.txt -c copy ${v}.mp4
    done
