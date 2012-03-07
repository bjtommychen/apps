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
 char *str = GetStringUTFChars(env, jstring, 0);
 (env)->ReleaseStringUTFChars(env, jstring, str);

 http://www.360doc.com/content/10/1229/17/5116642_82372464.shtml

 */

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/
#define DEBUG 0

#if DEBUG
#  define  D(x...)  __android_log_print(ANDROID_LOG_DEBUG,"audiotest",x)
#else
#  define  D(...)  do {} while (0)
#endif

#if 1
#  define  I(x...)  __android_log_print(ANDROID_LOG_INFO,"audiotest",x)
#else
#  define  I(...)  do {} while (0)
#endif

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

/*
 * Init
 */
jint Java_com_tommy_ffplayer_FFplayActivity_FFplayInit(JNIEnv* env,
		jobject thiz)
{
	D("FFplayInit called ! ");

	I("\n**************************Android******************************\n");
	I("*  FFplayer based on libffmpeg, build time: %s %s \n", __DATE__, __TIME__);
#ifdef OPT_TOMMY_NEON
	I("***************  TOMMY OPTIMIZED USING NEON  ********************\n");
#endif
	I("*****************************************************************\n");

	avcodec_init();
	avcodec_register_all();
	av_register_all();

	D("FFplayInit done !");
	return 0;
}

/*
 * Exit
 */
jint Java_com_tommy_ffplayer_FFplayActivity_FFplayExit(JNIEnv* env,
		jobject thiz)
{
	return 0;
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
	// ��jni��ֱ��newһ��byte���飬Ȼ����ú���(*env)->SetByteArrayRegion(env, bytearray, 0, len, buffer);��buffer��ֵcopy��bytearray�У�����ֱ��return bytearray�Ϳ�����
	jbyte *outbuf = (jbyte*)pcm->pOutBuffer;
	int nOutSize = pcm->length * pcm->channels * 2;
	jbyteArray jarray = (*env)->NewByteArray(env, nOutSize);
	(*env)->SetByteArrayRegion(env, jarray, 0, nOutSize, outbuf);
	return jarray;
#endif
}
#endif
