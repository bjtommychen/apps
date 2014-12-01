chcp 936
.\GetStockFollows.py 
.\GetStockFollows_hk.py 
rem .\GetStockFollows_us.py 
cp data/*.csv f:\KuaiDisk\StockSmart\follows\data\ -n
cp watch_*.csv d:\workspace\apps\StockSmart\Longan\

echo '[ China Market --- PreOpen ]' > body.txt
FollowsChanges.py  >> body.txt
echo '' >> body.txt

echo '[ US Market --- PostClose ]' >> body.txt
FollowsChanges_us.py  >> body.txt
echo '' >> body.txt

echo '[ HK Market --- PreOpen ]' >> body.txt
FollowsChanges_hk.py  >> body.txt
echo '' >> body.txt

chcp 936
cat body.txt
cp body.txt f:\KuaiDisk\StockSmart\follows\
xq_follows_sendmail.py "Ñ©Çò¹Ø×¢¸ú×ÙÔçÉÏºÃ@xueqiu#" body.txt

echo 'wait 60s...'
sleep 60
rem pause
