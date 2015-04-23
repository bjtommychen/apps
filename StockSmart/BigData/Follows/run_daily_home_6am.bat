REM RUN IT DAILY MORNING IN OFFICE
title RUN IT DAILY at Home
REM delay 10m for Kuaidisk sync done.
sleep 5s

REM Get QMdata.
REM python GetTodaySpurtList.py
python FindSidewaysLatent.py
REM beep

REM delay 10m for Kuaidisk sync done.
REM sleep 5m
cp f:/KuaiDisk/StockSmart/follows/hold*.csv . -f

mv save_png/* save_png_backup
d:\cygwin\bin\mkdir -p save_png/spurt
d:\cygwin\bin\mkdir -p save_png/sideway
d:\cygwin\bin\mkdir -p save_png/catchspurt
REM rm -f save_png/*
python SaveWatchList2PNG.py
REM pause
