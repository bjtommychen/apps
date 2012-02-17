echo Build
make clean -C Debug
make all -C Debug
echo Run
./Debug/ffplay_lite 
echo Test

#showmount -e 10.10.32.179
#sudo mount 10.10.32.179:/home/cncn1/nfs/stream /mnt/nfs
#sudo umount /mnt/nfs
#for i in `ls/mnt/nfs/avi/*.avi`;do ./Debug/ffplay_lite "$i"; done;
for i in /mnt/nfs/avi/*.avi;do ./Debug/ffplay_lite "$i"; done;

