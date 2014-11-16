chcp 936
.\GetStockFollows.py 
echo '[ China Market --- PreOpen ]' > body.txt
FollowsChanges.py  >> body.txt
echo '' >> body.txt

.\GetStockFollows_us.py 
echo '[ US Market --- PostClose ]' >> body.txt
FollowsChanges_us.py  >> body.txt
echo '' >> body.txt

.\GetStockFollows_hk.py 
echo '[ HK Market --- PreOpen ]' >> body.txt
FollowsChanges_hk.py  >> body.txt
echo '' >> body.txt

chcp 936
cat body.txt
xq_follows_sendmail.py "Ñ©Çò¹Ø×¢¸ú×Ù@xueqiu#" body.txt

cp *.csv f:\KuaiDisk\StockSmart\follows\data\ -n
echo 'wait 60s...'
sleep 60
rem pause
