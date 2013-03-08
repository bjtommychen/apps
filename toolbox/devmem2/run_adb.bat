@echo "--------- Run ADB Start! ------------" 
call ndk-build clean all
adb push libs\armeabi-v7a\devmem2 /data/local/tmp/ 
adb shell chmod 777 /data/local/tmp/* 
adb shell /data/local/tmp/devmem2 0x4a0022c4 
@echo "--------- Run ADB Done! ------------" 
