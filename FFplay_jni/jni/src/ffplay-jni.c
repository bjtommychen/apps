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
#include <string.h>
#include <jni.h>
#include <android/log.h>

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
//#include "libavdevice/avdevice.h"
//#include "libswscale/swscale.h"
//#include "libavcodec/audioconvert.h"
#include "libavutil/opt.h"
#include "libavcodec/avfft.h"
#include "libswresample/swresample.h"

#include "packet_queue.h"

/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/
/*
 jboolean    z;
 jbyte       b;
 jchar       c; 16bit, tommy
 jshort      s;
 jint        i;
 jlong       j;
 jfloat      f;
 jdouble     d;
 jobject     l;
 jstring     t = (*env)->NewStringUTF(env, "Hello from JNI !");
 jbyteArray jarray_rgb = (*env)->NewByteArray(env, nOutSize);
 char *str = (*env)->GetStringUTFChars(env, jstring, 0);
 (*env)->ReleaseStringUTFChars(env, jstring, str);

 http://www.360doc.com/content/10/1229/17/5116642_82372464.shtml

 */

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/
#define DEBUG 1

#if DEBUG
#  define  D(x...)  __android_log_print(ANDROID_LOG_DEBUG,"ffplay-jni",x)
#else
#  define  D(...)  do {} while (0)
#endif

#if DEBUG
#  define  I(x...)  __android_log_print(ANDROID_LOG_INFO,"ffplay-jni",x)
#else
#  define  I(...)  do {} while (0)
#endif

#if DEBUG
#  define  W(x...)  __android_log_print(ANDROID_LOG_WARN,"ffplay-jni",x)
#else
#  define  W(...)  do {} while (0)
#endif

#if DEBUG
#  define  E(x...)  __android_log_print(ANDROID_LOG_ERROR,"ffplay-jni",x)
#else
#  define  E(...)  do {} while (0)
#endif

#if DEBUG
#  define  V(x...)  __android_log_print(ANDROID_LOG_VERBOSE,"ffplay-jni",x)
#else
#  define  V(...)  do {} while (0)
#endif

#define PCMOUTLEN			(240*1024)
#define MAGIC_ID				(0xdeaf)
/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/
typedef struct
{
	uint16_t magic; //must be MAGIC_ID
	uint16_t header_len; // sizeof this structure.
	uint16_t type; //1: audio, 2:video
	//Audio
	uint16_t samplerate, channel, bitspersample;
	//Video
	uint16_t yuv_format;
	uint16_t width, height;
	uint16_t linesizeY, linesizeU, linesizeV;
	//Duration
	uint16_t duration;

	uint16_t null[64];
} DecOutInfo;

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
PacketQueue videoq;
PacketQueue audioq;

AVCodec *acodec, *vcodec;
AVCodecContext *ac, *vc;
AVStream *audio_st, *video_st;
AVFrame *vframe, *aframe;
AVPacket avpkt;
AVFormatContext *fc;
int audioidx, videoidx;
int hasVideo, hasAudio;

int frame, got_picture, len;
FILE *f = NULL;
char buf[1024];
char streaminfo[1024] = "streaminfo";

DecOutInfo decinfo;
unsigned char *vout = 0;

unsigned char *aout = 0;
int aout_offset = 0;
int aout_len = 0;

//jbyteArray jarray_hdr = NULL;
jintArray jarray_rgb = NULL;
//jbyteArray jarray_aud = NULL;

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

#define AUDIO_RESAMPLE_SIZE		(1024*20)
static int audio_resample_converter(AVCodecContext *audioc, unsigned char *src,
		int nb_samples, unsigned char *dst, int* dstlen)
{ // Need format convert, check swr_convert() for details.
	struct SwrContext *swr_ctx;
	unsigned char swr_tmpbuff[AUDIO_RESAMPLE_SIZE];
	unsigned char *in[] =
	{ src };
	unsigned char *out[] =
	{ swr_tmpbuff };
	int len2;

	V("enter resample !\n");
	swr_ctx = swr_alloc_set_opts(NULL, audioc->channel_layout,
			AV_SAMPLE_FMT_S16, audioc->sample_rate, audioc->channel_layout,
			audioc->sample_fmt, audioc->sample_rate, 0, NULL);
	swr_init(swr_ctx);
	len2 = swr_convert(swr_ctx, (uint8_t **) out,
			sizeof(swr_tmpbuff) / audioc->channels
					/ av_get_bytes_per_sample(AV_SAMPLE_FMT_S16),
			(const uint8_t **) in, nb_samples);
	swr_free(&swr_ctx);
	V("resample output %d samples.\n", len2);
	len2 *= audioc->channels * av_get_bytes_per_sample(AV_SAMPLE_FMT_S16);
	memcpy(dst, swr_tmpbuff, len2);
	if (dstlen)
		*dstlen = len2;

	return len2;
}

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/
jstring Java_com_tommy_ffplayer_FFplay_FFplayGetStreamInfo(JNIEnv* env,
		jobject thiz)
{
	return (*env)->NewStringUTF(env, streaminfo);
}

