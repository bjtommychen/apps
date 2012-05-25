
/************************************************************************
* Use of this software is covered by the terms and conditions
* of the ZSP License Agreement under which it is provided.
*
* Copyright (C) 2009 Verisilicon, Inc.  All rights reserved.
************************************************************************/


#ifndef __LIBMP3DEC_H__
#define __LIBMP3DEC_H__

#ifdef __cplusplus
extern "C"
{
#endif

#define MPEG_BUFSZ 			(977) // Max. data size in words for one frame. 
#define INPUT_BUFFER_GUARD	4

enum MP3D_STATUS {
  MP3D_STATUS_SUCCESS,      //decode one frame success
  MP3D_STATUS_FAILED_UNDERFLOW, //the data in input buffer is not enough to decode a frame
  MP3D_STATUS_FAILED_LOSTSYNC, //the header of current frame can't be found£¬one or more frames will be skipped.
  MP3D_STATUS_FAILED        // error happened in decoding current frame, only current frame will be skipped
};


enum MP3D_MSG {
  MP3D_MSG_CONTINUE,        /* continue to run */
  MP3D_MSG_STOP,            /* stop normally and return MP3D_STATUS_SUCCESS */
  MP3D_MSG_BREAK,           /* stop and return MP3D_STATUS_FAILED */
  MP3D_MSG_IGNORE           /* stop and return */
};

enum MPEG_VERSION {
  MPEG_1,
  MPEG_2,
  MPEG_2_5
};

enum MP3_LAYER {
  MP3_LAYER_I   = 1,
  MP3_LAYER_II  = 2,
  MP3_LAYER_III = 3,
};

enum MP3_CHMODE {
  MP3_CHMODE_SINGLE_CHANNEL,
  MP3_CHMODE_DUAL_CHANNEL,
  MP3_CHMODE_JOINT_STEREO,
  MP3_CHMODE_STEREO,
};

enum MP3_EMPHASIS {
  MP3_EMPHASIS_NONE	      = 0,		/* no emphasis */
  MP3_EMPHASIS_50_15_US	  = 1,		/* 50/15 microseconds emphasis */
  MP3_EMPHASIS_RESERVED   = 2,
  MP3_EMPHASIS_CCITT_J_17 = 3 		/* CCITT J.17 emphasis */
};

typedef void* HANDLE_MP3D;

struct MP3DEC_STREAM{
  /* input */
  unsigned short* pb_stream;        /* the pointer provided by application, with streamsize words available for decode core */
  unsigned int streamsize;      /* the word size of the stream buffer, <= */
  /* output*/
  unsigned short* pb_unused;		/* pointer to the unused buffer, which is not consumed by decode core,  if NULL, means no unused buffer*/
  unsigned int unusedsize;		/* the word size of the unused buffer */
};

struct MP3DEC_HEADER {
  enum MPEG_VERSION mpegversion;	/* mpeg version (1, 2, or 2.5) */
  enum MP3_LAYER layer;				/* audio layer (1, 2, or 3) */
  enum MP3_CHMODE mode;			/* channel mode */
  int mode_extension;					/* additional mode info */
  enum MP3_EMPHASIS emphasis;		/* de-emphasis to use */
  unsigned long bitrate;					/* stream bitrate (bps) */
  unsigned int samplerate;				/* sampling frequency (Hz) */
  unsigned short crc_check;				/* frame CRC accumulator */

  /*    XING VBR TAG
  ref http://gabriel.mp3-tech.org/mp3infotag.html
  */
  unsigned long vbr_flags;      /* Xing Tag flags 
                                  enum {
                                  XING_FRAMES = 0x00000001L,
                                  XING_BYTES  = 0x00000002L,
                                  XING_TOC    = 0x00000004L,
                                  XING_SCALE  = 0x00000008L
                                }; */
  unsigned long vbr_frames;     /* total frame amount */
  unsigned long vbr_bytes;      /* total byte size of audio stream */
  unsigned short vbr_toc[101];  /* ref Xing Tag Spec */
  unsigned long vbr_scale;      /* VBR quality indicator: 0=best 100=worst */
};

struct MP3DEC_PCM {
  /* output */
  unsigned int samplerate;		/* sampling frequency (Hz),maintain by decoder */
  unsigned short channels;		/* number of channels ,maintain by decoder*/
  unsigned short length;			/* number of samples per channel, maintain by decoder */
  /* input */
  unsigned short* pOutBuffer;      /* Output Buffer, maintain by APP*/
  unsigned int OutBufferSize;        /* Size of one Output Buffer, in words, maintain by APP*/
};

struct MP3DEC_INITCFG {
  unsigned short* pCoreMemPool;     /* Memory Pool for Core */
  unsigned int CoreMemPoolSize;    /* Size of Memory Pool, in words */
    
};

HANDLE_MP3D mp3decoder_init(void *userdata,
		      enum MP3D_MSG (*header_func)(void *, struct MP3DEC_HEADER const *),
		      struct MP3DEC_INITCFG *);

enum MP3D_STATUS mp3decoder_run(HANDLE_MP3D, struct MP3DEC_STREAM*, struct MP3DEC_PCM *);

int mp3decoder_finish(HANDLE_MP3D);

const char *get_libmp3dec_version(void);

#ifdef __cplusplus
}
#endif


#endif //__LIBMP3DEC_H__
