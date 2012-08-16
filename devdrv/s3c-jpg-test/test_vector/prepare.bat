adb root
adb shell . ./sdcard/work/remp1.txt
adb shell mount -o remount,rw -t vfat /dev/block//vold/179:1 /sdcard
