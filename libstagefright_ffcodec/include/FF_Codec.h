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

#ifndef FF_CODEC_H

#define FF_CODEC_H

#include <media/stagefright/MediaSource.h>

//struct tPVMP3DecoderExternal;

namespace android {

struct MediaBufferGroup;

struct FF_CODEC : public MediaSource {
    FF_CODEC(const sp<MediaSource> &source);

    virtual status_t start(MetaData *params);
    virtual status_t stop();

    virtual sp<MetaData> getFormat();

    virtual status_t read(
            MediaBuffer **buffer, const ReadOptions *options);

protected:
    virtual ~FF_CODEC();

private:
    sp<MediaSource> mSource;
    sp<MetaData> mMeta;
    int32_t mNumChannels;

    bool mStarted;

    MediaBufferGroup *mBufferGroup;

    //tPVMP3DecoderExternal *mConfig;
    void *mConfig;
    
    void *mDecoderBuf;
    int64_t mAnchorTimeUs;
    int64_t mNumFramesOutput;
    uint32_t mFixedHeader;

    MediaBuffer *mInputBuffer;
    //MediaBuffer *mPartialBuffer;		// Tommy:no use

    void init();

    FF_CODEC(const FF_CODEC &);
    FF_CODEC &operator=(const FF_CODEC &);
    //status_t updatePartialFrame();
    
};

}  // namespace android

#endif  // FF_CODEC_H
