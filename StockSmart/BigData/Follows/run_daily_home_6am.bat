REM RUN IT DAILY MORNING IN OFFICE
title RUN IT DAILY at Home
REM delay 10m for Kuaidisk sync done.
sleep 5s

REM Get QMdata.
python InsertFdata2db.py 
python GetTodaySpurtList.py
python FindSidewaysLatent_db.py
REM beep

REM delay 10m for Kuaidisk sync done.
REM sleep 5m
cp f:/KuaiDisk/StockSmart/follows/hold*.csv . -f

d:\cygwin\bin\cp -rf save_png/* save_png_backup
d:\cygwin\bin\rm -rf save_png
d:\cygwin\bin\mkdir -p save_png/spurt
d:\cygwin\bin\mkdir -p save_png/sideway
d:\cygwin\bin\mkdir -p save_png/catchspurt
REM rm -f save_png/*
python SaveWatchList2PNG.py
d:\cygwin\bin\rm -rf f:\KuaiDisk\StockSmart\follows\save_png\
d:\cygwin\bin\mkdir -p f:\KuaiDisk\StockSmart\follows\save_png\
d:\cygwin\bin\cp -rf save_png/* f:\KuaiDisk\StockSmart\follows\save_png\
REM pause
sleep 10s