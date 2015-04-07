
REM Get QMdata.
python GetQDAdata.py
python ..\UpdateCSV_withQMdata.py -opath output_qda -ipath input_qda
beep

REM delay 10m for Kuaidisk sync done.
REM sleep 5m
cp e:/KuaiDisk/StockSmart/follows/data/*.csv ./data -n
cp e:/KuaiDisk/StockSmart/follows/hold*.csv . -f
cp e:/KuaiDisk/StockSmart/follows/watch*.csv . -f
rm -f save_png/*
python SaveWatchList2PNG.py
pause
