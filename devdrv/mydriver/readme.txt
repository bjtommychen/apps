// make mydriver.ko
make clean all

// install device
sudo insmod mydriver.ko
sudo lsmod
dmesg 			//dump device msg.
cat /proc/devices		//get device id.  return '250 mydriver'
rm /dev/myDriver
mknod /dev/myDriver c 250 0 		//c is char file, 0 is minor number.

// test
gcc -o test test.c
./test

