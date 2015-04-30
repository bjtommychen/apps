REM goto copy_csv

chcp 936
copy f:\KuaiDisk\StockSmart\follows\hold_*.csv . /y

.\GetStockFollows.py
.\GetStockFollows_hk.py 
InsertFdata2db.py 
cp data/*.csv f:\KuaiDisk\StockSmart\follows\data\ -n

echo '[ China Market --- PreOpen ]' > body.txt
FollowsChanges.py  >> body.txt
echo '' >> body.txt

echo '[ US Market --- PostClose ]' >> body.txt
FollowsChanges_us.py  >> body.txt
echo '' >> body.txt

echo '[ HK Market --- PreOpen ]' >> body.txt
FollowsChanges_hk.py  >> body.txt
echo '' >> body.txt

:send_mail
chcp 936
cat body.txt
cp body.txt f:\KuaiDisk\StockSmart\follows\
xq_follows_sendmail.py "Ñ©Çò¹Ø×¢¸ú×ÙÔçÉÏºÃ@xueqiu#" body.txt

:copy_csv
REM cp watch_*.csv d:\workspace\apps\StockSmart\Longan\
copy watch_*.csv f:\KuaiDisk\StockSmart\follows\ /y
copy hold_*.csv f:\KuaiDisk\StockSmart\follows\ /y
copy catchspurt_cn.csv f:\KuaiDisk\StockSmart\follows\ /y
pscp -batch -i myec2.ppk hold_*.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/longan 
pscp -batch -i myec2.ppk watch_*.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/longan 
pscp -batch -i myec2.ppk *_hk.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/Longan_HK 
pscp -batch -i myec2.ppk catchspurt_cn.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/Longan_Foresight

call run_daily_home_6am.bat
pscp -batch -i myec2.ppk Sideway_cn.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/Longan_Foresight
echo 'wait 60s...'
sleep 60
rem pause
