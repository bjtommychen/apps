.\GetStockFollows.py 
FollowsChanges.py  > body.txt

.\GetStockFollows_us.py 
FollowsChanges_us.py  >> body.txt

.\GetStockFollows_hk.py 
FollowsChanges_hk.py  >> body.txt

cat body.txt
xq_follows_sendmail.py "ѩ���ע����@xueqiu#" body.txt

cp *.csv f:\KuaiDisk\StockSmart\follows\ -n
pause
