
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



/*
struct s3c_platform_jpeg { 
	unsigned int max_main_width;
	unsigned int max_main_height;
	unsigned int max_thumb_width;
	unsigned int max_thumb_height;
};

static struct s3c_platform_jpeg default_jpeg_data __initdata = {
	.max_main_width		= 2560,
	.max_main_height	= 1920,
	.max_thumb_width	= 0,
	.max_thumb_height	= 0,
};

void __init s3c_jpeg_set_platdata(struct s3c_platform_jpeg *pd)
{
	struct s3c_platform_jpeg *npd;

	if (!pd)
		pd = &default_jpeg_data;

	npd = kmemdup(pd, sizeof(struct s3c_platform_jpeg), GFP_KERNEL);
	if (!npd)
		printk(KERN_ERR "%s: no memory for platform data\n", __func__);
	else
		s3c_device_jpeg.dev.platform_data = npd;
}

static struct resource s3c_jpeg_resource[] = {
	[0] = {
		.start = S5PV210_PA_JPEG,
		.end   = S5PV210_PA_JPEG + S5PV210_SZ_JPEG - 1,
		.flags = IORESOURCE_MEM,
	},
	[1] = {
		.start = IRQ_JPEG,
		.end   = IRQ_JPEG,
		.flags = IORESOURCE_IRQ,
	}
};

struct platform_device s3c_device_jpeg = {
	.name             = "s3c-jpg",
	.id               = -1,
	.num_resources    = ARRAY_SIZE(s3c_jpeg_resource),
	.resource         = s3c_jpeg_resource,
};

#ifdef CONFIG_VIDEO_JPEG_V2
static struct s3c_platform_jpeg jpeg_plat __initdata = {
	.max_main_width		= 1280,
	.max_main_height	= 960,
	.max_thumb_width	= 400,
	.max_thumb_height	= 240,
};
#endif

#define  S5PV210_VIDEO_SAMSUNG_MEMSIZE_JPEG 		(4096 * SZ_1K)
	[4] = {
		.id = S5P_MDEV_JPEG,
		.name = "jpeg",
		.bank = 0,
		.memsize = S5PV210_VIDEO_SAMSUNG_MEMSIZE_JPEG,
		.paddr = 0,
	},

\\10.10.32.73\andev\cm9src\kernel\samsung\p1\arch\arm\plat-s5p\devs.c
\\10.10.32.73\andev\cm9src\kernel\samsung\p1\arch\arm\plat-s5p\include\plat\jpeg.h
\\10.10.32.73\andev\cm9src\kernel\samsung\p1\arch\arm\mach-s5pv210\mach-p1.c
\\10.10.32.73\andev\cm9src\kernel\samsung\p1\arch\arm\plat-s5p\bootmem.c

Tommy: 
looks like limit is 1280x960. and this is used in s3c_jpg_plat_init() in s3c-jpeg.c
1280x960*3 + 400*240*3 = 4Mbytes.
can't get the jpg_reserved_mem_size in bytes, maybe about 4M bytes.
#define jpg_reserved_mem_size		\
	((unsigned int)s5p_get_media_memsize_bank(S5P_MDEV_JPEG, 0))
until now, decode 1280x960 good.
but if decode 1600x1200, looks like IOCTL_JPG_DECODE done, but system crash when try to fwrite out.
*/

/* dmesg log

<6>[    2.573328] 
<6>[    2.573981] S3C JPEG Driver, (c) 2007 Samsung Electronics
<6>[    2.574187] JPEG driver for S5PV210
<4>[    2.574329] s3c_jpeg_probe called. 
<4>[    2.574431] s3c_jpg_plat_init called. 
<7>[    2.574621] s3c_jpg_plat_init: Resolution: Main (1280 x  960), Thumb ( 400 x  240)
<7>[    2.574731] s3c_jpg_plat_init: JPG Stream: Main(1228800 bytes @ 0x0), Thumb(98304 bytes @ 0x12c000)
<7>[    2.574925] s3c_jpg_plat_init: YUV frame: Main(2457600 bytes @ 0x144000), Thumb(192512 bytes @ 0x39c000)
<7>[    2.575116] s3c_jpg_plat_init: Total buffer size : 3977216 bytes
<7>[    2.575427] s3c_jpeg_probe: JPG_Init

<7>[  158.282340] s3c_jpeg_open: JPG_open 
<7>[  158.282456] s3c_jpeg_mmap: s3c_jpeg_mmap: Reserved memory (4194304), required memory (3977216)
<7>[  158.282463] mmap size (3391488). 
<7>[  158.283061] s3c_jpeg_ioctl: IOCTL_JPG_GET_STRBUF
<7>[  158.284093] s3c_jpeg_ioctl: IOCTL_JPEG_DECODE
<7>[  158.284686] decode_jpg: enter decode_jpg function
<7>[  158.284875] reset_jpg: s3c_jpeg_base f0800000
<7>[  158.292851] s3c_jpeg_irq: =====enter s3c_jpeg_irq===== 
<7>[  158.292943] s3c_jpeg_irq: int_status : 0x00000040 status : 0x00000000
<7>[  158.293108] decode_jpg: sample_mode : 2
<7>[  158.293194] decode_jpg: decode size:: width : 640 height : 480
<7>[  158.293348] get_yuv_size: get_yuv_size width(640) height(480)
<7>[  158.293464] s3c_jpeg_ioctl: IOCTL_JPG_GET_FRMBUF
<7>[  158.315505] s3c_jpeg_release: JPG_Close




*/


