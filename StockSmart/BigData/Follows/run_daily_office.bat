REM RUN IT DAILY MORNING IN OFFICE
title RUN IT DAILY at office 8am
REM delay 10m for Kuaidisk sync done.
sleep 5s

REM Get QMdata and Update CSV.
title running GetQDAdata.py 
python GetQDAdata.py
title UpdateCSV_withQMdata.py
python ..\UpdateCSV_withQMdata.py -opath output_qda -ipath input_qda
REM Get QMdata1min.
title running GetQDAdata1min.py 
python GetQDAdata1min.py
REM Update to db
title Insertcsv2db
python Insertcsv2db.py
REM Get list
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

c:\cygwin\bin\cp -rf save_png/* save_png_backup
c:\cygwin\bin\rm -rf save_png
c:\cygwin\bin\mkdir -p save_png/spurt
c:\cygwin\bin\mkdir -p save_png/sideway
c:\cygwin\bin\mkdir -p save_png/catchspurt
REM Save to PNG
title running SaveWatchList2PNG.py 
python SaveWatchList2PNG.py
title Done
echo Done
sleep 2h
 
