rm -rf d:\dts_dec_bak 
rmdir /s /q m: 
run_dts_test.py 
echo "check md5sum_log.txt for details" > body.txt
..\M8\SendMailName.py "DTS Verification Done! using Fast Test Mode." body.txt md5sum_log.txt

