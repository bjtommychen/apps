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
 

//#define MAX_JPG_WIDTH				1600
//#define MAX_JPG_HEIGHT				1200
//#define MAX_YUV_SIZE				(MAX_JPG_WIDTH * MAX_JPG_HEIGHT * 3)
//#define	MAX_FILE_SIZE				(MAX_JPG_WIDTH * MAX_JPG_HEIGHT)
//#define MAX_JPG_THUMBNAIL_WIDTH		320
//#define MAX_JPG_THUMBNAIL_HEIGHT	240
//#define MAX_YUV_THUMB_SIZE			(MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT * 3)
//#define	MAX_FILE_THUMB_SIZE			(MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT)
//#define EXIF_FILE_SIZE				28800

//#define JPG_STREAM_BUF_SIZE			(MAX_JPG_WIDTH * MAX_JPG_HEIGHT)
//#define JPG_STREAM_THUMB_BUF_SIZE	(MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT)
//#define JPG_FRAME_BUF_SIZE			(MAX_JPG_WIDTH * MAX_JPG_HEIGHT * 3)
//#define JPG_FRAME_THUMB_BUF_SIZE	(MAX_JPG_THUMBNAIL_WIDTH * MAX_JPG_THUMBNAIL_HEIGHT * 3)

//#define JPG_TOTAL_BUF_SIZE			(JPG_STREAM_BUF_SIZE + JPG_STREAM_THUMB_BUF_SIZE \
//									+ JPG_FRAME_BUF_SIZE + JPG_FRAME_THUMB_BUF_SIZE)

//#define PAGE_SIZE           (4*1024)

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

typedef	unsigned char	UCHAR;
typedef unsigned long	ULONG;
typedef	unsigned int	UINT;
typedef unsigned long	DWORD;
typedef unsigned int	UINT32;
typedef int				INT32;
typedef unsigned char	UINT8;
//typedef enum {FALSE, TRUE} BOOL;

//\\10.10.32.73\andev\cm9src\device\samsung\p1-common\libs3cjpeg\JpegEncoder.h


typedef enum {
    JPEG_SET_ENCODE_WIDTH,
    JPEG_SET_ENCODE_HEIGHT,
    JPEG_SET_ENCODE_QUALITY,
    JPEG_SET_ENCODE_IN_FORMAT,
    JPEG_SET_SAMPING_MODE,
    JPEG_SET_THUMBNAIL_WIDTH,
    JPEG_SET_THUMBNAIL_HEIGHT
} jpeg_conf;

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

#if 0
typedef enum tagSAMPLE_MODE_T{
	JPG_444,
	JPG_422,
	JPG_420, 
	JPG_411,
	JPG_400,
	JPG_SAMPLE_UNKNOWN
}SAMPLE_MODE_T;

typedef enum tagIMAGE_QUALITY_TYPE_T{
	JPG_QUALITY_LEVEL_1 = 0, /*high quality*/
	JPG_QUALITY_LEVEL_2,
	JPG_QUALITY_LEVEL_3,
	JPG_QUALITY_LEVEL_4     /*low quality*/
}IMAGE_QUALITY_TYPE_T;

typedef enum tagJPEGConf{
	JPEG_GET_DECODE_WIDTH,
	JPEG_GET_DECODE_HEIGHT,
	JPEG_GET_SAMPING_MODE,
	JPEG_SET_ENCODE_WIDTH,
	JPEG_SET_ENCODE_HEIGHT,
	JPEG_SET_ENCODE_QUALITY,
	JPEG_SET_ENCODE_THUMBNAIL,
	JPEG_SET_SAMPING_MODE,
	JPEG_SET_THUMBNAIL_WIDTH,
	JPEG_SET_THUMBNAIL_HEIGHT
}JPEGConf;

typedef enum tagJPEG_ERRORTYPE{
	JPEG_FAIL,
	JPEG_OK,
	JPEG_ENCODE_FAIL,
	JPEG_ENCODE_OK,
	JPEG_DECODE_FAIL,
	JPEG_DECODE_OK,
	JPEG_HEADER_PARSE_FAIL,
	JPEG_HEADER_PARSE_OK,
	JPEG_UNKNOWN_ERROR
}JPEG_ERRORTYPE;

typedef enum tagJPEG_SCALER{
	JPEG_USE_HW_SCALER=1,
	JPEG_USE_SW_SCALER=2
}JPEG_SCALER;

typedef struct tagExifFileInfo{
	char	Make[32]; 
	char	Model[32]; 
	char	Version[32]; 
	char	DateTime[32]; 
	char	CopyRight[32]; 

	UINT	Height; 
	UINT	Width;
	UINT	Orientation; 
	UINT	ColorSpace; 
	UINT	Process;
	UINT	Flash; 

	UINT	FocalLengthNum; 
	UINT	FocalLengthDen; 

	UINT	ExposureTimeNum; 
	UINT	ExposureTimeDen; 

	UINT	FNumberNum; 
	UINT	FNumberDen; 

	UINT	ApertureFNumber; 

	int		SubjectDistanceNum; 
	int		SubjectDistanceDen; 

	UINT	CCDWidth;

	int		ExposureBiasNum; 
	int		ExposureBiasDen; 


	int		WhiteBalance; 

	UINT	MeteringMode; 

	int		ExposureProgram;

	UINT	ISOSpeedRatings[2]; 
	
	UINT	FocalPlaneXResolutionNum;
	UINT	FocalPlaneXResolutionDen;

	UINT	FocalPlaneYResolutionNum;
	UINT	FocalPlaneYResolutionDen;

	UINT	FocalPlaneResolutionUnit;

	UINT	XResolutionNum;
	UINT	XResolutionDen;
	UINT	YResolutionNum;
	UINT	YResolutionDen;
	UINT	RUnit; 

	int		BrightnessNum; 
	int		BrightnessDen; 

	char	UserComments[150];
}ExifFileInfo;


#ifdef __cplusplus
extern "C" {
#endif


int SsbSipJPEGDecodeInit(void);
int SsbSipJPEGEncodeInit(void);
JPEG_ERRORTYPE SsbSipJPEGDecodeExe(int dev_fd);
JPEG_ERRORTYPE SsbSipJPEGEncodeExe(int dev_fd, ExifFileInfo *Exif, JPEG_SCALER scaler);
void *SsbSipJPEGGetDecodeInBuf(int dev_fd, long size);
void *SsbSipJPEGGetDecodeOutBuf (int dev_fd, long *size);
void *SsbSipJPEGGetEncodeInBuf(int dev_fd, long size);
void *SsbSipJPEGGetEncodeOutBuf (int dev_fd, long *size);
JPEG_ERRORTYPE SsbSipJPEGSetConfig (JPEGConf type, INT32 value);
JPEG_ERRORTYPE SsbSipJPEGGetConfig (JPEGConf type, INT32 *value);
JPEG_ERRORTYPE SsbSipJPEGDecodeDeInit (int dev_fd);
JPEG_ERRORTYPE SsbSipJPEGEncodeDeInit (int dev_fd);


#ifdef __cplusplus
}
#endif
#endif

#endif

