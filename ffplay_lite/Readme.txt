

Note:
use below to split the video/audio stream in vcd file.
ffmpeg -i /srv/stream/love_mv.mpg -vcodec copy -an -f rawvideo love_mv.mpeg1video 
ffmpeg -i /srv/stream/love_mv.mpg -acodec copy -vn love_mv.mp3




built on Feb 10 2012 14:58:09
decode mp3 to pcm successfully.  Note: mp3 must be error-free.