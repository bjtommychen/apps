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

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

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

	I("nb_streams is %d\n", fc->nb_streams);
	for (i = 0; i < fc->nb_streams; i++)
	{
		AVStream *st = fc->streams[i];
		I("Stream #%d: \n", i);
		switch (fc->streams[i]->codec->codec_type)
		{
		case AVMEDIA_TYPE_VIDEO:
			videoidx = i;
			I("Video.");
			break;
		case AVMEDIA_TYPE_AUDIO:
			audioidx = i;
			I("Audio.");
			break;
		default:
			I("OTHER AVMEDIA. ");
			break;
		}
		avcodec_string(buf, sizeof(buf), st->codec, 1);
		I(
				"\n[0x%x]:%s, \ncodec_name:'%s'. id:%05xH. tag:%08xH. time_base:%d, %d\n", st->id, buf, st->codec->codec_name, st->codec->codec_id, (st->codec->codec_tag), st->codec->time_base.num, st->codec->time_base.den);
	};

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
//		return (1);
	}
	if (avcodec_open2(vc, vcodec, 0) < 0)
	{
		E( "could not open vcodec.");
//		return (1);
	}

	/* the codec gives us the frame size, in samples */

//	f = fopen(filename, "rb");
//	if (!f)
//	{
//		E( "could not open %s\n", filename);
//		return (1);
//	}
	I( "OpenFile done.");
	return 0;
}

/*
 * CloseFile
 */
