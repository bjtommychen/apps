export BUILD_ARCH=x86
#make mydriver.ko
make clean all
#modinfo mydriver.ko

#install device
sudo rmmod mydriver
sudo insmod mydriver.ko
sudo lsmod | grep mydriver
#dump device msg.
dmesg | tail			
#get device id.  return '250 mydriver'
cat /proc/devices  | grep mydriver		
rm /dev/myDriver
#c is char file, 0 is minor number.
mknod /dev/myDriver c 250 0 		
ls /dev/* | grep myDriver
# test
gcc -o test test.c
./test

