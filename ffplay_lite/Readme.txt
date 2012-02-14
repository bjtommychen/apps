
need use packet_queue_put.



Note:
use below to split the video/audio stream in vcd file.
ffmpeg -i /srv/stream/love_mv.mpg -vcodec copy -an -f rawvideo love_mv.mpeg1video 
ffmpeg -i /srv/stream/love_mv.mpg -acodec copy -vn love_mv.mp3


built on Feb 10 2012 14:58:09


backup log:
[mpeg @ 0x9ae54a0] max_analyze_duration 5000000 reached at 5005000
Input #0, mpeg, from '/srv/stream/love_mv.mpg':
  Duration: 00:04:36.04, start: 0.777367, bitrate: 1395 kb/s
    Stream #0:0[0x1e0]: Video: mpeg1video, yuv420p, 352x240 [SAR 200:219 DAR 880:657], 1150 kb/s, 29.97 fps, 29.97 tbr, 90k tbn, 29.97 tbc
    Stream #0:1[0x1c0]: Audio: mp2, 44100 Hz, stereo, s16, 224 kb/s