/*
 * Init
 */
jint Java_com_tommy_ffplayer_FFplay_FFplayInit(JNIEnv* env, jobject thiz)
{
	D("FFplayInit called ! ");

	I("\n**************************Android*******************************\n");
	I(
			"*  FFplayer based on libffmpeg, build time: %s %s \n", __DATE__, __TIME__);
#ifdef OPT_TOMMY_NEON
	I("***************  TOMMY OPTIMIZED USING NEON  ********************\n");
#endif
	I("*********  avcodec version %d\n", avcodec_version());
	I("*********  avformat version %d\n", avformat_version());
	I("*****************************************************************\n");

//	avcodec_init();
	avcodec_register_all();
	av_register_all();

	decinfo.magic = MAGIC_ID;
	decinfo.header_len = sizeof(DecOutInfo);

//	jarray_hdr = (*env)->NewByteArray(env, decinfo.header_len);

	D("FFplayInit done !");
	return 0;
}

/*
 * return
 */
jint Java_com_tommy_ffplayer_FFplay_FFplayExit(JNIEnv* env, jobject thiz)
{
//	(*env)->DeleteLocalRef(env, jarray_hdr);
	return 0;
}

/*
 * OpenFile
 */

jint Java_com_tommy_ffplayer_FFplay_FFplayOpenFile(JNIEnv* env, jobject thiz,
		jstring fname)
{
	int i;
	const char *filename = (*env)->GetStringUTFChars(env, fname, 0);

	av_init_packet(&avpkt);
	packet_queue_init(&audioq);
	packet_queue_init(&videoq);

	I("avfile decoding ... %s \n", filename);

	fc = avformat_alloc_context();
	if (avformat_open_input(&fc, filename, NULL, 0) < 0)
	{
		E( "could not open file\n");
		return 1;
	}
	(*env)->ReleaseStringUTFChars(env, fname, filename);

	fc->flags |= AVFMT_FLAG_GENPTS;

	if (avformat_find_stream_info(fc, 0) < 0)
	{
		E( "find stream failed. \n");
		return 1;
	}

	streaminfo[0] = 0;
	strcpy(streaminfo, "-------------------------------------------------\n");
	sprintf(streaminfo, "%snb_streams is %d\n", streaminfo, fc->nb_streams);
	hasVideo = hasAudio = 0;

	for (i = 0; i < fc->nb_streams; i++)
	{
		AVStream *st = fc->streams[i];
		sprintf(streaminfo, "%sStream #%d: \n", streaminfo, i);

		switch (fc->streams[i]->codec->codec_type)
		{
		case AVMEDIA_TYPE_VIDEO:
			videoidx = i;
			sprintf(streaminfo, "%sVideo. ", streaminfo);
			hasVideo = 1;
			break;
		case AVMEDIA_TYPE_AUDIO:
			audioidx = i;
			sprintf(streaminfo, "%sAudio. ", streaminfo);
			hasAudio = 1;
			break;
		default:
			I("OTHER AVMEDIA. ");
			break;
		}
		avcodec_string(buf, sizeof(buf), st->codec, 1);
		sprintf(streaminfo,
				"%s\n[0x%x]:%s, \ncodec_name:'%s'. id:%05xH. tag:%08xH. time_base:%d, %d\n",
				streaminfo, st->id, buf, st->codec->codec_name,
				st->codec->codec_id, (st->codec->codec_tag),
				st->codec->time_base.num, st->codec->time_base.den);
	};

	I("%s", streaminfo);

	acodec = vcodec = 0;
	ac = vc = 0;
	if (hasVideo)
	{
		vc = fc->streams[videoidx]->codec;
		vcodec = avcodec_find_decoder(vc->codec_id);
	}
	if (hasAudio)
	{
		ac = fc->streams[audioidx]->codec;
		acodec = avcodec_find_decoder(ac->codec_id);
	}

	if (!acodec && !vcodec)
	{
		E( "at least one codec not found\n");
		return (1);
	}

	if (hasVideo)
	{
		vframe = avcodec_alloc_frame();
		if (vcodec->capabilities & CODEC_CAP_TRUNCATED)
			vc->flags |= CODEC_FLAG_TRUNCATED; /* we do not send complete frames */
	}
	if (hasAudio)
		aframe = avcodec_alloc_frame();

	/* For some codecs, such as msmpeg4 and mpeg4, width and height
	 MUST be initialized there because this information is not
	 available in the bitstream. */

	/* open it */
	if (acodec && avcodec_open2(ac, acodec, 0) < 0)
	{
		E( "could not open acodec.");
		return (1);
	}
	if (vcodec && avcodec_open2(vc, vcodec, 0) < 0)
	{
		E( "could not open vcodec.");
		return (1);
	}

	I( "OpenFile done.");
	return 0;
}

