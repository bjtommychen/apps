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

//#define VIDEO_ONLY
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
static AVFormatContext *fc = NULL;
static AVPacket apkt, vpkt;
static int audioidx, videoidx;
static bool hasVideo, hasAudio;
//static int sample_rate;
//static int num_channels;
static int bitrateA, bitrateV; // in Kbps.

static String8 mimetypeA, mimetypeV;

//static CodecID codec_id;
//static AVCodec *acodec;
static AVCodecContext *ac = NULL, *vc = NULL;
//static AVFrame *aframe = NULL;

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

	bool hasVideo;
	bool hasAudio;

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

	bitrateA = bitrateV = 0;

	if (hasAudio)
	{
		mTrackA = new Track;
		mTrackA->meta = new MetaData;

		bitrateA += ac->bit_rate / 1000;

		mTrackA->meta->setCString(kKeyMIMEType, mimetypeA);
		mTrackA->meta->setInt32(kKeySampleRate, ac->sample_rate);
		mTrackA->meta->setInt32(kKeyBitRate, ac->bit_rate);
		mTrackA->meta->setInt32(kKeyChannelCount, ac->channels);
		mTrackA->meta->setInt32(kKeyFFcodecid, ac->codec_id);
		mTrackA->meta->setPointer(kKeyFFcodecctx, (void*) ac);

		mTrackA->meta->setCString(kKeyFFextractor, "FFExtractor");

		mFirstFramePos = 0;
		int64_t duration = 0;
		if (duration > 0)
		{
			mTrackA->meta->setInt64(kKeyDuration, duration);
		}
		else
		{
			off_t fileSize;
			if (mDataSource->getSize(&fileSize) == OK)
			{
				mTrackA->meta->setInt64(kKeyDuration, 8000LL * (fileSize - mFirstFramePos) / bitrateA);
			}
		}
		LOGV("audio bitrate %d kbps.", bitrateA);
		LOGV("FFExtractor() audio done.");
	}

	if (hasVideo)
	{
		mTrackV = new Track;
		mTrackV->meta = new MetaData;

		bitrateV += vc->bit_rate / 1000;

		mTrackV->meta->setCString(kKeyMIMEType, mimetypeV);
		mTrackV->meta->setInt32(kKeyWidth, vc->width);
		mTrackV->meta->setInt32(kKeyHeight, vc->height);
		mTrackV->meta->setInt32(kKeyBitRate, vc->bit_rate);
		mTrackV->meta->setInt64(kKeyDuration, fc->duration);
		mTrackV->meta->setInt32(kKeyFFcodecid, vc->codec_id);
		mTrackV->meta->setPointer(kKeyFFcodecctx, (void*) vc);

		mTrackV->meta->setCString(kKeyFFextractor, "FFExtractor");

		LOGV("video bitrate %d kbps.", bitrateV);
		LOGV("FFExtractor() video done.");
	}

	mInitCheck = OK;
	LOGV("FFExtractor() done. total bitrate:%d kbps", bitrateA + bitrateV);
}

size_t FFExtractor::countTracks()
{
	int r = 0;

	if (mInitCheck != OK)
	{
	}
	else
	{
#ifndef VIDEO_ONLY
		if (hasAudio)
			r++;
#endif
		if (hasVideo)
			r++;
	}
	LOGV("countTracks return %d. ", r);

	return r;
}

sp<MediaSource> FFExtractor::getTrack(size_t index)
{
	if (mInitCheck != OK)
	{
		return NULL;
	}
	LOGV("getTrack(%d) new FFSource.", index);
#ifndef VIDEO_ONLY
	if (index == 0)
#else
		if (!hasVideo)
#endif
		return new FFSource(mTrackA->meta, mDataSource, mFirstFramePos, mFixedHeader, mByteNumber, NULL);
	else
		return new FFSource(mTrackV->meta, mDataSource, mFirstFramePos, mFixedHeader, mByteNumber, NULL);
}

sp<MetaData> FFExtractor::getTrackMetaData(size_t index, uint32_t flags)
{
	if (mInitCheck != OK)
	{
		return NULL;
	}
	LOGV("getTrackMetaData(%d).", index);
#ifndef VIDEO_ONLY
	if (index == 0)
#else
		if (!hasVideo)
#endif
		return mTrackA->meta;
	else
		return mTrackV->meta;
}

//////////////////////////////////FFSource//////////////////////////////////////////////

