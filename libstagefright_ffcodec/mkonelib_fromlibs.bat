rm -rf ./tmp 
mkdir tmp

mkdir tmp/libavformat
cd tmp/libavformat
ar x ../../../libavformat.a
cd ../..

mkdir tmp/libavcodec
cd tmp/libavcodec
ar x ../../../libavcodec.a
cd ../..

mkdir tmp/libavutil
cd tmp/libavutil
ar x ../../../libavutil.a
cd ../..

mkdir tmp/libswresample
cd tmp/libswresample
ar x ../../../libswresample.a
cd ../..

arm-linux-androideabi-ar cr libstagefright_ffmpeg.a tmp/libavformat/*.o tmp/libavcodec/*.o tmp/libavutil/*.o tmp/libswresample/*.o 



