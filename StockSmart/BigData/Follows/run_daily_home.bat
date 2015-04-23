REM RUN IT DAILY MORNING IN OFFICE
title RUN IT DAILY at Home
REM delay 10m for Kuaidisk sync done.
sleep 5s

REM Get QMdata.
python GetQDAdata.py
python ..\UpdateCSV_withQMdata.py -opath output_qda -ipath input_qda
python GetQDAdata1min.py
REM python ..\UpdateCSV_withQMdata1min.py -opath output_qda1m -ipath input_qda1m
python GetTodaySpurtList.py
python FindSidewaysLatent.py
REM beep

REM delay 10m for Kuaidisk sync done.
REM sleep 5m
REM cp f:/KuaiDisk/StockSmart/follows/data/*.csv ./data -n
cp f:/KuaiDisk/StockSmart/follows/hold*.csv . -f
REM cp f:/KuaiDisk/StockSmart/follows/watch*.csv . -f

mv save_png/* save_png_backup
mkdir -p save_png/spurt
mkdir -p save_png/sideway
mkdir -p save_png/catchspurt
REM rm -f save_png/*
python SaveWatchList2PNG.py
REM pause
