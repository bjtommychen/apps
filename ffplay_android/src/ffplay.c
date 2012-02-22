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
 *	$Id$
 *******************************************************************************/
#include "libavutil/avstring.h"
//#include "libavutil/colorspace.h"
#include "libavutil/mathematics.h"
#include "libavutil/pixdesc.h"
#include "libavutil/imgutils.h"
#include "libavutil/dict.h"
#include "libavutil/parseutils.h"
#include "libavutil/samplefmt.h"
#include "libavutil/avassert.h"
#include "libavformat/avformat.h"
#include "libavdevice/avdevice.h"
#include "libswscale/swscale.h"
//#include "libavcodec/audioconvert.h"
#include "libavutil/opt.h"
#include "libavcodec/avfft.h"
#include "libswresample/swresample.h"

#include "time.h"

#define DEBUG 1
#include <android/log.h>

#if DEBUG
#  define  D(x...)  __android_log_print(ANDROID_LOG_DEBUG,"FFNDK",x)
#else
#  define  D(...)  do {} while (0)
#endif

#if 1
#  define  I(x...)  __android_log_print(ANDROID_LOG_INFO,"FFNDK",x)
#else
#  define  I(...)  do {} while (0)
#endif

#define log D
#include "libffplay_ndk.h"

/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/
#define VIDEO_DATAIN_SIZE (1024*200)

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
int64_t time_start, time_stop;
float time_diff;

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/
static void picture_yuv420_save(FILE *fp, AVFrame *picture, int xsize, int ysize)
{
	int i;
	int len;

	// Note: xsize <= linesize[x];
	//Y
	for (i = 0; i < ysize; i++)
		fwrite(picture->data[0] + i * picture->linesize[0], 1, xsize, fp);
	//U
	for (i = 0; i < ysize / 2; i++)
		fwrite(picture->data[1] + i * picture->linesize[1], 1, xsize / 2, fp);
	//V
	for (i = 0; i < ysize / 2; i++)
		fwrite(picture->data[2] + i * picture->linesize[2], 1, xsize / 2, fp);
}

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

int FFNDK_init()
{
	avcodec_init();
	avcodec_register_all();
	av_register_all();
	return 0;
}

int FFNDK_showlibinfo()
{
	printf("avcodec version %d\n", avcodec_version());
	printf("avcodec config:\n %s\n", avcodec_configuration());
	printf("avcodec license:\n %s\n", avcodec_license());

	printf("avformat version %d\n", avformat_version());
	printf("avformat config:\n %s\n", avformat_configuration());
	printf("avformat license:\n %s\n", avformat_license());

	return 0;
}

void FFNDK_decode_video(const char *filename, int write_output)
{
	AVCodec *codec;
	AVCodecContext *c = NULL;
	int frame, got_picture, len;
	FILE *f, *outfile = NULL;
	AVFrame *picture;
	char buf[1024];
	uint8_t inbuf[VIDEO_DATAIN_SIZE];
	AVPacket avpkt;

	av_init_packet(&avpkt);

	/* set end of buffer to 0 (this ensures that no overreading happens for damaged mpeg streams) */
	memset(inbuf, 0, VIDEO_DATAIN_SIZE);

	printf("Video decoding\n");

	/* find the mpeg1 video decoder */
	codec = avcodec_find_decoder(CODEC_ID_MPEG1VIDEO);
//	codec = avcodec_find_decoder(CODEC_ID_H264);
	if (!codec)
	{
		fprintf(stderr, "codec not found\n");
		exit(1);
	}

	c = avcodec_alloc_context3(codec);
	picture = avcodec_alloc_frame();

	if (codec->capabilities & CODEC_CAP_TRUNCATED
	)
		c->flags |= CODEC_FLAG_TRUNCATED; /* we do not send complete frames */

	/* For some codecs, such as msmpeg4 and mpeg4, width and height
	 MUST be initialized there because this information is not
	 available in the bitstream. */

	/* open it */
	if (avcodec_open(c, codec) < 0)
	{
		fprintf(stderr, "could not open codec\n");
		exit(1);
	}

	/* the codec gives us the frame size, in samples */

	f = fopen(filename, "rb");
	if (!f)
	{
		fprintf(stderr, "could not open %s\n", filename);
		exit(1);
	}

	time_start = av_gettime();
	frame = 0;
	for (;;)
	{
		avpkt.size = fread(inbuf, 1, VIDEO_DATAIN_SIZE, f);
		if (avpkt.size == 0)
			break;

		/* NOTE1: some codecs are stream based (mpegvideo, mpegaudio)
		 and this is the only method to use them because you cannot
		 know the compressed data size before analysing it.

		 BUT some other codecs (msmpeg4, mpeg4) are inherently frame
		 based, so you must call them with all the data for one
		 frame exactly. You must also initialize 'width' and
		 'height' before initializing them. */

		/* NOTE2: some codecs allow the raw parameters (frame size,
		 sample rate) to be changed at any frame. We handle this, so
		 you should also take care of it */

		/* here, we use a stream based decoder (mpeg1video), so we
		 feed decoder and see if it could decode a frame */
		avpkt.data = inbuf;
		while (avpkt.size > 0)
		{
			got_picture = 0;
			len = avcodec_decode_video2(c, picture, &got_picture, &avpkt);
			D("avpkt.size:%d, decode_use_size:%d. \n", avpkt.size, len);

			if (len < 0)
			{
				fprintf(stderr, "Error while decoding frame %d\n", frame);
				exit(1);
			}
			if (got_picture)
			{
				if (frame % 100 == 0)
				{
					printf("saving frame %3d\n", frame);
				}

				if (outfile == NULL && write_output)
				{
					buf[0] = 0;
					sprintf(buf, "./%dx%d.yuv", c->width, c->height);
					outfile = fopen(buf, "wb");
					if (!outfile)
					{
						fprintf(stderr, "could not open %s\n", buf);
						exit(1);
					}
					printf("writing yuv data to %s\n", buf);

					buf[0] = 0;
				}
				/* the picture is allocated by the decoder. no need to
				 free it */
				if (frame == 0)
				{
					printf("yuv420 save: w:%d, h:%d, linesize:%d,%d,%d\n", picture->width, picture->height,
							picture->linesize[0], picture->linesize[1], picture->linesize[2]);
				}
				if (write_output)
					picture_yuv420_save(outfile, picture, c->width, c->height);

				frame++;
			} // got pic

			avpkt.size -= len;
			avpkt.data += len;
		}

//		if (frame > 1000)
//			break;
	}
	time_stop = av_gettime();
	time_diff = (time_stop-time_start)/1000.0;

	fclose(f);
	if (outfile)
		fclose(outfile);

	avcodec_close(c);
	av_free(c);
	av_free(picture);

	printf("Total %d frames. last %.2f s.\nSpeed is %.2f fps.\n ", frame,  time_diff/1000.0, (float)frame*1000.0/time_diff);
}