FFSource::FFSource(const sp<MetaData> &meta, const sp<DataSource> &source, off_t first_frame_pos, uint32_t fixed_header,
		int32_t byte_number, const char *table_of_contents) :
		mMeta(meta), mDataSource(source), mFirstFramePos(first_frame_pos), mFixedHeader(fixed_header), mCurrentPos(0), mCurrentTimeUs(
				0), mStarted(false), mByteNumber(byte_number), mGroup(NULL)
{
	//memcpy (mTableOfContents, table_of_contents, sizeof(mTableOfContents));
	hasVideo = false;
	hasAudio = false;

	const char *mime = NULL;
	CHECK(mMeta->findCString(kKeyMIMEType, &mime));
	if (!strncasecmp(mime, "video/", 6))
		hasVideo = true;
	if (!strncasecmp(mime, "audio/", 6))
		hasAudio = true;
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

	size_t kMaxFrameSize;
	if (hasVideo)
		kMaxFrameSize = 300 * 1024; //For 1080P, add *3.
	else
		kMaxFrameSize = 64 * 1024;
	mGroup->add_buffer(new MediaBuffer(kMaxFrameSize));
	mGroup->add_buffer(new MediaBuffer(kMaxFrameSize));
	LOGV("FFSource::start, Tommy do ONE more new MediaBuffer %d bytes. for ffcodec", kMaxFrameSize);

	mCurrentPos = mFirstFramePos;
	mCurrentTimeUs = 0;

#if 1
//	aframe = avcodec_alloc_frame();
	memset(&apkt, 0, sizeof(apkt));
	memset(&vpkt, 0, sizeof(vpkt));
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
//	av_free(aframe);
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
			av_seek_frame(fc, -1, seekTimeUs, AVSEEK_FLAG_BACKWARD);
		}
	}
#endif
	int frame_size = 0;
	int bitrate;

	MediaBuffer *buffer;
	status_t err = mGroup->acquire_buffer(&buffer);
	if (err != OK)
	{
		return err;
	}

	int status = 0;

	buffer->set_range(0, 0);
	if (hasAudio)
	{
		while ((status = av_read_frame(fc, &apkt)) == 0)
		{
			if (apkt.stream_index == audioidx)
			{
				LOGV("read audio packet %d bytes.", apkt.size);
				memcpy(buffer->data() + buffer->range_length(), apkt.data, apkt.size);
				buffer->set_range(0, buffer->range_length() + apkt.size);
				frame_size += apkt.size;
				continue;
			}
			else
			{
				LOGV("got video when read audio. save video packet. then return");
//				vpkt = apkt;
				break;
			}
		}

	}
	else if (hasVideo)
	{
		if (apkt.size)
		{
			//Video stored in last apkt.
			memcpy(buffer->data() + buffer->range_length(), apkt.data, apkt.size);
			buffer->set_range(0, buffer->range_length() + apkt.size);
			frame_size += apkt.size;
			apkt.size = 0;
		}
		else
		{
			while ((status = av_read_frame(fc, &apkt)) == 0)
			{
				if (apkt.stream_index == videoidx)
				{
					LOGV("read video packet %d bytes.", apkt.size);
					memcpy(buffer->data() + buffer->range_length(), apkt.data, apkt.size);
					buffer->set_range(0, buffer->range_length() + apkt.size);
					frame_size += apkt.size;
					break;
				}
				else
				{
					LOGV("got audio when read video. ");
				}
			}
		}
	}

	if (status != 0 && buffer->range_length() == 0)
	{
		buffer->release();
		buffer = NULL;

		return ERROR_END_OF_STREAM;
	}

//	memcpy(buffer->data(), apkt.data, apkt.size);
//	buffer->set_range(0, apkt.size);

	buffer->meta_data()->setInt64(kKeyTime, mCurrentTimeUs);
	buffer->meta_data()->setInt32(kKeyIsSyncFrame, 1);

	mCurrentPos += frame_size;

	if (hasVideo)
	{
		bitrate = bitrateV;
		if (bitrate == 0)
		{
			LOGE("bitrate %d, use time_base.", bitrate);
			mCurrentTimeUs += av_q2d(fc->streams[videoidx]->codec->time_base) * 1000000L;
		}
		else
		{
			mCurrentTimeUs += frame_size * 8000ll / bitrate;
		}
	}
	else if (hasAudio)
	{
		bitrate = bitrateA;
		mCurrentTimeUs += frame_size * 8000ll / bitrate;
	}

//	LOGV(" video bitrate is %d, frame_rate %lf. time base %lf. ", fc->streams[videoidx]->codec->bit_rate, av_q2d(fc->streams[videoidx]->avg_frame_rate),
//			av_q2d(fc->streams[videoidx]->codec->time_base));

	*out = buffer;
	LOGV("FFSource::read %d bytes. ", buffer->range_length());

	return OK;
}

sp<MetaData> FFExtractor::getMetaData()
{
	sp<MetaData> meta = new MetaData;

	if (mInitCheck != OK)
	{
		return meta;
	}

	if (hasAudio)
		meta->setCString(kKeyMIMEType, "audio/mp4");
	if (hasVideo)
		meta->setCString(kKeyMIMEType, "video/mp4");

	return meta;
}

