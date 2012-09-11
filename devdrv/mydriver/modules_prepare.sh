pushd . 
cp /mnt/nfs/bejquad4/andev/cm9src/config /mnt/nfs/bejquad4/andev/cm9src/kernel/samsung/p1/.config
cd /mnt/nfs/bejquad4/andev/cm9src/kernel/samsung/p1
make ARCH=arm CROSS_COMPILE=arm-linux-androideabi- modules_prepare
popd