jint Java_com_tommy_ffplayer_FFplay_FFplayCloseFile(JNIEnv* env, jobject thiz)
{
	fclose(f);
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
 * return the decoded pcm data.
 */
jbyteArray Java_com_tommy_ffplayer_FFplay_FFplayDecodeFrame(JNIEnv* env,
		jobject thiz)
{

	while (av_read_frame(fc, &avpkt) >= 0)
	{
		if (avpkt.stream_index == videoidx)
		{
			D("skip video frame.");
			continue;
		}

		while (avpkt.size > 0 && avpkt.stream_index == audioidx)
		{
			int got_audio_frame = 0;
			AVFrame *decoded_frame = NULL;

			D("Got audio frame. ");
			avcodec_get_frame_defaults(aframe);

			len = avcodec_decode_audio4(ac, aframe, &got_audio_frame, &avpkt);
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
			{
				char fmt_str[128] = "";
				I(
						"audio stream: ch:%d, srate:%d, samples:%d, fmt:%s\n", ac->channels, ac->sample_rate, aframe->nb_samples, av_get_sample_fmt_string(fmt_str, sizeof(fmt_str), ac->sample_fmt));
			}

			if (got_audio_frame)
			{
				D("got audio frame. %d samples.", aframe->nb_samples);
				jbyte *outbuf = (jbyte*) aframe->data[0];
				int outsize = av_samples_get_buffer_size(NULL, ac->channels,
						aframe->nb_samples, ac->sample_fmt, 1);
				jbyteArray jarray = (*env)->NewByteArray(env, outsize);
				(*env)->SetByteArrayRegion(env, jarray, 0, outsize, outbuf);

				return jarray;

				/* if a frame has been decoded, output it */

//				fwrite(decoded_frame->data[0], 1, data_size, outfile);
			}

			avpkt.size -= len;
			avpkt.data += len;
		}
		break;

//		if (frame > 1000)
//			break;
	}

	D("FFplayDecodeFrame done.");
	return NULL;
}

#if 0
/*
 * Note: split original decode_input_read() into below 2 function: GetInputDataLen() and FillData().
 * Get 16-bit short length need to read from mp3 files. will be called in android app.
 * len: in short.
 */
jint Java_com_tommy_test_audiotest_AudioTest_mp3decGetInputDataLen(JNIEnv* env,
		jobject thiz)
{
	MP3_PLAYER *pplayer = &player;
	struct MP3DEC_STREAM *stream = &lstream;
	int len = 0, need_len;

	need_len = MIN(INPUT_BUFSZ - stream->unusedsize, MAXLEN_READ);

	if (stream->pb_unused)
	{
		memmove(pplayer->input_data, stream->pb_unused, stream->unusedsize
				* sizeof(unsigned short));
	}

	return need_len;
}
/*
 * Fill mp3dec internal buffer with mp3 data.
 * len : in bytes.
 */
jint Java_com_tommy_test_audiotest_AudioTest_mp3decFillData(JNIEnv* env,
		jobject thiz, jbyteArray buf, jint len)
{
	MP3_PLAYER *pplayer = &player;
	struct MP3DEC_STREAM *stream = &lstream;
	short *ptr = pplayer->input_data + stream->unusedsize;
	//    int len=env->GetArrayLength(buf);
	// 	  jint elems[10];
	//	 (*env)->GetIntArrayRegion(env, buf, 0, len, elems);   //a2[]
	jbyte *elems = (*env)->GetByteArrayElements(env, buf, NULL);

	// Copy Data from elems to ptr.
	memcpy(ptr, elems, len);
	D("mp3decFillData fill %d bytes!\n", len);

	// info core the buff pointer with new data available.
	stream->pb_stream = pplayer->input_data;
	pplayer->input_length = stream->unusedsize + len / 2;
	stream->streamsize = pplayer->input_length;

	//	ReferenceTable overflow (max=1024)
	(*env)->ReleaseByteArrayElements(env, buf, elems, 0);
	return 0;

}

/*
 * Run mp3 decoder.
 */
jint Java_com_tommy_test_audiotest_AudioTest_mp3decRun(JNIEnv* env,
		jobject thiz)
{

	lpcm.pOutBuffer = player.output_data;
	lpcm.OutBufferSize = OUTPUT_BUFSZ;

	result = mp3decoder_run(decoder, &lstream, &lpcm);
	if (result != MP3D_STATUS_SUCCESS)
	{
		error_time++;
		D("\nmp3decoder_run result is %d, total is %d !\n", result, error_time);
		return 1;
	}
	D("\nmp3decoder_run OK !");

	return 0;
}

/*
 * Get PCM output len in bytes.
 * return value:
 * size : pcm output size in 8-bit byte.
 */
jint Java_com_tommy_test_audiotest_AudioTest_mp3decGetOutputPcmLen(JNIEnv* env,
		jobject thiz)
{
	struct MP3DEC_PCM *pcm = &lpcm;
	//	decode_output(&player, &lpcm);
	//    len = fwrite(pcm->pOutBuffer, 1, pcm->length * pcm->channels * 2, player->output_fd);
	return (pcm->length * pcm->channels * 2);
}

/*
 * Get PCM output.
 * size : pcm output size in 8-bit byte.
 */
jbyteArray Java_com_tommy_test_audiotest_AudioTest_mp3decGetOutputPcmBuff(
		JNIEnv* env, jobject thiz, jbyteArray buf)
{
	struct MP3DEC_PCM *pcm = &lpcm;
#if 0
	// Copy mp3dec internal output buffer to Android app's buffer.
	jbyte *elems = (*env)->GetByteArrayElements(env, buf, NULL);

	memcpy(elems, pcm->pOutBuffer, pcm->length * pcm->channels * 2);

	//	ReferenceTable overflow (max=1024)
	(*env)->ReleaseByteArrayElements(env, buf, elems, 0);
	return buf;
#else
	// 锟斤拷jni锟斤拷直锟斤拷new一锟斤拷byte锟斤拷锟介，然锟斤拷锟斤拷煤锟斤拷锟�*env)->SetByteArrayRegion(env, bytearray, 0, len, buffer);锟斤拷buffer锟斤拷值copy锟斤拷bytearray锟叫ｏ拷锟斤拷锟斤拷直锟斤拷return bytearray锟酵匡拷锟斤拷锟斤拷
	jbyte *outbuf = (jbyte*)pcm->pOutBuffer;
	int nOutSize = pcm->length * pcm->channels * 2;
	jbyteArray jarray = (*env)->NewByteArray(env, nOutSize);
	(*env)->SetByteArrayRegion(env, jarray, 0, nOutSize, outbuf);
	return jarray;
#endif
}
#endif