bool SniffFF(const sp<DataSource> &source, String8 *mimeType, float *confidence, sp<AMessage> *)
{
	char buf[256];
	bool audiosupport = false, videosupport = false;

	LOGV("enter SniffFF. ");
//	return false;

	*confidence = 0.0f;

	I("\n**************************SniffFF*******************************\n");
	I( "*  FFplayer based on libffmpeg, build time: %s %s \n", __DATE__, __TIME__);
#ifdef OPT_TOMMY_NEON
	I("***************  TOMMY OPTIMIZED USING NEON  ********************\n");
#endif
//	I("avcodec version %d\n", avutil_version());
//	I("avcodec version %d\n", avcodec_version());
//	I("avformat version %d\n", avformat_version());
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
	videoidx = -1;
	hasVideo = false;
	hasAudio = false;

	//fc = avformat_alloc_context();
	if (fc != NULL)
		avformat_close_input(&fc);

	if (avformat_open_input(&fc, source->uri_file_tommy, NULL, 0) < 0)
	{
		LOGE("could not open file\n");
		return false;
	}
	fc->flags |= AVFMT_FLAG_GENPTS;

	if (avformat_find_stream_info(fc, 0) < 0)
	{
		LOGE("find stream failed. \n");
		return false;
	}

	LOGV("nb_streams is %d\n", fc->nb_streams);
	for (unsigned int i = 0; i < fc->nb_streams; i++)
	{
		LOGV("\nStream #%d: ", i);
		switch (fc->streams[i]->codec->codec_type)
		{
		case AVMEDIA_TYPE_VIDEO:
			videoidx = i;
			LOGV("Video..............................");
			break;
		case AVMEDIA_TYPE_AUDIO:
			audioidx = i;
			LOGV("Audio..............................");
			break;
		default:
			LOGV("OTHER AVMEDIA. ");
			break;
		}
		LOGV("codec_name:%s. id:%xH. tag:%xH", fc->streams[i]->codec->codec_name, fc->streams[i]->codec->codec_id,
				&(fc->streams[i]->codec->codec_tag));
		avcodec_string(buf, sizeof(buf), fc->streams[i]->codec, 1);
		LOGV("%s", buf);

	}

	LOGV("\n");

	if (audioidx == -1)
	{
		LOGV("leave SniffFF. no audio idx found.");
		return false;
	}

	ac = fc->streams[audioidx]->codec;

	switch (ac->codec_id)
	{
	case CODEC_ID_WMAV1:
	case CODEC_ID_WMAV2:
	case CODEC_ID_WMAPRO:
		mimetypeA = MEDIA_MIMETYPE_AUDIO_WMA;
		audiosupport = true;
		break;
	case CODEC_ID_MP1:
	case CODEC_ID_MP2:
	case CODEC_ID_MP3:
		mimetypeA = MEDIA_MIMETYPE_AUDIO_MPEG;
		audiosupport = true;
		break;
	case CODEC_ID_AAC:
		mimetypeA = MEDIA_MIMETYPE_AUDIO_AAC;
		audiosupport = true;
		break;
	case CODEC_ID_AMR_NB:
	case CODEC_ID_AMR_WB:
		mimetypeA = MEDIA_MIMETYPE_AUDIO_AMR_NB;
		audiosupport = true;
	case CODEC_ID_COOK:
		mimetypeA = MEDIA_MIMETYPE_AUDIO_RAW;
		audiosupport = true;

	default:
		*confidence = 0.0f;
		break;
	}
	hasAudio = audiosupport;

	if (videoidx != -1)
	{
		vc = fc->streams[videoidx]->codec;
		switch (vc->codec_id)
		{
		case CODEC_ID_H263:
			mimetypeV = MEDIA_MIMETYPE_VIDEO_H263;
			videosupport = true;
			break;
		case CODEC_ID_H264:
			mimetypeV = MEDIA_MIMETYPE_VIDEO_AVC;
			videosupport = true;
			break;
		case CODEC_ID_MPEG1VIDEO:
		case CODEC_ID_RV10:
		case CODEC_ID_RV20:
		case CODEC_ID_RV30:
		case CODEC_ID_RV40:
		case CODEC_ID_MPEG2VIDEO:
		case CODEC_ID_MPEG4:
			mimetypeV = MEDIA_MIMETYPE_VIDEO_AVC;
			videosupport = true;
			break;
		default:
			*confidence = 0.0f;
			break;
		}
		hasVideo = videosupport;
	}

	if (hasAudio && !hasVideo)
	{
		*mimeType = "audio/ffone"; //mimetypeA;
		*confidence = 0.73f;
	}
	else if (hasVideo)
	{
		*mimeType = "video/ffone"; //MEDIA_MIMETYPE_CONTAINER_MPEG4;
		*confidence = 0.73f;
	}

//	*confidence = 0.0f;
	LOGV("*confidence is %.2f, video:%s, audio:%s", *confidence, hasVideo ? "Yes" : "No", hasAudio ? "Yes" : "No");
	LOGV("leave SniffFF. ");

	return true;
}

} // namespace android

