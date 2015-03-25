python GetQDAdata.py
python ..\UpdateCSV_withQMdata.py -opath output_qda -ipath input_qda
cp e:/KuaiDisk/StockSmart/follows/data/*.csv ./data -n
beep
sleep 10m

rm -f save_png/*
python SaveWatchList2PNG.py
pause
