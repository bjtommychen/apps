copy \\tu\home_tommy\git\apps\ffplay_android\tool\*.sh *.bat /Y
copy \\tu\home_tommy\git\apps\ffplay_android\test\example\ffplay_android.out .
adb push ffplay_android.out /sdcard/work/ffplay/
adb shell <script
#adb pull /sdcard/work/ffplay/352x240.yuv
