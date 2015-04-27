REM RUN IT DAILY MORNING IN OFFICE
title RUN IT DAILY at office 8am
REM delay 10m for Kuaidisk sync done.
sleep 5s

REM Get QMdata.
title running GetQDAdata.py 
python GetQDAdata.py
title UpdateCSV_withQMdata.py
python ..\UpdateCSV_withQMdata.py -opath output_qda -ipath input_qda
title running GetTodaySpurtList.py 
python GetTodaySpurtList.py
title running FindSidewaysLatent.py 
python FindSidewaysLatent.py
REM beep

REM delay 10m for Kuaidisk sync done.
REM sleep 5m
cp e:/KuaiDisk/StockSmart/follows/data/*.csv ./data -n
cp e:/KuaiDisk/StockSmart/follows/hold*.csv . -f
cp e:/KuaiDisk/StockSmart/follows/watch*.csv . -f
cp e:/KuaiDisk/StockSmart/follows/watch*.csv . -f
cp e:/KuaiDisk/StockSmart/follows/catchspurt_cn.csv . -f

c:\cygwin\bin\mv save_png/* save_png_backup
c:\cygwin\bin\mkdir -p save_png/spurt
c:\cygwin\bin\mkdir -p save_png/sideway
c:\cygwin\bin\mkdir -p save_png/catchspurt
REM rm -f save_png/*
title running SaveWatchList2PNG.py 
python SaveWatchList2PNG.py
title Done
echo Done
sleep 2h
 
