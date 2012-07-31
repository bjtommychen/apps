@echo off
if {%2}=={} goto noparms

@echo on
mkdir tmp
rm -rf tmp/*.*
cd tmp
zdar x ../%1
rm -f ..\allobjs.o
zdld -g3 --allow_overlapping_sections -r *.o -o ..\allobjs.o --retain-symbols-file ../%2
cd ..
zdobjdump -h allobjs.o
zdnm allobjs.o
rm -f allobjs_strip.o t1.o t2.o %1.new
rem --redefine-sym _Mixer2CH_V2_800M=aaaaa 
zdobjcopy allobjs.o t1.o --keep-global-symbols %2
zdnm t1.o
zdobjcopy t1.o t2.o -xg 
zdnm t2.o 
rem zdnm t2.o > a.txt
rem $ awk 'BEGIN {sum=1000} $2=="t" || $2=="d"{sum+=1; v1= "zdobjcopy t.o --redefine-sym "  $3  "=localsym" sum; print v1;system(v1)}' a.txt
zdobjcopy t2.o allobjs_strip.o
rem -N _Mixer2CH_V2_800M
rem -S --keep-symbols keep_symbols.txt
zdnm allobjs_strip.o 
zdar -r %1.new allobjs_strip.o
zdsize -t %1
zdsize -t %1.new
goto end

:noparms
@echo *****************************************************
@echo *** REMOVE_SYMBOLS_FROM_LIB.BAT ------- Tommy
@echo ***     Example: thisbat libxxx.a keep_symbols.txt
@echo *****************************************************
rem @echo off
goto end

rem @echo output lib file is %1.new
:end