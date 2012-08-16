/*******************************************************************************
*
*    Template.c    -   Template source file
*
*    Copyright (c) 2012 Tommy
*    All Rights Reserved.
*
*    Use of Tommy's code is governed by terms and conditions
*    stated in the accompanying licensing statement.
*
*    Description:
*
*    Rivision Table
* ------------------------------------------------------------------------------
*    Name            Date            Summary
* ------------------------------------------------------------------------------
*    Tommy  2/27/2012  created this file.
*
*   $Id$
*******************************************************************************/

/*********************************************************


**********************************************************/

#include "stdio.h"
#include "stdlib.h"
#include "string.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include "linux/rtc.h"
#include <sys/mman.h>

#include "JPGApi.h"

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
can't get the jpg_reserved_mem_size in bytes, maybe about 4M bytes.
#define jpg_reserved_mem_size		\
	((unsigned int)s5p_get_media_memsize_bank(S5P_MDEV_JPEG, 0))
until now, decode 1280x960 good.
but if decode 1600x1200, looks like IOCTL_JPG_DECODE done, but system crash when try to fwrite out.
*/


/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/

#define VERSION "1.00"
#define AUTHOR "TommyChen"

#define JPG_DRIVER_NAME     "/dev/s3c-jpg"
#define POST_DRIVER_NAME    "/dev/s3c-pp"

#define R_RGB565(x)     (unsigned char) (((x) >> 8) & 0xF8)
#define G_RGB565(x)     (unsigned char) (((x) >> 3) & 0xFC)
#define B_RGB565(x)     (unsigned char) ((x) << 3)

#define TRUE    1
#define FALSE   0
#define DEBUG   1
/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/


/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
int dev_fd;

FILE    *fpin, *fpout;
unsigned long    width, height, samplemode;
//char    *in_buf = NULL, *out_buf = NULL;
char    outFilename[128] ="", inFilename[128]="";
unsigned long infileSize, outfileSize, streamSize;

jpg_args *jCtx;

struct timeval start;
struct timeval stop;
unsigned int    time = 0;
/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/
static void show_banner(int argc, char **argv)
{
    printf("s3c-jpg test v %s by %s.\t", VERSION, AUTHOR);
    printf("%sbuilt on %s %s \n", " ", __DATE__, __TIME__);
}


/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/
static void initDecodeParam(void)
{
    jCtx = (jpg_args *)malloc(sizeof(jpg_args));
    memset(jCtx, 0x00, sizeof(jpg_args));

    //dec
    jCtx->dec_param = (jpg_dec_proc_param *)malloc(sizeof(jpg_dec_proc_param));
    memset(jCtx->dec_param, 0x00, sizeof(jpg_dec_proc_param));
    jCtx->dec_param->dec_type = JPG_MAIN;
    jCtx->dec_param->out_format = YCBCR_420;

    //enc
//    jCtx->enc_param = (jpg_enc_proc_param *)malloc(sizeof(jpg_enc_proc_param));
//    memset(jCtx->enc_param, 0x00, sizeof(jpg_enc_proc_param));
//    jCtx->enc_param->sample_mode = JPG_420;
//    jCtx->enc_param->enc_type = JPG_MAIN;
//    jCtx->enc_param->width = 320;
//    jCtx->enc_param->height= 240;
//    jCtx->enc_param->quality = JPG_QUALITY_LEVEL_2;
//    jCtx->enc_param->in_format = JPG_MODESEL_YCBCR;
//    jCtx->enc_param->sample_mode = JPG_422;

//    //enc thum
//    jCtx->thumb_enc_param = (jpg_enc_proc_param *)malloc(sizeof(jpg_enc_proc_param));
//    memset(jCtx->thumb_enc_param, 0x00, sizeof(jpg_enc_proc_param));
//    jCtx->thumb_enc_param->sample_mode = JPG_420;
//    jCtx->thumb_enc_param->enc_type = JPG_THUMBNAIL;
//    jCtx->thumb_enc_param->width = 320;
//    jCtx->thumb_enc_param->height= 240;
//    jCtx->thumb_enc_param->quality = JPG_QUALITY_LEVEL_2;
//    jCtx->thumb_enc_param->in_format = JPG_MODESEL_YCBCR;
//    jCtx->thumb_enc_param->sample_mode = JPG_422;

}

