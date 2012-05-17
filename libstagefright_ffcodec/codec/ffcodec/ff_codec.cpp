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
 */

#include "FF_Codec.h"
#define LOG_NDEBUG 0
#define LOG_TAG "FF_Codec"

#define __UINT64_C(c)     c ## ULL
#define UINT64_C(c)       __UINT64_C(c)

#include <utils/Log.h> 
#define  I(x...)  LOGI(x)
#define  D(x...)  LOGD(x)

#ifdef __cplusplus
extern "C"
{
#endif
/* start of ffmpeg */
#define INT64_C	int64_t

#include "libavutil/avstring.h"
#include "libavutil/mathematics.h"
#include "libavutil/pixdesc.h"
#include "libavutil/imgutils.h"
#include "libavutil/dict.h"
#include "libavutil/parseutils.h"
#include "libavutil/samplefmt.h"
#include "libavutil/avassert.h"
#include "libavformat/avformat.h"
#include "libavutil/opt.h"
#include "libavcodec/avfft.h"
#include "libswresample/swresample.h" 
/* end of ffmpeg */
//#include "libavutil/colorspace.h"
//#include "libavdevice/avdevice.h"
//#include "libswscale/swscale.h"
//#include "libavcodec/audioconvert.h"
#ifdef __cplusplus
}
#endif

#include <media/stagefright/MediaBufferGroup.h>
#include <media/stagefright/MediaDebug.h>
#include <media/stagefright/MediaDefs.h>
#include <media/stagefright/MetaData.h>
#include <media/stagefright/Utils.h>

