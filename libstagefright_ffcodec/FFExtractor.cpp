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
#define LOG_TAG "FFExtractor"
#include <utils/Log.h>
#define  I(x...)  LOGI(x)
#define  D(x...)  LOGD(x)

#define __UINT64_C(c)     c ## ULL
#define UINT64_C(c)       __UINT64_C(c)

#include "include/FFExtractor.h"

#include "include/ID3.h"

#include <media/stagefright/foundation/AMessage.h>
#include <media/stagefright/DataSource.h>
#include <media/stagefright/MediaBuffer.h>
#include <media/stagefright/MediaBufferGroup.h>
#include <media/stagefright/MediaDebug.h>
#include <media/stagefright/MediaDefs.h>
#include <media/stagefright/MediaErrors.h>
#include <media/stagefright/MediaSource.h>
#include <media/stagefright/MetaData.h>
#include <media/stagefright/Utils.h>
#include <utils/String8.h>

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
//#include "libavcodec/avfft.h"
//#include "libswresample/swresample.h" 
/* end of ffmpeg */
//#include "libavutil/colorspace.h"
//#include "libavdevice/avdevice.h"
//#include "libswscale/swscale.h"
//#include "libavcodec/audioconvert.h"
#ifdef __cplusplus
}
#endif

namespace android
{

// ffmpeg avformat.
static AVFormatContext *c = NULL;
static AVPacket avpkt;
static int audioidx, videoidx;
static int sample_rate;
static int num_channels;
static int bitrate; // in Kbps.
static String8 mimetype;

static CodecID codec_id;
//static AVCodec *acodec;
static AVCodecContext *ac = NULL;
static AVFrame *aframe = NULL;

class FFSource: public MediaSource
{
public:
	FFSource(const sp<MetaData> &meta, const sp<DataSource> &source, off_t first_frame_pos, uint32_t fixed_header,
			int32_t byte_number, const char *table_of_contents);

	virtual status_t start(MetaData *params = NULL);
	virtual status_t stop();

	virtual sp<MetaData> getFormat();

	virtual status_t read(MediaBuffer **buffer, const ReadOptions *options = NULL);

protected:
	virtual ~FFSource();

private:
	sp<MetaData> mMeta;
	sp<DataSource> mDataSource;
	off_t mFirstFramePos;
	uint32_t mFixedHeader;
	off_t mCurrentPos;
	int64_t mCurrentTimeUs;
	bool mStarted;
	int32_t mByteNumber; // total number of bytes in this FF
	MediaBufferGroup *mGroup;