int main(int argc, char **argv)
{
    show_banner(argc, argv);

    strcpy(inFilename, "in.jpg");
    strcpy(outFilename, "out.yuv");

    fpin = fopen(inFilename, "rb");
    if(fpin == NULL)
    {
        printf("file open error : %s\n", inFilename);
    }

    fpout = fopen(outFilename, "wb");
    if(fpout == NULL )
    {
        printf("file open error : %s\n", outFilename);
    }


    fseek(fpin, 0, SEEK_END);
    infileSize = ftell(fpin);
    fseek(fpin, 0, SEEK_SET);
    printf("infile size %d bytes . \n", infileSize);

    //////////////////////////////////////////////////////////////
    // 1. handle Init                                           //
    //////////////////////////////////////////////////////////////

    initDecodeParam();

    dev_fd = open(JPG_DRIVER_NAME, O_RDWR);
    if(dev_fd < 0)
    {
        printf("JPEG Driver open failed\n");
        return -1;
    }
    printf("dev_fd is %d.\n", dev_fd);
    jCtx->mmapped_addr = (char *)MAP_FAILED;
    jCtx->mmapped_addr = (char *) mmap(0,
                                       JPG_TOTAL_BUF_SIZE,
                                       PROT_READ | PROT_WRITE,
                                       MAP_SHARED,
                                       dev_fd,
                                       0
                                      );
    if (jCtx->mmapped_addr == MAP_FAILED)
    {
        printf( "JPEG mmap failed\n");
        return -1;
    }

    /* prepare dec param */
    //////////////////////////////////////////////////////////////
    // 3. get Input buffer address                              //
    //////////////////////////////////////////////////////////////
    jCtx->dec_param->file_size = infileSize;
//    jCtx->dec_param->data_size = infileSize;
    jCtx->in_buf_size = infileSize;
    printf("mmapped_addr : 0x%lx\n", jCtx->mmapped_addr);
    jCtx->in_buf = (char *)ioctl(dev_fd, IOCTL_JPG_GET_STRBUF, jCtx->mmapped_addr);
    printf("in_buf : 0x%lx\n", jCtx->in_buf);

//    jCtx->out_buf = (char *)ioctl(dev_fd, IOCTL_JPG_GET_FRMBUF, jCtx->mmapped_addr);
//    printf("Decodeout_buf : 0x%x  size : %d\n", jCtx->out_buf, jCtx->dec_param->data_size);

    //enc
//    jCtx->enc_param->data_size = 320*240*2;
//    jCtx->in_buf = (char *)ioctl(dev_fd, IOCTL_JPG_GET_FRMBUF, jCtx->mmapped_addr);
//    printf("in_buf : 0x%lx\n", jCtx->in_buf);

//    jCtx->phy_in_buf = (char *)ioctl(dev_fd, IOCTL_JPG_GET_PHY_FRMBUF, jCtx->mmapped_addr);
//    printf("phy_in_buf : 0x%lx\n", jCtx->phy_in_buf);

    //////////////////////////////////////////////////////////////
    // 4. put JPEG frame to Input buffer                        //
    //////////////////////////////////////////////////////////////
    printf("read jpeg data in .");
    fread(jCtx->in_buf, 1, infileSize, fpin);
    fclose(fpin);
    printf(" done\n");


    //////////////////////////////////////////////////////////////
    // 5. Decode JPEG frame                                     //
    //////////////////////////////////////////////////////////////
    if(jCtx->dec_param->dec_type == JPG_MAIN)
    {
        ioctl(dev_fd, IOCTL_JPG_DECODE, jCtx);

        printf("dec_param->width : %d dec_param->height : %d\n", jCtx->dec_param->width, jCtx->dec_param->height);

//        printf(" enc start.\n");
//        jCtx->enc_param->enc_type = JPG_MAIN;
//        ioctl(dev_fd, IOCTL_JPG_ENCODE, jCtx);
//        printf(" enc done.\n");

    }
    else
    {
        // thumbnail decode, for the future work.
    }

    //////////////////////////////////////////////////////////////
    // 6. get Output buffer address                             //
    //////////////////////////////////////////////////////////////
    jCtx->out_buf = (char *)ioctl(dev_fd, IOCTL_JPG_GET_FRMBUF, jCtx->mmapped_addr);

    streamSize = jCtx->dec_param->data_size;
    printf("Decodeout_buf : 0x%x  size : %d\n", jCtx->out_buf, jCtx->dec_param->data_size);

    //////////////////////////////////////////////////////////////
    // 7. get decode config.                                    //
    //////////////////////////////////////////////////////////////
    width = (INT32)jCtx->dec_param->width;
    height = (INT32)jCtx->dec_param->height;
    samplemode = (INT32)jCtx->dec_param->sample_mode;

    printf("width : %d height : %d samplemode : %d\n", width, height, samplemode);

    //////////////////////////////////////////////////////////////
    // 8. wirte output file & dispaly to LCD                    //
    //////////////////////////////////////////////////////////////
    fwrite(jCtx->out_buf, 1, streamSize, fpout);
    fclose(fpout);

    //////////////////////////////////////////////////////////////
    // 9. finalize handle                                      //
    //////////////////////////////////////////////////////////////
    munmap(jCtx->mmapped_addr, JPG_TOTAL_BUF_SIZE);

    close(dev_fd);

    if(jCtx->dec_param != NULL)
        free(jCtx->dec_param);

    free(jCtx);



    printf("------------------------Decoder Test Done ---------------------\n");
    printf("Done.\n");
}



