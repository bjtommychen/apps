rem @echo input lib file is %1.
rem @echo off
mkdir tmp
rm -rf tmp/*.*
cd tmp
zdar x ../%1
zdld -g3 --allow_overlapping_sections -r *.o -o ..\allobjs.o
cd ..
zdobjdump -h allobjs.o
zdnm allobjs.o
zdobjcopy allobjs.o allobjs_strip.o -S --keep-symbols keep_symbols.txt
zdnm allobjs_strip.o
rm %1.new
zdar -r %1.new allobjs_strip.o
zdsize -t %1
zdsize -t %1.new
rem @echo output lib file is %1.new