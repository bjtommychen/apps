REM RUN IT DAILY MORNING IN OFFICE
title RUN IT DAILY at Home 8pm
REM delay 10m for Kuaidisk sync done.
sleep 5s

REM Get QMdata.
title running GetQDAdata1min.py 
python GetQDAdata1min.py
REM python ..\UpdateCSV_withQMdata1min.py -opath output_qda1m -ipath input_qda1m
title running GetTodaySpurtList.py 
python GetTodaySpurtList.py
title running FindSidewaysLatent.py 
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
title running SaveWatchList2PNG.py 
python SaveWatchList2PNG.py
