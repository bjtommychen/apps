make clean -C Debug
make all -C Debug
./Debug/audioout  -i /srv/stream/hero.wav -srate 44100 -ch 2