#if 0
void FFNDK_demux_example(const char *filename, int isSDLshow)
{

	AVFormatContext *c;
	AVPacket avpkt;
	FILE *fa, *fv;
	char str[128];
	int i;
	int audioidx, videoidx;

	printf(" avfile decoding ... \n");

	c = avformat_alloc_context();
	if (avformat_open_input(&c, filename, NULL, 0) < 0)
	{
		fprintf(stderr, "could not open file\n");
		return;
	}
	c->flags |= AVFMT_FLAG_GENPTS;

	if (avformat_find_stream_info(c, 0) < 0)
	{
		fprintf(stderr, "find stream failed. \n");
		return;
	}

	log("nb_streams is %d\n", c->nb_streams);
	for (i = 0; i < c->nb_streams; i++)
	{
		printf("\nStream #%d: \n ", i);
		switch (c->streams[i]->codec->codec_type)
		{
			case AVMEDIA_TYPE_VIDEO:
			videoidx = i;
			printf("Video.");
			break;
			case AVMEDIA_TYPE_AUDIO:
			audioidx = i;
			printf("Audio.");
			break;
			default:
			printf("OTHER AVMEDIA. ");
			break;
		}
		printf("codec_name:%s. id:%xH. tag:%xH", c->streams[i]->codec->codec_name, c->streams[i]->codec->codec_id,
				&(c->streams[i]->codec->codec_tag));
	}
	printf("\n");

	// Demux start
	if (!isSDLshow)
	{
		str[0] = 0;
		strcpy(str, filename);
		strcat(str, ".audiostream");
		fa = fopen(str, "wb");
		if (!fa)
		{
			fprintf(stderr, "could not open %s\n", str);
			return;
		}
		log("open stream files %s to write .\n", str);

		str[0] = 0;
		strcpy(str, filename);
		strcat(str, ".videostream");
		fv = fopen(str, "wb");
		if (!fv)
		{
			fprintf(stderr, "could not open %s\n", str);
			return;
		}
		log("open stream files %s to write .\n", str);

	}

	while (av_read_frame(c, &avpkt) >= 0)
	{
		if (!isSDLshow)
		{
			if (avpkt.stream_index == videoidx)
			{
				fwrite(avpkt.data, 1, avpkt.size, fv);
//				log("write audio %d bytes.\n", avpkt.size);
			}
			if (avpkt.stream_index == audioidx)
			{
				fwrite(avpkt.data, 1, avpkt.size, fa);
			}

		}
	}

	if (!isSDLshow)
	{
		fclose(fa);
		fclose(fv);
	}
	avformat_free_context(c);

}
#endif
