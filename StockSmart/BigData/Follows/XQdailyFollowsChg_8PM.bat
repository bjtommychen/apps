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
xq_follows_sendmail.py "я╘гР╧ьв╒╦ЗвымМио╨ц@xueqiu#" body.txt

echo 'wait 60s...'
sleep 60
rem pause