/*
 * CloseFile
 */
jint Java_com_tommy_ffplayer_FFplay_FFplayCloseFile(JNIEnv* env, jobject thiz)
{
	packet_queue_abort(&audioq);
	packet_queue_end(&audioq);
	packet_queue_abort(&videoq);
	packet_queue_end(&videoq);

	if (ac)
	{
		avcodec_close(ac);
		av_free(ac);
	}
	if (vc)
	{
		avcodec_close(vc);
		av_free(vc);
	}
	if (vframe)
		av_free(vframe);
	if (aframe)
		av_free(aframe);

	if (vout)
	{
		free(vout);
		vout = NULL;
	}
	if (aout)
	{
		free(aout);
		aout = NULL;
		aout_offset = 0;
	}
	if (jarray_rgb)
	{
		(*env)->DeleteLocalRef(env, jarray_rgb);
		jarray_rgb = NULL;
	}
//	if (jarray_aud)
//	{
//		(*env)->DeleteLocalRef(env, jarray_aud);
//		jarray_aud = NULL;
//	}

	return 0;
}

/*
 * DecodeFrame
 * return the decoded data.
 * Tommy: use first 5 int for info header.
 * int 0 : 1 for audio, 2 for video.
 */

jbyteArray Java_com_tommy_ffplayer_FFplay_FFplayDecodeFrame(JNIEnv* env,
		jobject thiz)
{
	int hdr_len = decinfo.header_len;
	jbyteArray jarray_hdr;
	int got_audio_frame = 0;

	while (av_read_frame(fc, &avpkt) >= 0)
	{
		if (hasVideo && avpkt.stream_index == videoidx)
		{
//			D("Got video frame.");
			while (avpkt.size > 0)
			{
				len = avcodec_decode_video2(vc, vframe, &got_picture, &avpkt);
				if (got_picture)
				{
					V(
							"got video frame. %d x %d. linesize %d,%d,%d", vframe->width, vframe->height, vframe->linesize[0], vframe->linesize[1], vframe->linesize[2]);
					decinfo.type = 2;
					decinfo.width = vframe->width;
					decinfo.height = vframe->height;
					decinfo.linesizeY = vframe->linesize[0];
					decinfo.linesizeU = vframe->linesize[1];
					decinfo.linesizeV = vframe->linesize[2];
					decinfo.duration = fc->duration / AV_TIME_BASE;
					V("duration is %d", decinfo.duration);
					jarray_hdr = (*env)->NewByteArray(env, hdr_len);
					(*env)->SetByteArrayRegion(env, jarray_hdr, 0, hdr_len,
							(jbyte*) &decinfo);
					return jarray_hdr;
				}
			}
		}

		// Decode Audio
		if (hasAudio && avpkt.stream_index == audioidx)
		{
			packet_queue_put(&audioq, &avpkt);

			if (audioq.nb_packets < 1)
			{
				D("audioq.nb_packets .  NO.%d", audioq.nb_packets);
			}
			else
			{
				D( "got audio frame. %d samples.", aframe->nb_samples);
				decinfo.bitspersample = 16; //Support all, include float format.
				decinfo.type = 1;
				jarray_hdr = (*env)->NewByteArray(env, hdr_len);
				(*env)->SetByteArrayRegion(env, jarray_hdr, 0, hdr_len,
						(jbyte*) &decinfo);
				return jarray_hdr;
			}
		}
//		if (frame > 1000)
//			break;
	}

	D("FFplayDecodeFrame done.");
	return NULL;
}

