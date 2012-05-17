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

#ifndef MP3_DECODER_TOMMY_H_

#define MP3_DECODER_TOMMY_H_

#include <media/stagefright/MediaSource.h>

//struct tPVMP3DecoderExternal;

namespace android {

struct MediaBufferGroup;

struct MP3DecoderTommy : public MediaSource {
    MP3DecoderTommy(const sp<MediaSource> &source);

    virtual status_t start(MetaData *params);
    virtual status_t stop();

    virtual sp<MetaData> getFormat();

    virtual status_t read(
            MediaBuffer **buffer, const ReadOptions *options);

protected:
    virtual ~MP3DecoderTommy();

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
    MediaBuffer *mPartialBuffer;

    void init();

    MP3DecoderTommy(const MP3DecoderTommy &);
    MP3DecoderTommy &operator=(const MP3DecoderTommy &);
    status_t updatePartialFrame();
    
    status_t decode_input_read();
};

}  // namespace android

#endif  // MP3_DECODER_H_
