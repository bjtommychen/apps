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

#define LOG_NDEBUG 0
#define LOG_TAG "FF_Codec"
#include <utils/Log.h>
#define  I(x...)  LOGI(x)
#define  D(x...)  LOGD(x)

#define __UINT64_C(c)     c ## ULL
#define UINT64_C(c)       __UINT64_C(c)

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

#include "FF_Codec.h"

#include <OMX_Component.h>

#include <media/stagefright/MediaBufferGroup.h>
#include <media/stagefright/MediaDebug.h>
#include <media/stagefright/MediaDefs.h>
#include <media/stagefright/MetaData.h>
#include <media/stagefright/Utils.h>

#include <utils/threads.h>

namespace android
{

/*	TOMMY ADD	*/
//#define AUDIO_INBUF_SIZE (1024*32)
#define READ_REFILL_THRESH 4096

static AVCodec *codec;
static AVCodecContext *ac = NULL, *vc = NULL;
static int len, ending;
static AVFrame *decoded_frame = NULL;
static bool alloc_ac = false, alloc_vc = false;
static CodecID codec_id[2]; //Video. Audio.
static AVPacket apkt, vpkt;

Mutex mLock;

extern "C" void mylog_ffcodec(char *fmt)
{
	//LOGI("mylog");
	__android_log_print(ANDROID_LOG_INFO, "ffcodec log", "%s", fmt);
}

FF_CODEC::FF_CODEC(const sp<MediaSource> &source) :
		mSource(source), mNumChannels(0), mStarted(false), mBufferGroup(NULL), mConfig(NULL), mDecoderBuf(NULL), mAnchorTimeUs(
				0), mNumFramesOutput(0), mInputBuffer(NULL), mFixedHeader(0), mNumSamplesOutput(0)
{
	init();
	LOGV("FF_CODEC() ");
}

void FF_CODEC::init()
{
	CHECK(!mStarted);
	const char *mime = NULL;
	sp<MetaData> meta = mSource->getFormat();
	CHECK(meta->findCString(kKeyMIMEType, &mime));

	LOGV("mime is %s", mime);

	mMeta = new MetaData;
	if (!strncasecmp(mime, "video/", 6))
	{ //Video
		isVideo = true;
		CHECK(mSource->getFormat()->findInt32(kKeyWidth, &mWidth));
		CHECK(mSource->getFormat()->findInt32(kKeyHeight, &mHeight));
		mMeta->setInt32(kKeyWidth, mWidth);
		mMeta->setInt32(kKeyHeight, mHeight);
		mMeta->setInt32(kKeyColorFormat, OMX_COLOR_FormatYUV420Planar);
		mMeta->setCString(kKeyMIMEType, MEDIA_MIMETYPE_VIDEO_RAW);
		CHECK(meta->findInt32(kKeyFFcodecid, (int32_t*) &codec_id[0]));
		CHECK(meta->findPointer(kKeyFFcodecctx, (void**) &vc));
	}
	else if (!strncasecmp(mime, "audio/", 6))
	{ //Audiocodec
		int32_t sampleRate;

		isVideo = false;
		CHECK(meta->findInt32(kKeyChannelCount, &mNumChannels));
		CHECK(meta->findInt32(kKeySampleRate, &sampleRate));
		CHECK(meta->findInt32(kKeyFFcodecid, (int32_t*) &codec_id[1]));
		CHECK(meta->findPointer(kKeyFFcodecctx, (void**) &ac));

		mMeta->setCString(kKeyMIMEType, MEDIA_MIMETYPE_AUDIO_RAW);
		mMeta->setInt32(kKeyChannelCount, mNumChannels);
		mMeta->setInt32(kKeySampleRate, sampleRate);

		int64_t durationUs;
		if (meta->findInt64(kKeyDuration, &durationUs))
		{
			mMeta->setInt64(kKeyDuration, durationUs);
		}
	}

	mMeta->setCString(kKeyDecoderComponent, "FF_CODEC");
}

FF_CODEC::~FF_CODEC()
{
	if (mStarted)
	{
		stop();
	}

	//delete mConfig;
	mConfig = NULL;
	LOGV("~FF_CODEC()");

}

void FF_CODEC::allocateFrames(int32_t width, int32_t height)
{
	size_t frameSize = (((width + 15) & -16) * ((height + 15) & -16) * 3) / 2;

	for (uint32_t i = 0; i < 2; ++i)
	{
		mFrames[i] = new MediaBuffer(frameSize);
		mFrames[i]->setObserver(this);
	}
}

void FF_CODEC::releaseFrames()
{
	for (size_t i = 0; i < sizeof(mFrames) / sizeof(mFrames[0]); ++i)
	{
		MediaBuffer *buffer = mFrames[i];

		buffer->setObserver(NULL);
		buffer->release();

		mFrames[i] = NULL;
	}
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

	/* find the mpeg audio decoder */
	codec = avcodec_find_decoder(codec_id[isVideo ? 0 : 1]);
	if (!codec)
	{
		LOGE("codec not found\n");
		return UNKNOWN_ERROR;
	}

	if (isVideo)
	{
		av_init_packet(&vpkt);

		alloc_vc = false;
		if (vc == NULL)
		{
			LOGD("avcodec_alloc_context3. ");
			vc = avcodec_alloc_context3(codec);
			alloc_vc = true;
		}

		/* open it */
		if (avcodec_open2(vc, codec, 0) < 0)
		{
			LOGE("could not open vcodec\n");
			return UNKNOWN_ERROR;
		}

		allocateFrames(mWidth, mHeight);
	}
	else
	{
		av_init_packet(&apkt);

		alloc_ac = false;
		if (ac == NULL)
		{
			LOGD("avcodec_alloc_context3. ");
			ac = avcodec_alloc_context3(codec);
			alloc_ac = true;
		}

		/* open it */
		if (avcodec_open2(ac, codec, 0) < 0)
		{
			LOGE("could not open acodec\n");
			return UNKNOWN_ERROR;
		}
	}

	decoded_frame = avcodec_alloc_frame();
	avframe = (void*) decoded_frame;

	ending = false;

#endif

	LOGV("FF_CODEC::start() done");

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

	mSource->stop();

	mStarted = false;

#if 1
	if (!isVideo)
	{
		avcodec_close(ac);
		if (alloc_ac)
			av_free(ac);
		ac = NULL;
		alloc_ac = false;
	}
	else if (isVideo)
	{
		avcodec_close(vc);
		if (alloc_vc)
			av_free(vc);
		vc = NULL;
		alloc_vc = false;
		releaseFrames();
	}

	decoded_frame = (AVFrame*) avframe;
	if (decoded_frame)
		av_free(decoded_frame);
	decoded_frame = NULL;

#endif

	LOGV(" FF_CODEC::stop()");
	return OK;
}

sp<MetaData> FF_CODEC::getFormat()
{
	LOGV(" FF_CODEC::getFormat()");
	return mMeta;
}

static void ff_CopyYuv(int width, int height, MediaBuffer *buff, AVFrame *frame)
{
	int i, j;
	uint8_t *dst, *src;

	src = frame->data[0];
	dst = (uint8_t*) buff->data();
	for (j = 0; j < height; j++)
	{
		memcpy(dst, src, width);
		src += frame->linesize[0];
		dst += width;
	}

	src = frame->data[1];
	for (j = 0; j < height / 2; j++)
	{
		memcpy(dst, src, width / 2);
		src += frame->linesize[1];
		dst += width / 2;
	}

	src = frame->data[2];
	for (j = 0; j < height / 2; j++)
	{
		memcpy(dst, src, width / 2);
		src += frame->linesize[2];
		dst += width / 2;
	}
	buff->set_range(0, buff->size());
}

status_t FF_CODEC::read(MediaBuffer **out, const ReadOptions *options)
{
	Mutex::Autolock autoLock(mLock);

	status_t err;
	MediaBuffer *buffer = NULL;
	int64_t timeUs;
	bool seekSource = false;

	int got_audio_frame = 0;
	int offset;
	MediaBuffer *mbtmp;
	int nb_samples = 0;

	LOGV("read().");

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

#if 0
	const char *extractor_name;
	CHECK(mSource->getFormat()->findCString(kKeyFFextractor, &extractor_name));

	LOGV("extractor_name is %s.", extractor_name);
	if (strcmp(extractor_name, "FFExtractor") != NULL)
	{
		// If input buffer length < thresh, try to fill it.
		if (mInputBuffer && mInputBuffer->range_length() < READ_REFILL_THRESH)
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
					memcpy(
							(uint8_t *) mInputBuffer->data() + mInputBuffer->range_offset()
							+ mInputBuffer->range_length(), (uint8_t *) mbtmp->data() + mbtmp->range_offset(),
							mbtmp->range_length());
					mInputBuffer->set_range(mInputBuffer->range_offset(),
							mInputBuffer->range_length() + mbtmp->range_length());
					mbtmp->release();
				}
			}
		}
	}
