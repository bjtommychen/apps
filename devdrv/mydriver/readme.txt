
On Linux:
easy :) just run run_linux.sh.

On Android:
1. make failed. 
Ref http://forum.xda-developers.com/archive/index.php/t-1236576.html
First we must retrieve and copy the kernel config from our device.
$ cd /path/to/android-sdk/tools
$ ./adk pull /proc/config.gz
$ gunzip ./config.gz
$ cp config /path/to/kernel/.config 
 
Next we have to prepare our kernel source for our module.
Tommy: modules_prepare !  do as user root, by 'su -' to enter.
$ cd /mnt/nfs/cm9src/kernel/samsung/p1
$ make ARCH=arm CROSS_COMPILE=arm-linux-androideabi- modules_prepare
Use modules_prepare.sh for easier.

2. insmod failed.
Ref http://blog.csdn.net/douniwan5788/article/details/7603178
Tommy: check 'dmesg' on adb, show that Unknown symbol _GLOBAL_OFFSET_TABLE_, use solution 1 OK.
solution 1:
	when make, use arm-eabi-4.4.3 of android/prebuild/toolchain, can solve this.
	When use android-toolchain of ndk will failed to insmod.
solution 2:
	add '-fno-pic' for compiler.


