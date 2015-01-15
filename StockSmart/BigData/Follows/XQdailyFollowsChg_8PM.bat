chcp 936
rem .\GetStockFollows.py 
.\GetStockFollows_us.py 
rem .\GetStockFollows_hk.py 
cp data/*.csv f:\KuaiDisk\StockSmart\follows\data\ -n

echo '[ China Market --- PostClose ]' > body.txt
FollowsChanges.py  >> body.txt
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
xq_follows_sendmail.py "Ñ©Çò¹Ø×¢¸ú×ÙÍíÉÏºÃ@xueqiu#" body.txt

cp watch_*.csv d:\workspace\apps\StockSmart\Longan\
cp watch_*.csv f:\KuaiDisk\StockSmart\follows\
pscp -batch -i myec2.ppk watch_*.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/longan 
pscp -batch -i myec2.ppk hold_*.csv ubuntu@bjtommychen.oicp.net:/home/ubuntu/script/longan 

echo 'wait 60s...'
sleep 60
rem pause
