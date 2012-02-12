echo Build
make clean -C Debug
make all -C Debug
echo Run
./Debug/ffplay_lite
echo Test
#../AudioOut/Debug/audioout -i out.pcm
#ffplay out.mp3
#../YuvShow/Debug/yuvshow -i 352x240.yuv -w 352 -h 240
