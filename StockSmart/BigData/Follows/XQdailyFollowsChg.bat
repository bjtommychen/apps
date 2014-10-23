.\GetStockFollows.py 
echo '[ China Market ]' > body.txt
FollowsChanges.py  >> body.txt
echo '' >> body.txt

.\GetStockFollows_us.py 
echo '[ US Market ]' >> body.txt
FollowsChanges_us.py  >> body.txt
echo '' >> body.txt

.\GetStockFollows_hk.py 
echo '[ HK Market ]' >> body.txt
FollowsChanges_hk.py  >> body.txt
echo '' >> body.txt

cat body.txt
xq_follows_sendmail.py "Ñ©Çò¹Ø×¢¸ú×Ù@xueqiu#" body.txt

cp *.csv f:\KuaiDisk\StockSmart\follows\ -n
echo 'wait 60s...'
sleep 60
rem pause
