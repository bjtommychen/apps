chcp 936
copy f:\KuaiDisk\StockSmart\follows\hold_*.csv . /y
REM Update All Stock Day Price Data
python GetQDAdata.py
python ..\UpdateCSV_withQMdata.py -opath output_qda -ipath input_qda
title running GetQDAdata1min.py 
python GetQDAdata1min.py
python Insertcsv2db.py
title GetStockFollows_us
.\GetStockFollows_us.py
title InsertFdata2db
python InsertFdata2db.py 
cp data/*.csv f:\KuaiDisk\StockSmart\follows\data\ -n

echo '[ China Market --- PostClose ]' > body.txt
FollowsChanges_db.py  >> body.txt
echo '' >> body.txt

echo '[ US Market --- PreOpen ]' >> body.txt
FollowsChanges_us.py  >> body.txt
echo '' >> body.txt

echo '[ HK Market --- PostClose ]' >> body.txt
FollowsChanges_hk.py  >> body.txt
echo '' >> body.txt

chcp 936
cat body.txt
cp body.txt f:\KuaiDisk\StockSmart\follows\
xq_follows_sendmail.py "ѩ���ע�������Ϻ�@xueqiu#" body.txt

REM cp watch_*.csv f:\KuaiDisk\StockSmart\follows\
pscp -batch -i myec2.ppk watch_*.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/longan 
pscp -batch -i myec2.ppk hold_*.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/longan 

call run_daily_home_8pm.bat
pscp -pw K9armed  hold_cn.csv tommy@192.168.99.9:/home/tommy/MyScripts/Longan_Foresight
echo 'wait 60s...'
sleep 60
rem pause
