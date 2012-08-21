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
#include <sys/time.h>

#include "JPGApi.h"


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

#define LOOPNUM (10L)


/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/


/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
int dev_fd;

FILE    *fpin, *fpout;
unsigned long    width, height, samplemode;
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



static unsigned int measureTime_inMs(struct timeval *start, struct timeval *stop)
{
    unsigned int sec, usec, time;

    sec = stop->tv_sec - start->tv_sec;
    if(stop->tv_usec >= start->tv_usec)
    {
        usec = stop->tv_usec - start->tv_usec;
    }
    else
    {
        usec = stop->tv_usec + 1000000 - start->tv_usec;
        sec--;
    }
    time = sec*1000 + ((double)usec)/1000;
    return time;
}

static void initJpegCodecParam(void)
{
    jCtx = (jpg_args *)malloc(sizeof(jpg_args));
    memset(jCtx, 0x00, sizeof(jpg_args));

    //dec
    jCtx->dec_param = (jpg_dec_proc_param *)malloc(sizeof(jpg_dec_proc_param));
    memset(jCtx->dec_param, 0x00, sizeof(jpg_dec_proc_param));
    jCtx->dec_param->dec_type = JPG_MAIN;
    jCtx->dec_param->out_format = YCBCR_420;

    //enc
    jCtx->enc_param = (jpg_enc_proc_param *)malloc(sizeof(jpg_enc_proc_param));
    memset(jCtx->enc_param, 0x00, sizeof(jpg_enc_proc_param));
    jCtx->enc_param->sample_mode = JPG_420;
    jCtx->enc_param->enc_type = JPG_MAIN;
    jCtx->enc_param->width = 320;
    jCtx->enc_param->height= 240;
    jCtx->enc_param->quality = JPG_QUALITY_LEVEL_2;
    jCtx->enc_param->in_format = JPG_MODESEL_YCBCR;
    jCtx->enc_param->sample_mode = JPG_422;

    //enc thum
    jCtx->thumb_enc_param = (jpg_enc_proc_param *)malloc(sizeof(jpg_enc_proc_param));
    memset(jCtx->thumb_enc_param, 0x00, sizeof(jpg_enc_proc_param));
    jCtx->thumb_enc_param->sample_mode = JPG_420;
    jCtx->thumb_enc_param->enc_type = JPG_THUMBNAIL;
    jCtx->thumb_enc_param->width = 320;
    jCtx->thumb_enc_param->height= 240;
    jCtx->thumb_enc_param->quality = JPG_QUALITY_LEVEL_2;
    jCtx->thumb_enc_param->in_format = JPG_MODESEL_YCBCR;
    jCtx->thumb_enc_param->sample_mode = JPG_422;

}


/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/
int test_jpeg_decode(char *infile, char *outfile)
{
    int len;
    struct timeval start;
    struct timeval stop;
    unsigned int    time = 0;
    int loop = LOOPNUM;

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


    printf("JPEG mmap %d bytes. need < reserved memory size.\n", JPG_TOTAL_BUF_SIZE);
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
    jCtx->in_buf_size = infileSize;
    printf("mmapped_addr : 0x%lx\n", jCtx->mmapped_addr);
    jCtx->in_buf = (char *)ioctl(dev_fd, IOCTL_JPG_GET_STRBUF, jCtx->mmapped_addr);
    printf("in_buf : 0x%lx\n", jCtx->in_buf);

    //////////////////////////////////////////////////////////////
    // 4. put JPEG frame to Input buffer                        //
    //////////////////////////////////////////////////////////////
    printf("read jpeg data in ...");
    fread(jCtx->in_buf, 1, infileSize, fpin);
    fclose(fpin);
    printf(" done\n");


    //////////////////////////////////////////////////////////////
    // 5. Decode JPEG frame                                     //
    //////////////////////////////////////////////////////////////
    if(jCtx->dec_param->dec_type == JPG_MAIN)
    {

        while(loop--)
        {
            gettimeofday(&start, NULL);
            ioctl(dev_fd, IOCTL_JPG_DECODE, jCtx);
            gettimeofday(&stop, NULL);
            time += measureTime_inMs(&start, &stop);
            printf("No.%d, diff %d ms.\n", loop, measureTime_inMs(&start, &stop));
        }

        printf("Hw codec performance is %ldK pixel/second.\n", (jCtx->dec_param->width*jCtx->dec_param->height*LOOPNUM)/time);

        printf("dec_param->width : %d dec_param->height : %d\n", jCtx->dec_param->width, jCtx->dec_param->height);

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
    len = fwrite(jCtx->out_buf, 1, streamSize, fpout);
    printf("write %d bytes.\n", len);
    fclose(fpout);

    //////////////////////////////////////////////////////////////
    // 9. finalize handle                                      //
    //////////////////////////////////////////////////////////////
    munmap(jCtx->mmapped_addr, JPG_TOTAL_BUF_SIZE);

    return 0;

}


/*Tommy: this function not finished */
int test_jpeg_encode(char *infile, char *outfile)
{
    int len;
    struct timeval start;
    struct timeval stop;
    unsigned int    time = 0;
    int loop = LOOPNUM;

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


    printf("JPEG mmap %d bytes. need < reserved memory size.\n", JPG_TOTAL_BUF_SIZE);
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
    printf("mmapped_addr : 0x%lx\n", jCtx->mmapped_addr);

    //enc
    jCtx->enc_param->data_size = 320*240*2;
    jCtx->in_buf = (char *)ioctl(dev_fd, IOCTL_JPG_GET_FRMBUF, jCtx->mmapped_addr);
    printf("in_buf : 0x%lx\n", jCtx->in_buf);


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

    printf(" enc start.\n");
    jCtx->enc_param->enc_type = JPG_MAIN;
    ioctl(dev_fd, IOCTL_JPG_ENCODE, jCtx);
    printf(" enc done.\n");


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
    len = fwrite(jCtx->out_buf, 1, streamSize, fpout);
    printf("write %d bytes.\n", len);
    fclose(fpout);

    //////////////////////////////////////////////////////////////
    // 9. finalize handle                                      //
    //////////////////////////////////////////////////////////////
    munmap(jCtx->mmapped_addr, JPG_TOTAL_BUF_SIZE);

    return 0;

}


int main(int argc, char **argv)
{
    int ret;

    /***************************/
    show_banner(argc, argv);

    printf("------------------------Decoder Test Start ---------------------\n");
    /***************************/
    initJpegCodecParam();
    dev_fd = open(JPG_DRIVER_NAME, O_RDWR);
    if(dev_fd < 0)
    {
        printf("JPEG Driver open failed\n");
        return -1;
    }
    printf("%s opened, dev_fd is %d.\n", JPG_DRIVER_NAME ,dev_fd);

    /***************************/
    ret = test_jpeg_decode(0, 0);

    /***************************/
    close(dev_fd);
    if(jCtx->dec_param != NULL)
        free(jCtx->dec_param);

    free(jCtx);


    printf("------------------------Decoder Test Done ---------------------\n");
}