namespace android
{


/*	TOMMY ADD	*/
//#define INBUF_SIZE 4096
#define AUDIO_INBUF_SIZE (1024*32)
#define AUDIO_REFILL_THRESH 4096

static AVCodec *codec;
static AVCodecContext *ac = NULL;
static int len, ending;
static AVPacket avpkt;
static AVFrame *decoded_frame = NULL;
static bool alloc_ac = false;

static unsigned long absolute_framecount = 0;
static long sample_rate;
static int layer;
static long bitrate;
static int mpegversion;

static CodecID codec_id;

extern "C" void mylog_ffcodec(char *fmt)
{
	//LOGI("mylog");
	__android_log_print(ANDROID_LOG_INFO, "ffcodec log", "%s", fmt);
}

FF_CODEC::FF_CODEC(const sp<MediaSource> &source) :
		mSource(source), mNumChannels(0), mStarted(false), mBufferGroup(NULL), mConfig(NULL), //new tPVMP3DecoderExternal),
		mDecoderBuf(NULL), mAnchorTimeUs(0), mNumFramesOutput(0), mInputBuffer(NULL), mFixedHeader(0)
{
	init();
	LOGV(" FF_CODEC() ");
}

void FF_CODEC::init()
{
	sp<MetaData> srcFormat = mSource->getFormat();

	int32_t sampleRate;

	CHECK(srcFormat->findInt32(kKeyChannelCount, &mNumChannels));
	CHECK(srcFormat->findInt32(kKeySampleRate, &sampleRate));
	CHECK(srcFormat->findInt32(kKeyColorFormat, (int32_t*)&codec_id));
	CHECK(srcFormat->findPointer(kKeyWidth, (void**)&ac));

	mMeta = new MetaData;
	mMeta->setCString(kKeyMIMEType, MEDIA_MIMETYPE_AUDIO_RAW);
	mMeta->setInt32(kKeyChannelCount, mNumChannels);
	mMeta->setInt32(kKeySampleRate, sampleRate);

	int64_t durationUs;
	if (srcFormat->findInt64(kKeyDuration, &durationUs))
	{
		mMeta->setInt64(kKeyDuration, durationUs);
	}

	mMeta->setCString(kKeyDecoderComponent, "FF_CODEC");

#if 0
	LOGD("FFplayInit called ! ");

	I("\n**************************FF_CODEC*******************************\n");
	I( "*  FFplayer based on libffmpeg, build time: %s %s \n", __DATE__, __TIME__);
#ifdef OPT_TOMMY_NEON
	I("***************  TOMMY OPTIMIZED USING NEON  ********************\n");
#endif
	I("avcodec version %d\n", avutil_version());
	I("avcodec version %d\n", avcodec_version());
	I("test using prelink.");
	I("avformat version %d\n", avformat_version());
	I("*****************************************************************\n");

	avcodec_register_all();
	av_register_all();

	LOGD("FFplayInit done !");
#endif
}

FF_CODEC::~FF_CODEC()
{
	if (mStarted)
	{
		stop();
	}

	//delete mConfig;
	mConfig = NULL;
	LOGV(" ~FF_CODEC()");

}

status_t FF_CODEC::start(MetaData *params)
{
	CHECK(!mStarted);

	mBufferGroup = new MediaBufferGroup;
	//Tommy: alloc enough output space. as wma will output much than mp3.
	mBufferGroup->add_buffer(new MediaBuffer(48000 * 2 * 2));

	mSource->start();

	mAnchorTimeUs = 0;
	mNumFramesOutput = 0;
	mStarted = true;

#if 1
	av_init_packet(&avpkt);

	/* find the mpeg audio decoder */
	codec = avcodec_find_decoder(codec_id);		//(CODEC_ID_MP3);
	if (!codec)
	{
		LOGE( "codec not found\n");
		return UNKNOWN_ERROR;
	}

	alloc_ac = false;
	if(ac == NULL)
	{
		LOGD("avcodec_alloc_context3. ");
		ac = avcodec_alloc_context3(codec);
		alloc_ac = true;
	}

	/* open it */
	if (avcodec_open2(ac, codec, 0) < 0)
	{
		LOGE( "could not open codec\n");
		return UNKNOWN_ERROR;
	}
	ending = false;

#endif

	LOGV(" FF_CODEC::start() done");

	return OK;
}

status_t FF_CODEC::stop()
{
	CHECK(mStarted);

	if (mInputBuffer)
	{
		mInputBuffer->release();
		mInputBuffer = NULL;
	}

	if (mDecoderBuf)
	{
		free(mDecoderBuf);
		mDecoderBuf = NULL;
	}

	delete mBufferGroup;
	mBufferGroup = NULL;

#if 1
	avcodec_close(ac);
	if(alloc_ac)
		av_free(ac);
	alloc_ac = false;

	if (decoded_frame)
		av_free(decoded_frame);
	decoded_frame = NULL;
#endif

	mSource->stop();

	mStarted = false;

	LOGV(" FF_CODEC::stop()");
	return OK;
}

sp<MetaData> FF_CODEC::getFormat()
{
	LOGV(" FF_CODEC::getFormat()");
	return mMeta;
}

status_t FF_CODEC::read(MediaBuffer **out, const ReadOptions *options)
{
	status_t err;
	MediaBuffer *buffer = NULL;
	int64_t timeUs;
	bool seekSource = false;

	int got_audio_frame = 0;
	int offset;
	MediaBuffer *mbtmp;
	int nb_samples = 0;

	*out = NULL;

	int64_t seekTimeUs;
	ReadOptions::SeekMode mode;
	if (options && options->getSeekTo(&seekTimeUs, &mode))
	{
		CHECK(seekTimeUs >= 0);

		mNumFramesOutput = 0;
		seekSource = true;

		if (mInputBuffer)
		{
			mInputBuffer->release();
			mInputBuffer = NULL;
		}

		avcodec_flush_buffers(ac);
	}
	else
	{
		seekTimeUs = -1;
	}

	// SEEK.
	if (seekSource && mInputBuffer == NULL)
	{
		err = mSource->read(&mInputBuffer, options);

		if (err != OK)
		{
			ending = true;
		}

		if ((mFixedHeader == 0) && (mInputBuffer->range_length() > 4))
		{
			//save the first 4 bytes as fixed header for the reset of the file
			mFixedHeader = U32_AT((uint8_t *) mInputBuffer->data());
		}

		if (seekSource == true)
		{
//			off_t syncOffset = 0;
//			bool valid = resync((uint8_t *) mInputBuffer->data() + mInputBuffer->range_offset(),
//					mInputBuffer->range_length(), mFixedHeader, &syncOffset);
//			if (valid)
//			{
//				// consume these bytes, we might find a frame header in next buffer
//				mInputBuffer->set_range(mInputBuffer->range_offset() + syncOffset,
//						mInputBuffer->range_length() - syncOffset);
//				LOGV("FFcodec found a sync point after seek syncOffset %d", (int)syncOffset);
//			}
//			else
//			{
//				LOGV("NO SYNC POINT found, buffer length %d", mInputBuffer->range_length());
//			}
		}

		int64_t timeUs;
		if (mInputBuffer->meta_data()->findInt64(kKeyTime, &timeUs))
		{
			mAnchorTimeUs = timeUs;
			mNumFramesOutput = 0;
		}
		else
		{
			// We must have a new timestamp after seeking.
			CHECK(seekTimeUs < 0);
		}
	}

	LOGV("read().");

	if (mInputBuffer == NULL)
	{
		err = mSource->read(&mInputBuffer, NULL);

		if (err != OK)
		{
			if (ending != true)
				ending = true;
			else
				return err;
		}
	}

	// If input buffer length < thresh, try to fill it.
	if (mInputBuffer && mInputBuffer->range_length() < AUDIO_REFILL_THRESH)
	{
		err = OK;
		while (mInputBuffer->range_length() < (mInputBuffer->size() / 2) && err == OK)
		{
			err = mSource->read(&mbtmp, NULL);
			if (err != OK)
			{
				ending = true;
			}
			else
			{
				memcpy((uint8_t *) mInputBuffer->data() + mInputBuffer->range_offset() + mInputBuffer->range_length(),
						(uint8_t *) mbtmp->data() + mbtmp->range_offset(), mbtmp->range_length());
				mInputBuffer->set_range(mInputBuffer->range_offset(),
						mInputBuffer->range_length() + mbtmp->range_length());
				mbtmp->release();
			}
		}
	}

	// below fix one bug, which cause ftptest.wma crash at tail.
	if (mInputBuffer == NULL && ending == true)
	{
		*out = NULL;
		return ERROR_END_OF_STREAM;
	}

	avpkt.data = (uint8_t*) mInputBuffer->data() + mInputBuffer->range_offset();
	avpkt.size = mInputBuffer->range_length();
	CHECK_EQ(mBufferGroup->acquire_buffer(&buffer), OK);
	buffer->set_range(0, 0);

	LOGV("ready to decode. avpkt.size  %d bytes (input).\n", avpkt.size);
	LOGV("ready to decode. buffer size  %d bytes (output).\n", buffer->size());
	while (got_audio_frame == 0 && avpkt.size > 0)
	{
		if (!decoded_frame)
		{
			if (!(decoded_frame = avcodec_alloc_frame()))
			{
				LOGE("out of memory\n");
				buffer->release();
				*out = NULL;
				return UNKNOWN_ERROR;
			}
		}
		else
		{
			avcodec_get_frame_defaults(decoded_frame);
		}

		// len is the used bytes from the input stream.
		len = avcodec_decode_audio4(ac, decoded_frame, &got_audio_frame, &avpkt);
		if (len < 0)
		{
			LOGE("avpkt.size  %d bytes left.\n", avpkt.size);
			LOGE( "Error while decoding\n");
			if (ending == true)
			{
				avpkt.size = 0;
				buffer->release();
				*out = NULL;
				return ERROR_END_OF_STREAM;
			}
			avpkt.size = 0;
		}
		else
		{
			if (got_audio_frame)
			{
				LOGV("^, ch:%d, samples:%d, fmt:%d\n", ac->channels, decoded_frame->nb_samples, ac->sample_fmt);
				/* if a frame has been decoded, output it */
				int data_size = av_samples_get_buffer_size(NULL, ac->channels, decoded_frame->nb_samples, ac->sample_fmt,
						1);
				LOGV("%d bytes of input consumed, output %d bytes .", len, data_size);
				//fwrite(decoded_frame->data[0], 1, data_size, outfile);
				memcpy((uint8_t*) buffer->data() + buffer->range_length(), decoded_frame->data[0], data_size);
				buffer->set_range(0, buffer->range_length() + data_size);
				sample_rate = ac->sample_rate;
				nb_samples += decoded_frame->nb_samples;
			}
			avpkt.size -= len;
			avpkt.data += len;
			avpkt.dts = avpkt.pts = AV_NOPTS_VALUE;
		}
//		LOGV("avpkt.size  %d bytes left.\n", avpkt.size);
	}

	LOGV("decode done. avpkt.size  %d bytes left.\n", avpkt.size);

	// move unused data to header of mInputBuffer.
	memmove((uint8_t*) mInputBuffer->data(), (uint8_t*) avpkt.data, avpkt.size);
	mInputBuffer->set_range(0, avpkt.size);

	if (mInputBuffer->range_length() == 0)
	{
		mInputBuffer->release();
		mInputBuffer = NULL;
	}

	buffer->meta_data()->setInt64(kKeyTime, mAnchorTimeUs + (mNumFramesOutput * 1000000) / sample_rate);
	mNumFramesOutput += nb_samples;

	LOGV("read() done.");
	*out = buffer;
	return OK;

}

} // namespace android
