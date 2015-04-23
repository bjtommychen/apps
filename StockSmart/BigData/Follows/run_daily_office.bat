REM RUN IT DAILY MORNING IN OFFICE
title RUN IT DAILY MORNING IN OFFICE
REM delay 10m for Kuaidisk sync done.
sleep 5s

REM Get QMdata.
python GetQDAdata.py
python ..\UpdateCSV_withQMdata.py -opath output_qda -ipath input_qda
python GetTodaySpurtList.py
python FindSidewaysLatent.py
REM beep

REM delay 10m for Kuaidisk sync done.
REM sleep 5m
cp e:/KuaiDisk/StockSmart/follows/data/*.csv ./data -n
cp e:/KuaiDisk/StockSmart/follows/hold*.csv . -f
cp e:/KuaiDisk/StockSmart/follows/watch*.csv . -f
cp e:/KuaiDisk/StockSmart/follows/watch*.csv . -f
cp e:/KuaiDisk/StockSmart/follows/catchspurt_cn.csv . -f

mv save_png/* save_png_backup
mkdir -p save_png/spurt
mkdir -p save_png/sideway
mkdir -p save_png/catchspurt
REM rm -f save_png/*
python SaveWatchList2PNG.py
echo Done
sleep 2h
 
