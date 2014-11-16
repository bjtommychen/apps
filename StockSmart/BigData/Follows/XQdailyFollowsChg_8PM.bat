chcp 936
rem .\GetStockFollows.py 
echo '[ China Market --- PostClose ]' > body.txt
FollowsChanges.py  >> body.txt
echo '' >> body.txt

.\GetStockFollows_us.py 
echo '[ US Market --- PreOpen ]' >> body.txt
FollowsChanges_us.py  >> body.txt
echo '' >> body.txt

rem .\GetStockFollows_hk.py 
echo '[ HK Market --- PostClose ]' >> body.txt
FollowsChanges_hk.py  >> body.txt
echo '' >> body.txt

chcp 936
cat body.txt
xq_follows_sendmail.py "я╘гР╧ьв╒╦ЗвымМио╨ц@xueqiu#" body.txt

cp *.csv f:\KuaiDisk\StockSmart\follows\data\ -n
echo 'wait 60s...'
sleep 60
rem pause
