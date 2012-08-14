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


#define IOCTL_JPG_DECODE                0x00000002
#define IOCTL_JPG_ENCODE                0x00000003
#define IOCTL_JPG_GET_STRBUF            0x00000004
#define IOCTL_JPG_GET_FRMBUF            0x00000005
#define IOCTL_JPG_GET_THUMB_STRBUF      0x0000000A
#define IOCTL_JPG_GET_THUMB_FRMBUF      0x0000000B
#define IOCTL_JPG_GET_PHY_FRMBUF        0x0000000C
#define IOCTL_JPG_GET_PHY_THUMB_FRMBUF  0x0000000D


#define R_RGB565(x)     (unsigned char) (((x) >> 8) & 0xF8)
#define G_RGB565(x)     (unsigned char) (((x) >> 3) & 0xFC)
#define B_RGB565(x)     (unsigned char) ((x) << 3)

#define TRUE    1
#define FALSE   0
#define DEBUG   1
/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/
typedef enum tagENCDEC_TYPE_T
{
    JPG_MAIN,
    JPG_THUMBNAIL
} ENCDEC_TYPE_T;

typedef struct tagJPG_DEC_PROC_PARAM
{
    SAMPLE_MODE_T   sampleMode;
    ENCDEC_TYPE_T   decType;
    UINT32  width;
    UINT32  height;
    UINT32  dataSize;
    UINT32  fileSize;
} JPG_DEC_PROC_PARAM;

typedef struct tagJPG_ENC_PROC_PARAM
{
    SAMPLE_MODE_T   sampleMode;
    ENCDEC_TYPE_T   encType;
    IMAGE_QUALITY_TYPE_T quality;
    UINT32  width;
    UINT32  height;
    UINT32  dataSize;
    UINT32  fileSize;
} JPG_ENC_PROC_PARAM;

typedef struct tagJPG_CTX
{
    UINT    debugPrint;
    char    *InBuf;
    char    *OutBuf;
    char    *InThumbBuf;
    char    *OutThumbBuf;
    char    *mappedAddr;
    UINT8   thumbnailFlag;
    JPG_DEC_PROC_PARAM  *decParam;
    JPG_ENC_PROC_PARAM  *encParam;
    JPG_ENC_PROC_PARAM  *thumbEncParam;
    ExifFileInfo *ExifInfo;
} JPG_CTX;

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
int dev_fd;

FILE    *fpin, *fpout;
unsigned long    width, height, samplemode;
char    *InBuf = NULL, *OutBuf = NULL;
char    outFilename[128], inFilename[128];
unsigned long infileSize, outfileSize, streamSize;

JPG_CTX *jCtx;

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
    jCtx = (JPG_CTX *)malloc(sizeof(JPG_CTX));
    memset(jCtx, 0x00, sizeof(JPG_CTX));

    jCtx->decParam = (JPG_DEC_PROC_PARAM *)malloc(sizeof(JPG_DEC_PROC_PARAM));
    memset(jCtx->decParam, 0x00, sizeof(JPG_DEC_PROC_PARAM));

    jCtx->debugPrint = TRUE;
    jCtx->decParam->decType = JPG_MAIN;
}

int main(int argc, char **argv)
{
    show_banner(argc, argv);

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
    strcpy(inFilename, "in.jpg");
    strcpy(outFilename, "out.yuv");

    fseek(fpin, 0, SEEK_END);
    infileSize = ftell(fpin);
    fseek(fpin, 0, SEEK_SET);
    printf(" infile size %d bytes . \n", infileSize);
    
    //////////////////////////////////////////////////////////////
    // 1. handle Init                                           //
    //////////////////////////////////////////////////////////////
    initDecodeParam();
    dev_fd = open(JPG_DRIVER_NAME, O_RDWR|O_NDELAY);
    if(dev_fd < 0)
    {
        printf("JPEG Driver open failed\n");
        return -1;
    }
    jCtx->mappedAddr = (char *) mmap(0,
                                     JPG_TOTAL_BUF_SIZE,
                                     PROT_READ | PROT_WRITE,
                                     MAP_SHARED,
                                     dev_fd,
                                     0
                                    );
    if (jCtx->mappedAddr == NULL)
    {
        printf( "JPEG mmap failed\n");
        return -1;
    }

    /* prepare dec param */
    //////////////////////////////////////////////////////////////
    // 3. get Input buffer address                              //
    //////////////////////////////////////////////////////////////
    jCtx->decParam->fileSize = infileSize;
    jCtx->InBuf = InBuf=(char *)ioctl(dev_fd, IOCTL_JPG_GET_STRBUF, jCtx->mappedAddr);
    printf("inBuf : 0x%x\n", InBuf);


    //////////////////////////////////////////////////////////////
    // 4. put JPEG frame to Input buffer                        //
    //////////////////////////////////////////////////////////////
    fread(InBuf, 1, infileSize, fpin);
    fclose(fpin);


    //////////////////////////////////////////////////////////////
    // 5. Decode JPEG frame                                     //
    //////////////////////////////////////////////////////////////
    if(jCtx->decParam->decType == JPG_MAIN)
    {
        ioctl(dev_fd, IOCTL_JPG_DECODE, jCtx->decParam);

        printf("decParam->width : %d decParam->height : %d\n", jCtx->decParam->width, jCtx->decParam->height);
        printf("streamSize : %d\n", jCtx->decParam->dataSize);
    }
    else
    {
        // thumbnail decode, for the future work.
    }

    //////////////////////////////////////////////////////////////
    // 6. get Output buffer address                             //
    //////////////////////////////////////////////////////////////
    jCtx->OutBuf = (char *)ioctl(dev_fd, IOCTL_JPG_GET_FRMBUF, jCtx->mappedAddr);

    printf("DecodeOutBuf : 0x%x  size : %d\n", jCtx->OutBuf, jCtx->decParam->dataSize);
    streamSize = jCtx->decParam->dataSize;

    printf("OutBuf : 0x%x streamsize : %d\n", OutBuf, streamSize);

    //////////////////////////////////////////////////////////////
    // 7. get decode config.                                    //
    //////////////////////////////////////////////////////////////
    width = (INT32)jCtx->decParam->width;
    height = (INT32)jCtx->decParam->height;
    samplemode = (INT32)jCtx->decParam->sampleMode;

    printf("width : %d height : %d samplemode : %d\n", width, height, samplemode);

    //////////////////////////////////////////////////////////////
    // 8. wirte output file & dispaly to LCD                    //
    //////////////////////////////////////////////////////////////
    fwrite(OutBuf, 1, streamSize, fpout);
    fclose(fpout);

    //////////////////////////////////////////////////////////////
    // 9. finalize handle                                      //
    //////////////////////////////////////////////////////////////
    munmap(jCtx->mappedAddr, JPG_TOTAL_BUF_SIZE);

    close(dev_fd);

    if(jCtx->decParam != NULL)
        free(jCtx->decParam);

    free(jCtx);



    printf("------------------------Decoder Test Done ---------------------\n");
    printf("Done.\n");
}



