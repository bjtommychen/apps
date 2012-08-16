/*
 * Project Name JPEG API for HW JPEG IP IN WINCE
 * Copyright  2007 Samsung Electronics Co, Ltd. All Rights Reserved. 
 *
 * This software is the confidential and proprietary information
 * of Samsung Electronics  ("Confidential Information").   
 * you shall not disclose such Confidential Information and shall use
 * it only in accordance with the terms of the license agreement
 * you entered into with Samsung Electronics 
 *
 * This file implements JPEG driver.
 *
 * @name JPEG DRIVER MODULE Module (JPGApi.h)
 * @author Jiyoung Shin (idon.shin@samsung.com)
 * @date 28-05-07
 */
#ifndef __JPG_API_H__
#define __JPG_API_H__
 
#if 0
#define MAX_JPG_WIDTH				1600
#define MAX_JPG_HEIGHT				1200
#define MAX_YUV_SIZE				(MAX_JPG_WIDTH * MAX_JPG_HEIGHT * 3)
#define	MAX_FILE_SIZE				(MAX_JPG_WIDTH * MAX_JPG_HEIGHT)
#define MAX_JPG_THUMBNAIL_WIDTH		320
#define MAX_JPG_THUMBNAIL_HEIGHT	240
#define MAX_YUV_THUMB_SIZE			(MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT * 3)
#define	MAX_FILE_THUMB_SIZE			(MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT)
#define EXIF_FILE_SIZE				28800

#define JPG_STREAM_BUF_SIZE			(MAX_JPG_WIDTH * MAX_JPG_HEIGHT)
#define JPG_STREAM_THUMB_BUF_SIZE	(MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT)
#define JPG_FRAME_BUF_SIZE			(MAX_JPG_WIDTH * MAX_JPG_HEIGHT * 3)
#define JPG_FRAME_THUMB_BUF_SIZE	(MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT * 3)

#define JPG_TOTAL_BUF_SIZE			(JPG_STREAM_BUF_SIZE + JPG_STREAM_THUMB_BUF_SIZE \
									+ JPG_FRAME_BUF_SIZE + JPG_FRAME_THUMB_BUF_SIZE)
#endif
//#define PAGE_SIZE           (4*1024)

#if 0
#define MAX_JPG_WIDTH        3072//3264
#define MAX_JPG_HEIGHT       2048//2448

#define MAX_JPG_THUMBNAIL_WIDTH	 320
#define MAX_JPG_THUMBNAIL_HEIGHT 240

#define MAX_RGB_WIDTH        800
#define MAX_RGB_HEIGHT       480
/*******************************************************************************/
// define JPG & image memory 
// memory area is 4k(PAGE_SIZE) aligned because of VirtualCopyEx()
#define JPG_STREAM_BUF_SIZE        ((MAX_JPG_WIDTH * MAX_JPG_HEIGHT )/PAGE_SIZE + 1)*PAGE_SIZE
#define JPG_STREAM_THUMB_BUF_SIZE  ((MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT )/PAGE_SIZE + 1)*PAGE_SIZE
#define JPG_FRAME_BUF_SIZE         ((MAX_JPG_WIDTH * MAX_JPG_HEIGHT * 3)/PAGE_SIZE + 1)*PAGE_SIZE
#define JPG_FRAME_THUMB_BUF_SIZE   ((MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT * 3)/PAGE_SIZE + 1)*PAGE_SIZE
#define JPG_RGB_BUF_SIZE           ((MAX_RGB_WIDTH * MAX_RGB_HEIGHT*4)/PAGE_SIZE + 1)*PAGE_SIZE

#define JPG_TOTAL_BUF_SIZE			(JPG_STREAM_BUF_SIZE + JPG_STREAM_THUMB_BUF_SIZE \
			      + JPG_FRAME_BUF_SIZE + JPG_FRAME_THUMB_BUF_SIZE + JPG_RGB_BUF_SIZE)

#endif
#if 1

#define MAX_JPG_WIDTH                   800
#define MAX_JPG_HEIGHT                  480
#define MAX_JPG_RESOLUTION              (MAX_JPG_WIDTH * MAX_JPG_HEIGHT)

#define MAX_JPG_THUMBNAIL_WIDTH         320
#define MAX_JPG_THUMBNAIL_HEIGHT        240
#define MAX_JPG_THUMBNAIL_RESOLUTION    (MAX_JPG_THUMBNAIL_WIDTH *  \
                                            MAX_JPG_THUMBNAIL_HEIGHT)

#define MAX_RGB_WIDTH                   800
#define MAX_RGB_HEIGHT                  480
#define MAX_RGB_RESOLUTION              (MAX_RGB_WIDTH * MAX_RGB_HEIGHT)

/*******************************************************************************/
/* define JPG & image memory */
/* memory area is 4k(PAGE_SIZE) aligned because of VirtualCopyEx() */
#define JPG_STREAM_BUF_SIZE     \
        (MAX_JPG_RESOLUTION / PAGE_SIZE + 1) * PAGE_SIZE
#define JPG_STREAM_THUMB_BUF_SIZE   \
        (MAX_JPG_THUMBNAIL_RESOLUTION / PAGE_SIZE + 1) * PAGE_SIZE
#define JPG_FRAME_BUF_SIZE  \
        ((MAX_JPG_RESOLUTION * 3) / PAGE_SIZE + 1) * PAGE_SIZE
