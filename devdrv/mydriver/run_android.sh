#all MUST be done under root@tu.
#/path/to/kernel/ is /mnt/nfs/cm9src/kernel/samsung/p1
#get .config first.
#


#make mydriver.ko
export BUILD_ARCH=arm
make clean all
modinfo mydriver.ko
arm-linux-androideabi-gcc --sysroot /srv/android-ndk/platforms/android-14/arch-arm/ -o test.out test.c

#Under ADB shell as root.
#install device
# sudo rmmod mydriver
# sudo insmod mydriver.ko
# sudo lsmod | grep mydriver
#dump device msg.
# dmesg | tail			
#get device id.  return '249 mydriver'
# cat /proc/devices  | grep mydriver		
# rm /dev/myDriver
#c is char file, 0 is minor number.
# mknod /dev/myDriver c 249 0 		
# ls /dev/* | grep myDriver
# ./test.out

