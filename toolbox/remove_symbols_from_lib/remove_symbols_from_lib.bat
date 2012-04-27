rem @echo input lib file is %1.
rem @echo off
mkdir tmp
rm -rf tmp/*.*
cd tmp
zdar x ../%1
rm ..\allobjs.o
zdld -g3 --allow_overlapping_sections -r *.o -o ..\allobjs.o
cd ..
zdobjdump -h allobjs.o
zdnm allobjs.o
rm allobjs_strip.o
rm t1.o
rm t2.o
rem --redefine-sym _Mixer2CH_V2_800M=aaaaa 
zdobjcopy allobjs.o t1.o --keep-global-symbols keep_symbols.txt 
zdnm t1.o
zdobjcopy t1.o t2.o -xg 
zdnm t2.o
zdobjcopy t2.o allobjs_strip.o
rem -N _Mixer2CH_V2_800M
rem -S --keep-symbols keep_symbols.txt
zdnm allobjs_strip.o 
rm %1.new
zdar -r %1.new allobjs_strip.o
zdsize -t %1
zdsize -t %1.new
rem @echo output lib file is %1.new