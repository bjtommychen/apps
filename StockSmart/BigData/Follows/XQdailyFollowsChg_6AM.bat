chcp 936
.\GetStockFollows.py 
.\GetStockFollows_hk.py 
rem .\GetStockFollows_us.py 
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

cp watch_*.csv d:\workspace\apps\StockSmart\Longan\
cp watch_*.csv f:\KuaiDisk\StockSmart\follows\

chcp 936
cat body.txt
cp body.txt f:\KuaiDisk\StockSmart\follows\
xq_follows_sendmail.py "ѩ���ע�������Ϻ�@xueqiu#" body.txt

echo 'wait 60s...'
sleep 60
rem pause