jintArray Java_com_tommy_ffplayer_FFplay_FFplayConvertRGB(JNIEnv* env,
		jobject thiz)
{
	int i, j;
	int len = vframe->height * vframe->linesize[0];
	int *dst;
	char *src = vframe->data[0];

	if (vout == NULL)
	{
		D("FFplayConvertRGB alloc mem done.");
		vout = malloc(len * sizeof(int));
	}
	if (jarray_rgb == NULL)
	{
		jarray_rgb = (*env)->NewIntArray(env, len);
	}
	dst = (int*) vout;
	for (j = 0; j < vframe->height; j++)
	{
		for (i = 0; i < vframe->linesize[0]; i++)
		{ // Convert Y to RGB888
			*dst++ = (*src << 16) | (*src << 8) | (*src);
			src++;
		}
	}
	(*env)->SetIntArrayRegion(env, jarray_rgb, 0, len, (jint*) vout);

	return jarray_rgb;
}

jint Java_com_tommy_ffplayer_FFplay_FFplayConvertGray(JNIEnv* env, jobject thiz,
		jintArray buf)
{
	int i, j;
	int len = vframe->height * vframe->linesize[0];
	int *dst;
	char *src = vframe->data[0];
	jint *elems = (*env)->GetIntArrayElements(env, buf, (jboolean*) NULL);

	dst = (int*) elems;
	for (j = 0; j < vframe->height; j++)
	{
		for (i = 0; i < vframe->linesize[0]; i++)
		{ // Convert Y to RGB888
			*dst++ = (*src << 16) | (*src << 8) | (*src);
			src++;
		}
	}
	//	ReferenceTable overflow (max=1024)
	(*env)->ReleaseIntArrayElements(env, buf, elems, 0);

	return 0;
}

jbyteArray Java_com_tommy_ffplayer_FFplay_FFplayGetPCM(JNIEnv* env,
		jobject thiz)
{
	jbyteArray jarray_aud;
	jbyte * outbuf;
	int outsize;
	int got_audio_frame;

	if (aout == NULL)
	{	// Allocate the memory if the 1st enter.
		aout_len = PCMOUTLEN;
		D("FFplayGetPCM alloc %d mem done.", aout_len);
		aout = malloc(aout_len);
	}

	aout_offset = 0;
	// Loop to decoded all audio packets.
	while (audioq.nb_packets > 0 && aout_offset < aout_len)
	{
		D("packet get.");
		packet_queue_get(&audioq, &avpkt, 0);
		outsize = 0;
		while (avpkt.size > 0)
		{
			AVFrame *decoded_frame = NULL;
			avcodec_get_frame_defaults(aframe);

			got_audio_frame = 0;
			len = avcodec_decode_audio4(ac, aframe, &got_audio_frame, &avpkt);
			if (len < 0)
			{
				D("avpkt.size  %d bytes left.\n", avpkt.size);
				E("Error while decoding\n");
				avpkt.size = 0;
			}
			else
			{
				avpkt.size -= len;
				avpkt.data += len;

				if (got_audio_frame)
				{
					outbuf = (jbyte*) aframe->data[0];
					outsize = av_samples_get_buffer_size(NULL, ac->channels,
							aframe->nb_samples, ac->sample_fmt, 1);
					if (ac->sample_fmt == AV_SAMPLE_FMT_S16)
					{
						memcpy(aout + aout_offset, aframe->data[0], outsize);
					}
					else
					{	// Do convert from float to pcm.
						outsize = audio_resample_converter(ac, aframe->data[0],
								aframe->nb_samples,
								(uint8_t*) aout + aout_offset, NULL);
					}
				}
			}
		} //while

		aout_offset += outsize;

		if ((aout_offset + outsize) >= aout_len)
		{ //buffer full.
			break;
		}
	}

	D( "return audio frame. %d bytes.", aout_offset);
	jarray_aud = (*env)->NewByteArray(env, aout_offset);
	(*env)->SetByteArrayRegion(env, jarray_aud, 0, aout_offset, aout);
	aout_offset = 0;

	return jarray_aud;
}
