make clean -C Debug
make all -C Debug
./Debug/ffplay_lite
../AudioOut/Debug/audioout -i out.pcm
ffplay out.mp3
