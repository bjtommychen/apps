/*
 * Copyright (C) 2009 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
#include <string.h>
#include <jni.h>

#define DEBUG 1

#if DEBUG
#include <android/log.h>
#  define  D(x...)  __android_log_print(ANDROID_LOG_DEBUG,"audiotest",x)
#else
#  define  D(...)  do {} while (0)
#endif

/* This is a trivial JNI example where we use a native method
 * to return a new VM String. See the corresponding Java source
 * file located at:
 *
 *   apps/samples/hello-jni/project/src/com/example/HelloJni/HelloJni.java
 */
jstring Java_com_tommy_test_audiotest_AudioTest_stringFromJNI(JNIEnv* env,
		jobject thiz)
{
	D("Java_com_tommy_test_audiotest_AudioTest_stringFromJNI called !");
	return (*env)->NewStringUTF(env, "Hello from JNI 222, AudioTest !");
}

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
 */

#include "libmp3dec.h"

/*******************************************************************************\
*  <Typedefs>
 \*******************************************************************************/
#define INPUT_BUFSZ				(MPEG_BUFSZ)	//could be larger
#define OUTPUT_BUFSZ			(1152*2) 		// 1152*2 for frame, 1152 for granule.
#define MP3DEC_BUFSZ			(9500)
#define MAXLEN_READ             INPUT_BUFSZ
#define MIN(a,b)				((a) < (b) ? (a) : (b))

enum player_channel
{
	PLAYER_CHANNEL_DEFAULT = 0,
	PLAYER_CHANNEL_LEFT = 1,
	PLAYER_CHANNEL_RIGHT = 2,
	PLAYER_CHANNEL_MONO = 3,
	PLAYER_CHANNEL_STEREO = 4
};

typedef struct
{
	//input
//	char const *input_path;
	//    FILE* input_fd;
	unsigned short *input_data;
	unsigned long input_length;

	int input_eof;

	//output
	unsigned int channels_in;
	unsigned int channels_out;
	enum player_channel output_select;
//	char const *output_path;
	//    FILE* output_fd;
	int output_speed;
	unsigned short *output_data;

	struct stats
	{
		unsigned long global_framecount;
		unsigned long absolute_framecount;
		unsigned long play_framecount;
	} stats;
} MP3_PLAYER;

/*******************************************************************************\
*  <Global Variables>
 \*******************************************************************************/

/*******************************************************************************\
*  <Local Variables>
 \*******************************************************************************/
static long data_len;
static long sample_rate;
static int layer;
static long bitrate;
static int mpegversion;

static MP3_PLAYER player;
static HANDLE_MP3D decoder;
static enum MP3D_STATUS result;

static struct MP3DEC_INITCFG initcfg;
static struct MP3DEC_PCM lpcm;
static struct MP3DEC_STREAM lstream;
static int error_time = 0;
static int sync_done = 0;

/*
 * Function Name:     decode_header
 * Description:          decoder lib uses this function to inform application the header info of mp3 stream
 * Input:                   data: context of the callback function
 *                             header: pointer to the header info
 * Output:                 MP3D_MSG_STOP: stop decoding for whole stream
 *                             MP3D_MSG_BREAK: stop decoding current frame
 *                             MP3D_MSG_IGNORE: skip current frame
 *                             MP3D_MSG_CONTINUE: decoding current frame normally
 * Dependency:
 */
static enum MP3D_MSG decode_header(void *data,
		struct MP3DEC_HEADER const *header)
{
	MP3_PLAYER *player = data;
	static int bVBRtagPrinted = 0;

	layer = header->layer;
	bitrate = header->bitrate;
	sample_rate = header->samplerate;
	mpegversion = header->mpegversion;

	if (player->stats.absolute_framecount)
	{
		// printf("%d ", player->stats.absolute_framecount);
		++player->stats.absolute_framecount;
		++player->stats.global_framecount;
	}

	return MP3D_MSG_CONTINUE;
}

/*
 * Init
 */
jint Java_com_tommy_test_audiotest_AudioTest_mp3decInit(JNIEnv* env,
		jobject thiz)
{
	D("mp3dec_init called ! ");

	D("\n**************************android******************************\n");
	D("*  MP3 Decoder application, build time: %s %s \n", __DATE__, __TIME__);
#ifdef OPT_TOMMY_NEON
	D("***************  TOMMY OPTIMIZED USING NEON  ********************\n");
#endif
	D("*****************************************************************\n");

	player.input_data = (unsigned short *) malloc(INPUT_BUFSZ
			* sizeof(unsigned short));
	if (player.input_data == 0)
	{
		return 0;
	}

	player.input_length = 0;
	player.input_eof = 0;

	player.output_data = (unsigned short *) malloc(OUTPUT_BUFSZ
			* sizeof(unsigned short));
	if (player.output_data == 0)
	{
		free(player.input_data);
		return 0;
	}

	initcfg.CoreMemPoolSize = MP3DEC_BUFSZ;
	initcfg.pCoreMemPool = malloc(initcfg.CoreMemPoolSize * sizeof(short));
	if (initcfg.pCoreMemPool == 0)
	{
		D("initcfg.pCoreMemPool malloc return 0!\n");
		//      goto errout1;
	}

	decoder = mp3decoder_init(&player, decode_header, &initcfg);
	if (decoder == 0)
	{
		D("mp3decoder_init return 0!\n");
	}

	lstream.unusedsize = 0;

	D("mp3dec_init done !");
	return 1;
}

/*
 * Exit
 */
jint Java_com_tommy_test_audiotest_AudioTest_mp3decExit(JNIEnv* env,
		jobject thiz)
{
	mp3decoder_finish(decoder);
	free(initcfg.pCoreMemPool);
	free(player.input_data);
	free(player.output_data);

	return 0;
}

/*
 * Get 16-bit short len to read from mp3 files.
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

	// Copy Data
	memcpy(ptr, elems, len);
	D("mp3decFillData fill %d bytes!\n", len);

	// info core the buff pointer with new data available.
	stream->pb_stream = pplayer->input_data;
	pplayer->input_length = stream->unusedsize + len / 2;
	stream->streamsize = pplayer->input_length;
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
	jbyte *elems = (*env)->GetByteArrayElements(env, buf, NULL);

	memcpy(elems, pcm->pOutBuffer, pcm->length * pcm->channels * 2);

	return buf;
}

