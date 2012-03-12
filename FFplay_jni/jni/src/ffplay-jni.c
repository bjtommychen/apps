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
 jbyteArray jarray = (*env)->NewByteArray(env, nOutSize);
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

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
AVCodec *acodec, *vcodec;
AVCodecContext *ac, *vc;
AVStream *audio_st, *video_st;
AVFrame *vframe, *aframe;
AVPacket avpkt;
AVFormatContext *fc;
int audioidx, videoidx;

int frame, got_picture, len;
FILE *f = NULL;
char buf[1024];
char streaminfo[1024] = "streaminfo";

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

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
	I("avcodec version %d\n", avcodec_version());
	I("avformat version %d\n", avformat_version());
	I("*****************************************************************\n");

//	avcodec_init();
	avcodec_register_all();
	av_register_all();

	D("FFplayInit done !");
	return 0;
}

/*
 * return
 */
jint Java_com_tommy_ffplayer_FFplay_FFplayExit(JNIEnv* env, jobject thiz)
{
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
	sprintf(streaminfo, "nb_streams is %d\n", streaminfo, fc->nb_streams);
	for (i = 0; i < fc->nb_streams; i++)
	{
		AVStream *st = fc->streams[i];
		sprintf(streaminfo, "%sStream #%d: \n", streaminfo, i);
		switch (fc->streams[i]->codec->codec_type)
		{
		case AVMEDIA_TYPE_VIDEO:
			videoidx = i;
			sprintf(streaminfo, "%sVideo. ", streaminfo);
			break;
		case AVMEDIA_TYPE_AUDIO:
			audioidx = i;
			sprintf(streaminfo, "%sAudio. ", streaminfo);
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
	vc = fc->streams[videoidx]->codec;
	ac = fc->streams[audioidx]->codec;

	vcodec = avcodec_find_decoder(vc->codec_id);
	acodec = avcodec_find_decoder(ac->codec_id);
	if (!acodec || !vcodec)
	{
		E( "codec not found\n");
		return (1);
	}

	vframe = avcodec_alloc_frame();
	aframe = avcodec_alloc_frame();

	if (vcodec->capabilities & CODEC_CAP_TRUNCATED)
		vc->flags |= CODEC_FLAG_TRUNCATED; /* we do not send complete frames */

	/* For some codecs, such as msmpeg4 and mpeg4, width and height
	 MUST be initialized there because this information is not
	 available in the bitstream. */

	/* open it */
	if (avcodec_open2(ac, acodec, 0) < 0)
	{
		E( "could not open acodec.");
		return (1);
	}
	if (avcodec_open2(vc, vcodec, 0) < 0)
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
	avcodec_close(ac);
	av_free(ac);
	avcodec_close(vc);
	av_free(vc);
	av_free(vframe);
	av_free(aframe);

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

	static jint decinfo_header[10];

	while (av_read_frame(fc, &avpkt) >= 0)
	{
		if (avpkt.stream_index == videoidx)
		{
			D("Got video frame.");
			while (avpkt.size > 0)
			{
				len = avcodec_decode_video2(vc, vframe, &got_picture, &avpkt);
				if (got_picture)
				{
					D(
							"got video frame. %d x %d.", vframe->width, vframe->height);
					jbyteArray jarray = (*env)->NewByteArray(env,
							(vframe->width * vframe->height * 3 / 2)+40);

					decinfo_header[0] = 2;
					(*env)->SetByteArrayRegion(env, jarray, 0, 40, decinfo_header);
					(*env)->SetByteArrayRegion(env, jarray, 40,
							vframe->width * vframe->height, vframe->data[0]);
					(*env)->SetByteArrayRegion(env, jarray,
							vframe->width * vframe->height +40,
							vframe->width * vframe->height / 4,
							vframe->data[1]);
					(*env)->SetByteArrayRegion(env, jarray,
							vframe->width * vframe->height * 5 / 4 + 40,
							vframe->width * vframe->height / 4,
							vframe->data[2]);
					return jarray;
				}
			}
			break;
		}

		// Decode Audio
		if (avpkt.stream_index == audioidx)
		{
			while (avpkt.size > 0)
			{
				int got_audio_frame = 0;
				AVFrame *decoded_frame = NULL;

//				D("Got audio frame. ");
				avcodec_get_frame_defaults(aframe);

				len = avcodec_decode_audio4(ac, aframe, &got_audio_frame,
						&avpkt);
				if (len < 0)
				{
					D("avpkt.size  %d bytes left.\n", avpkt.size);
					E("Error while decoding\n");
//				if (ending == TRUE)
//				{
//					avpkt.size = 0;
//					break;
//				}
					avpkt.size -= 1;
					avpkt.data += 1;
					continue;
				}

//			{
//				char fmt_str[128] = "";
//				I(
//						"audio stream: ch:%d, srate:%d, samples:%d, fmt:%s\n", ac->channels, ac->sample_rate, aframe->nb_samples, av_get_sample_fmt_string(fmt_str, sizeof(fmt_str), ac->sample_fmt));
//			}

				if (got_audio_frame)
				{
					D("got audio frame. %d samples.", aframe->nb_samples);
					jbyte *outbuf = (jbyte*) aframe->data[0];
					int outsize = av_samples_get_buffer_size(NULL, ac->channels,
							aframe->nb_samples, ac->sample_fmt, 1);
					jbyteArray jarray = (*env)->NewByteArray(env, outsize + 40);
					decinfo_header[0] = 1;
					(*env)->SetByteArrayRegion(env, jarray, 0, 40, decinfo_header);
					(*env)->SetByteArrayRegion(env, jarray, 40, outsize, outbuf);

					return jarray;
				}

				avpkt.size -= len;
				avpkt.data += len;
			}
			break;
		}

//		if (frame > 1000)
//			break;
	}

	D("FFplayDecodeFrame done.");
	return NULL;
}

