#make mydriver.ko
make clean all

#install device
sudo rmmod mydriver
sudo insmod mydriver.ko
sudo lsmod
#dump device msg.
dmesg 			
#get device id.  return '250 mydriver'
cat /proc/devices		
rm /dev/myDriver
#c is char file, 0 is minor number.
mknod /dev/myDriver c 250 0 		

# test
gcc -o test test.c
./test

