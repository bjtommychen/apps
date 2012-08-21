
Test Platform
1. Samsung GalaxyTab p1000.

Build & Test
1. build with 'ndk-build clean all', got s3cjpgtest.out
2. adb push to /sdcard/work/s3cjpg/, and also copy one 'in.jpg' there.
3. adb root, then remount p1000. then su.
4. under /sdcard/work/s3cjpg, ./s3cjpgtest.out
		root@android:/sdcard/work/s3cjpg # ./s3cjpgtest.out
		s3c-jpg test v 1.00 by TommyChen.        built on Aug 21 2012 15:15:40
		infile size 1121940 bytes .
		dev_fd is 5.
		JPEG mmap 16252928 bytes. need < reserved memory size.
		mmapped_addr : 0x40075000
		in_buf : 0x40075000
		read jpeg data in . done
		No.9, diff 106 ms.
		No.8, diff 106 ms.
		No.7, diff 106 ms.
		No.6, diff 109 ms.
		No.5, diff 110 ms.
		No.4, diff 109 ms.
		No.3, diff 110 ms.
		No.2, diff 110 ms.
		No.1, diff 109 ms.
		No.0, diff 110 ms.
		Hw codec performance is 35681K pixel/second.
		dec_param->width : 2272 dec_param->height : 1704
		Decodeout_buf : 0x401b9000  size : 5834496
		width : 2272 height : 1704 samplemode : 2
		write 5834496 bytes.
		------------------------Decoder Test Done ---------------------
		Done.

Tommy Notes:
1. The original ROM can only decode jpeg upto 1280x800. because the reserved 
memory limited to 4M bytes.
2. so, I have to change S5PV210_VIDEO_SAMSUNG_MEMSIZE_JPEG from 4M bytes to 16M 
bytes in mach-p1.c
3. then use 'make out/target/product/p1/boot.img' to rebuild kernel.
4. when done, adb push to /sdcard/work/, then adb shell, su, then 'flash_image 
boot boot.img', make sure flash no error msg.
5. reboot device, let the new kernel work. 
6. now, as the reserved memory size upto 16M bytes, we can decode jpeg upto 
2272x1704 now. Test OK !



