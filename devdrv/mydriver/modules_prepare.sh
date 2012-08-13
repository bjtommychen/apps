pushd . 
cp /mnt/nfs/cm9src/config /mnt/nfs/cm9src/kernel/samsung/p1/.config
cd /mnt/nfs/cm9src/kernel/samsung/p1
make ARCH=arm CROSS_COMPILE=arm-linux-androideabi- modules_prepare
popd