	FFSource(const FFSource &);
	FFSource &operator=(const FFSource &);
};

FFExtractor::FFExtractor(const sp<DataSource> &source, const sp<AMessage> &meta) :
		mInitCheck(NO_INIT), mDataSource(source), mFirstFramePos(-1), mFixedHeader(0), mByteNumber(0)
{
	off_t pos = 0;
	uint32_t header;
	bool success;

	size_t frame_size;

	mMeta = new MetaData;

	mMeta->setCString(kKeyMIMEType, mimetype);// MEDIA_MIMETYPE_AUDIO_MPEG);
	mMeta->setInt32(kKeySampleRate, sample_rate);
	mMeta->setInt32(kKeyBitRate, bitrate * 1000);
	mMeta->setInt32(kKeyChannelCount, num_channels);
	mMeta->setInt32(kKeyColorFormat, codec_id);
	mMeta->setPointer(kKeyWidth, (void*)ac);


	mFirstFramePos = 0;
	int64_t duration = 0;
	if (duration > 0)
	{
		mMeta->setInt64(kKeyDuration, duration);
	}
	else
	{
		off_t fileSize;
		if (mDataSource->getSize(&fileSize) == OK)
		{
			mMeta->setInt64(kKeyDuration, 8000LL * (fileSize - mFirstFramePos) / bitrate);
		}
	}

	mInitCheck = OK;
	LOGV("FFExtractor() done.");
}

size_t FFExtractor::countTracks()
{
	return mInitCheck != OK ? 0 : 1;
}

sp<MediaSource> FFExtractor::getTrack(size_t index)
{
	if (mInitCheck != OK || index != 0)
	{
		return NULL;
	}
	LOGV("getTrack() new FFSource done.");
	return new FFSource(mMeta, mDataSource, mFirstFramePos, mFixedHeader, mByteNumber, NULL);
}

sp<MetaData> FFExtractor::getTrackMetaData(size_t index, uint32_t flags)
{
	if (mInitCheck != OK || index != 0)
	{
		return NULL;
	}

	return mMeta;
}

//////////////////////////////////FFSource//////////////////////////////////////////////

FFSource::FFSource(const sp<MetaData> &meta, const sp<DataSource> &source, off_t first_frame_pos, uint32_t fixed_header,
		int32_t byte_number, const char *table_of_contents) :
		mMeta(meta), mDataSource(source), mFirstFramePos(first_frame_pos), mFixedHeader(fixed_header), mCurrentPos(0), mCurrentTimeUs(
				0), mStarted(false), mByteNumber(byte_number), mGroup(NULL)
{
	//memcpy (mTableOfContents, table_of_contents, sizeof(mTableOfContents));
}

FFSource::~FFSource()
{
	if (mStarted)
	{
		stop();
	}
}

status_t FFSource::start(MetaData *)
{
	CHECK(!mStarted);

	mGroup = new MediaBufferGroup;

	const size_t kMaxFrameSize = 32768;
	mGroup->add_buffer(new MediaBuffer(kMaxFrameSize));

	mGroup->add_buffer(new MediaBuffer(kMaxFrameSize));
	LOGV("start(), Tommy do ONE more new MediaBuffer %d bytes. for ffcodec", kMaxFrameSize);

	mCurrentPos = mFirstFramePos;
	mCurrentTimeUs = 0;

#if 1
//	/* find the mpeg audio decoder */
//	acodec = avcodec_find_decoder(ac->codec_id);
//	if (!acodec)
//	{
//		LOGE("acodec not found .");
//	}
//	/* open it */
//	if (avcodec_open2(ac, acodec, 0) < 0)
//	{
//		LOGE("could not open acodec\n");
//	}

	aframe = avcodec_alloc_frame();

#endif

	mStarted = true;

	return OK;
}

status_t FFSource::stop()
{
	CHECK(mStarted);

	delete mGroup;
	mGroup = NULL;

#if 1
	av_free(aframe);
	if(c)
		avformat_free_context(c);
	c = NULL;
#endif
	mStarted = false;

	return OK;
}

sp<MetaData> FFSource::getFormat()
{
	return mMeta;
}

status_t FFSource::read(MediaBuffer **out, const ReadOptions *options)
{
	*out = NULL;

#if 1	//Seek
	int64_t seekTimeUs;
	ReadOptions::SeekMode mode;
	if (options != NULL && options->getSeekTo(&seekTimeUs, &mode))
	{
		int32_t bitrate;
		if (!mMeta->findInt32(kKeyBitRate, &bitrate))
		{
			// bitrate is in bits/sec.
			LOGI("no bitrate");

			return ERROR_UNSUPPORTED;
		}

		mCurrentTimeUs = seekTimeUs;
		// interpolate in TOC to get file seek point in bytes
		int64_t duration;
		{
//			LOGD("seekTimeUs %ld.", seekTimeUs);
			mCurrentPos = mFirstFramePos + seekTimeUs * bitrate / 8000000;
			av_seek_frame(c, -1, seekTimeUs, AVSEEK_FLAG_BACKWARD);
		}
	}
#endif
	int frame_size;

	MediaBuffer *buffer;
	status_t err = mGroup->acquire_buffer(&buffer);
	if (err != OK)
	{
		return err;
	}

	memset(&avpkt, 0, sizeof(avpkt));
	while (av_read_frame(c, &avpkt) == 0)
	{
		if (avpkt.stream_index == audioidx)
			break;

		LOGV("skip frame idx.%d", avpkt.stream_index);
	}

//	ssize_t n = mDataSource->readAt(mCurrentPos, buffer->data(), frame_size);
//	if (n < (ssize_t) frame_size)
	if (avpkt.size == 0)
	{
		buffer->release();
		buffer = NULL;

		return ERROR_END_OF_STREAM;
	}

	frame_size = avpkt.size;
	memcpy(buffer->data(), avpkt.data, frame_size);
	buffer->set_range(0, frame_size);
	LOGV("FFSource::read %d bytes. ", frame_size);

	buffer->meta_data()->setInt64(kKeyTime, mCurrentTimeUs);
	buffer->meta_data()->setInt32(kKeyIsSyncFrame, 1);

	mCurrentPos += frame_size;
	mCurrentTimeUs += frame_size * 8000ll / bitrate;

	*out = buffer;

	return OK;
}

sp<MetaData> FFExtractor::getMetaData()
{
	sp<MetaData> meta = new MetaData;

	if (mInitCheck != OK)
	{
		return meta;
	}

	switch (codec_id)
	{
	case CODEC_ID_WMAV1:
	case CODEC_ID_WMAV2:
	case CODEC_ID_WMAPRO:
		meta->setCString(kKeyMIMEType, "audio/x-ms-wma");
		break;
	case CODEC_ID_MP1:
	case CODEC_ID_MP2:
	case CODEC_ID_MP3:
		meta->setCString(kKeyMIMEType, "audio/mpeg");
		break;
	default:
		break;
	}
	return meta;

}

bool SniffFF(const sp<DataSource> &source, String8 *mimeType, float *confidence, sp<AMessage> *)
{
//	off_t pos = 0;
//	uint32_t header;
	char buf[256];

	LOGV("enter SniffFF. ");
//	return false;

	I("\n**************************SniffFF*******************************\n");
	I( "*  FFplayer based on libffmpeg, build time: %s %s \n", __DATE__, __TIME__);
#ifdef OPT_TOMMY_NEON
	I("***************  TOMMY OPTIMIZED USING NEON  ********************\n");
#endif
	I("avcodec version %d\n", avutil_version());
	I("avcodec version %d\n", avcodec_version());
	I("avformat version %d\n", avformat_version());
	I("*****************************************************************\n");

	avcodec_register_all();
	av_register_all();

	LOGD("libffmpeg Init done !");

	LOGV("AVFORMAT filename is %s.", source->uri_file_tommy);

	if (source->uri_file_tommy == NULL)
	{
		LOGV("leave SniffFF. filename NULL!");
		return false;
	}

	audioidx = -1;
	c = avformat_alloc_context();
	if (avformat_open_input(&c, source->uri_file_tommy, NULL, 0) < 0)
	{
		LOGE("could not open file\n");
		return false;
	}
	c->flags |= AVFMT_FLAG_GENPTS;

	if (avformat_find_stream_info(c, 0) < 0)
	{
		LOGE("find stream failed. \n");
		return false;
	}

	LOGV("nb_streams is %d\n", c->nb_streams);
	for (int i = 0; i < c->nb_streams; i++)
	{
		LOGV("\nStream #%d: ", i);
		switch (c->streams[i]->codec->codec_type)
		{
		case AVMEDIA_TYPE_VIDEO:
			videoidx = i;
			LOGV("Video.");
			break;
		case AVMEDIA_TYPE_AUDIO:
			audioidx = i;
			LOGV("Audio.");
			break;
		default:
			LOGV("OTHER AVMEDIA. ");
			break;
		}
		LOGV("codec_name:%s. id:%xH. tag:%xH", c->streams[i]->codec->codec_name, c->streams[i]->codec->codec_id,
				&(c->streams[i]->codec->codec_tag));
		avcodec_string(buf, sizeof(buf), c->streams[i]->codec, 1);
		LOGV(" %s", buf);
	}

	LOGV("\n");

	if (audioidx == -1)
	{
		LOGV("leave SniffFF. no audio idx found.");
		return false;
	}

	ac = c->streams[audioidx]->codec;
	codec_id = ac->codec_id;
	num_channels = ac->channels;
	sample_rate = ac->sample_rate;
	bitrate = ac->bit_rate / 1000;

//	LOGI("timebase %lf", av_q2d(ac->time_base));

	switch (codec_id)
	{
	case CODEC_ID_WMAV1:
	case CODEC_ID_WMAV2:
	case CODEC_ID_WMAPRO:
		*mimeType = MEDIA_MIMETYPE_AUDIO_WMA;
		*confidence = 0.73f;
		break;
	case CODEC_ID_MP1:
	case CODEC_ID_MP2:
	case CODEC_ID_MP3:
		*mimeType = MEDIA_MIMETYPE_AUDIO_MPEG;
		*confidence = 0.73f;
		break;
	default:
		*confidence = 0.0f;
		break;
	}

	mimetype = *mimeType;

	LOGV("*confidence is %.2f", *confidence);
	LOGV("leave SniffFF. ");

	return true;
}

} // namespace android
