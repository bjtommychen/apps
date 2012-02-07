make clean -C Debug
make all -C Debug
./Debug/yuvshow  -i 352x240.yuv -h 240 -w 352 -fmt yuv420
