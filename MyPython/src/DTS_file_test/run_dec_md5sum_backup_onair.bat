@echo off
echo "======================= Test Start ====================="
echo . > run_all_log.txt
echo %* > run_all_log.txt
echo . >>run_all_log.txt
echo ================================================= >>run_all_log.txt
dir *.exe >>run_all_log.txt
echo ================================================= >>run_all_log.txt
python run_dts_test.py ConfigInfoShow >>run_all_log.txt
echo Test start: >>run_all_log.txt
date /T >>run_all_log.txt
time /T >>run_all_log.txt
echo " ----------start----------- " >>run_all_log.txt
rem goto checkmd5sum
python ..\M8\SendMailName.py "DTS FastTest start!" run_all_log.txt

rem rm -rf d:\dts_dec_bak\testing
rmdir /s /q m: 
python run_dts_test.py 

time /T >>run_all_log.txt
echo " ----------done----------- " >>run_all_log.txt

:checkmd5sum
type md5sum_log.txt | sort -k2> md5sum_sortk2.txt

echo " ---------- REPORT ----------- " >>run_all_log.txt
diff md5sum_sortk2.txt md5sum_ref_sortk2_int32.txt | grep ">" > check_md5_log.txt
type check_md5_log.txt |wc -l|xargs echo "Diff Files: " >>run_all_log.txt
type md5sum_ref_sortk2_int32.txt |wc -l|xargs echo "Total Files: " >>run_all_log.txt
echo "================ check_md5_log.txt start ==============" >> run_all_log.txt
type check_md5_log.txt >>run_all_log.txt
echo "================ check_md5_log.txt end ==============" >> run_all_log.txt

echo "Sending Mail"
gzip -c9 md5sum_log.txt >md5sum.gz
python ..\M8\SendMailName.py "DTS FastTest done!" run_all_log.txt md5sum.gz
echo "Done !" 