#define JPG_FRAME_THUMB_BUF_SIZE    \
        ((MAX_JPG_THUMBNAIL_RESOLUTION * 3) / PAGE_SIZE + 1) * PAGE_SIZE
#define JPG_RGB_BUF_SIZE    \
        ((MAX_RGB_RESOLUTION * 4) / PAGE_SIZE + 1) * PAGE_SIZE

#define JPG_TOTAL_BUF_SIZE  (JPG_STREAM_BUF_SIZE + \
                             JPG_STREAM_THUMB_BUF_SIZE + \
                             JPG_FRAME_BUF_SIZE + \
                             JPG_FRAME_THUMB_BUF_SIZE + \
                             JPG_RGB_BUF_SIZE)

#define JPG_MAIN_START      0x00
#define JPG_THUMB_START     JPG_STREAM_BUF_SIZE
#define IMG_MAIN_START      (JPG_STREAM_BUF_SIZE + JPG_STREAM_THUMB_BUF_SIZE)
#define IMG_THUMB_START     (IMG_MAIN_START + JPG_FRAME_BUF_SIZE)
/*******************************************************************************/

#endif


typedef	unsigned char	UCHAR;
typedef unsigned long	ULONG;
typedef	unsigned int	UINT;
typedef unsigned long	DWORD;
typedef unsigned int	UINT32;
typedef int				INT32;
typedef unsigned char	UINT8;
//typedef enum {FALSE, TRUE} BOOL;

//\\10.10.32.73\andev\cm9src\device\samsung\p1-common\libs3cjpeg\JpegEncoder.h


#define JPEG_IOCTL_MAGIC                'J'
#define IOCTL_JPG_DECODE                _IO(JPEG_IOCTL_MAGIC, 1)
#define IOCTL_JPG_ENCODE                _IO(JPEG_IOCTL_MAGIC, 2)
#define IOCTL_JPG_GET_STRBUF            _IO(JPEG_IOCTL_MAGIC, 3)
#define IOCTL_JPG_GET_FRMBUF            _IO(JPEG_IOCTL_MAGIC, 4)
#define IOCTL_JPG_GET_THUMB_STRBUF      _IO(JPEG_IOCTL_MAGIC, 5)
#define IOCTL_JPG_GET_THUMB_FRMBUF      _IO(JPEG_IOCTL_MAGIC, 6)
#define IOCTL_JPG_GET_PHY_FRMBUF        _IO(JPEG_IOCTL_MAGIC, 7)
#define IOCTL_JPG_GET_PHY_THUMB_FRMBUF  _IO(JPEG_IOCTL_MAGIC, 8)

typedef enum {
    JPG_FAIL,
    JPG_SUCCESS,
    OK_HD_PARSING,
    ERR_HD_PARSING,
    OK_ENC_OR_DEC,
    ERR_ENC_OR_DEC,
    ERR_UNKNOWN
} jpg_return_status;

typedef enum {
    JPG_RGB16,
    JPG_YCBYCR,
    JPG_TYPE_UNKNOWN
} image_type_t;

typedef enum {
    JPG_444,
    JPG_422,
    JPG_420,
    JPG_400,
    RESERVED1,
    RESERVED2,
    JPG_411,
    JPG_SAMPLE_UNKNOWN
} sample_mode_t;

typedef enum {
    YCBCR_422,
    YCBCR_420,
    YCBCR_SAMPLE_UNKNOWN
} out_mode_t;

typedef enum {
    JPG_MODESEL_YCBCR = 1,
    JPG_MODESEL_RGB,
    JPG_MODESEL_UNKNOWN
} in_mode_t;

typedef enum {
    JPG_MAIN,
    JPG_THUMBNAIL
} encode_type_t;

typedef enum {
    JPG_QUALITY_LEVEL_1,        /* high */
    JPG_QUALITY_LEVEL_2,
    JPG_QUALITY_LEVEL_3,
    JPG_QUALITY_LEVEL_4         /* low */
} image_quality_type_t;

typedef struct {
    sample_mode_t   sample_mode;
    encode_type_t   dec_type;
    out_mode_t      out_format;
    uint32_t        width;
    uint32_t        height;
    uint32_t        data_size;
    uint32_t        file_size;
} jpg_dec_proc_param;

typedef struct {
    sample_mode_t       sample_mode;
    encode_type_t       enc_type;
    in_mode_t           in_format;
    image_quality_type_t quality;
    uint32_t            width;
    uint32_t            height;
    uint32_t            data_size;
    uint32_t            file_size;
    uint32_t            set_framebuf;
} jpg_enc_proc_param;

typedef struct {
    char    *in_buf;
    char    *phy_in_buf;
    int     in_buf_size;
    char    *out_buf;
    char    *phy_out_buf;
    int     out_buf_size;
    char    *in_thumb_buf;
    char    *phy_in_thumb_buf;
    int     in_thumb_buf_size;
    char    *out_thumb_buf;
    char    *phy_out_thumb_buf;
    int     out_thumb_buf_size;
    char    *mmapped_addr;
    jpg_dec_proc_param  *dec_param;
    jpg_enc_proc_param  *enc_param;
    jpg_enc_proc_param  *thumb_enc_param;
} jpg_args;


#endif