#endif
	// below fix one bug, which cause ftptest.wma crash at tail.
	if (mInputBuffer == NULL && ending == true)
	{
		*out = NULL;
		return ERROR_END_OF_STREAM;
	}

	if (!isVideo)
	{ //AUDIO
		LOGV("read().AUDIO");
		apkt.data = (uint8_t*) mInputBuffer->data() + mInputBuffer->range_offset();
		apkt.size = mInputBuffer->range_length();
		CHECK_EQ(mBufferGroup->acquire_buffer(&buffer), OK);
		buffer->set_range(0, 0);

		LOGV("ready to decode. avpkt.size  %d bytes (input).\n", apkt.size);
		LOGV("ready to decode. buffer size  %d bytes (output).\n", buffer->size());
		while (/*got_audio_frame == 0 &&*/apkt.size > 0 && buffer->range_length() < (buffer->size() * 9 / 10))
		{
			decoded_frame = (AVFrame*) avframe;
			avcodec_get_frame_defaults(decoded_frame);

			// len is the used bytes from the input stream.
			len = avcodec_decode_audio4(ac, decoded_frame, &got_audio_frame, &apkt);
			if (len < 0)
			{
				LOGE("avpkt.size  %d bytes left.\n", apkt.size);
				LOGE("Error while decoding\n");
				if (ending == true)
				{
					apkt.size = 0;
					buffer->release();
					*out = NULL;
					return ERROR_END_OF_STREAM;
				}
				apkt.size = 0;
			}
			else
			{
				if (got_audio_frame)
				{
					LOGV("^, ch:%d, samples:%d, fmt:%d\n", ac->channels, decoded_frame->nb_samples, ac->sample_fmt);
					/* if a frame has been decoded, output it */
					int data_size = av_samples_get_buffer_size(NULL, ac->channels, decoded_frame->nb_samples,
							ac->sample_fmt, 1);
					LOGV("%d bytes of input consumed, output %d bytes .", len, data_size);
					//fwrite(decoded_frame->data[0], 1, data_size, outfile);
					memcpy((uint8_t*) buffer->data() + buffer->range_length(), decoded_frame->data[0], data_size);
					buffer->set_range(0, buffer->range_length() + data_size);
					sample_rate = ac->sample_rate;
					nb_samples += decoded_frame->nb_samples;
				}
				apkt.size -= len;
				apkt.data += len;
				apkt.dts = apkt.pts = AV_NOPTS_VALUE;
			}
//		LOGV("avpkt.size  %d bytes left.\n", avpkt.size);
		}

		LOGV("decode done. avpkt.size  %d bytes left.\n", apkt.size);

		// move unused data to header of mInputBuffer.
		memmove((uint8_t*) mInputBuffer->data(), (uint8_t*) apkt.data, apkt.size);
		mInputBuffer->set_range(0, apkt.size);

		if (mInputBuffer->range_length() == 0)
		{
			mInputBuffer->release();
			mInputBuffer = NULL;
		}

		buffer->meta_data()->setInt64(kKeyTime, mAnchorTimeUs + (mNumFramesOutput * 1000000) / sample_rate);
		mNumFramesOutput += nb_samples;

		*out = buffer;
	}
	else
	{ //VIDEO
		LOGV("read().VIDEO");
		vpkt.data = (uint8_t*) mInputBuffer->data() + mInputBuffer->range_offset();
		vpkt.size = mInputBuffer->range_length();
		buffer = mFrames[mNumSamplesOutput & 0x01];
		buffer->set_range(0, 0);

		LOGV("ready to decode. avpkt.size  %d bytes (input).\n", vpkt.size);
		LOGV("ready to decode. buffer size  %d bytes (output).\n", buffer->size());
		while (vpkt.size > 0)
		{
			int got_picture;
			decoded_frame = (AVFrame*) avframe;

			// len is the used bytes from the input stream.
			len = avcodec_decode_video2(vc, decoded_frame, &got_picture, &vpkt);
			if (len < 0)
			{
				LOGE("avpkt.size  %d bytes left.\n", vpkt.size);
				LOGE("Error while decoding\n");
				if (ending == true)
				{
					vpkt.size = 0;
					buffer->release();
					*out = NULL;
					return ERROR_END_OF_STREAM;
				}
				vpkt.size = 0;
			}
			else
			{
				if (got_picture)
				{
					LOGV("got video frame! %d x %d. linesize %d,%d,%d", decoded_frame->width, decoded_frame->height,
							decoded_frame->linesize[0], decoded_frame->linesize[1], decoded_frame->linesize[2]);

					/* if a frame has been decoded, output it */
//					int data_size = decoded_frame->height * decoded_frame->linesize[0]; // * 3 / 2;
//					LOGV("%d bytes of input consumed, output %d bytes .", len, data_size);
//					memcpy((uint8_t*) buffer->data() + buffer->range_length(), decoded_frame->data[0], data_size);
//					buffer->set_range(0, buffer->range_length() + data_size);
					ff_CopyYuv(mWidth, mHeight, buffer, decoded_frame);

				}
				vpkt.size -= len;
				vpkt.data += len;
				vpkt.dts = vpkt.pts = AV_NOPTS_VALUE;
			}
//		LOGV("avpkt.size  %d bytes left.\n", avpkt.size);
		}

		LOGV("decode done. vpkt.size %d bytes left.\n", vpkt.size);

		// move unused data to header of mInputBuffer.
		memmove((uint8_t*) mInputBuffer->data(), (uint8_t*) vpkt.data, vpkt.size);
		mInputBuffer->set_range(0, vpkt.size);

		int64_t timeUs;
		CHECK(mInputBuffer->meta_data()->findInt64(kKeyTime, &timeUs));

		if (mInputBuffer->range_length() == 0)
		{
			mInputBuffer->release();
			mInputBuffer = NULL;
		}

		*out = buffer; //mFrames[mNumSamplesOutput & 0x01];
		(*out)->add_ref();
		(*out)->meta_data()->setInt64(kKeyTime, timeUs);
		++mNumSamplesOutput;
	}

	LOGV("read() done.");

	return OK;

}

void FF_CODEC::signalBufferReturned(MediaBuffer *buffer)
{
	LOGV("signalBufferReturned");
}

} // namespace android
