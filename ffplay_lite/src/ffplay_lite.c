/*
 ============================================================================
 Name        : ffplay_lite.c
 Author      : ctao
 Version     :
 Copyright   : Your copyright notice
 Description : Hello World in C, Ansi-style
 ============================================================================
 */

/* based on ffmpeg/doc/examples/Decoding_encoding.c */

/*
 * Copyright (c) 2001 Fabrice Bellard
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

/**
 * @file
 * libavcodec API use example.
 *
 * Note that libavcodec only handles codecs (mpeg, mpeg4, etc...),
 * not file formats (avi, vob, mp4, mov, mkv, mxf, flv, mpegts, mpegps, etc...). See library 'libavformat' for the
 * format handling
 */

#include "libavutil/imgutils.h"
#include "libavutil/opt.h"
#include "libavcodec/avcodec.h"
#include "libavutil/mathematics.h"
#include "libavutil/samplefmt.h"
#include "libavformat/avformat.h"
#include "libavutil/avutil.h"
#include "libswresample/swresample.h"

#include "SDL.h"
#include "SDL_main.h"
#include "av_io.h"

/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/
#define INBUF_SIZE 4096
#define AUDIO_INBUF_SIZE (1024*32)
#define AUDIO_REFILL_THRESH 4096

#define VIDEO_INBUF_SIZE (1024*200)

#define AUDIO_DATAIN_SIZE (AUDIO_INBUF_SIZE + FF_INPUT_BUFFER_PADDING_SIZE)
#define VIDEO_DATAIN_SIZE (VIDEO_INBUF_SIZE + FF_INPUT_BUFFER_PADDING_SIZE)

#define AUDIO_OUTBUF_SIZE		(1024*20)

#define MAX_AUDIOQ_SIZE (5 * 16 * 1024)
#define MAX_VIDEOQ_SIZE (5 * 256 * 1024)

// SDL
#define FF_REFRESH_EVENT (SDL_USEREVENT + 0)

//#define DEBUG

#if 1//def DEBUG
#define log(a, b...)	fprintf(stdout, "FFPLAY:"a, ##b)
#else
#define log(a, b...)
#endif

#ifdef DEBUG
#define logd(a, b...)	fprintf(stdout,  "FFPLAY:"a, ##b)
#else
#define logd(a, b...)
#endif

#if 1//def DEBUG
#define logi(a, b...)	fprintf(stdout,  "FFPLAY info: "a, ##b)
#else
#define logi(a, b...)
#endif

#define loge(a, b...)	fprintf(stderr, a, ##b)

#define TRUE 1
#define FALSE 0
#define VERSION "0.01"
#define AUTHOR "Tommy"

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/
typedef struct RINGBUFF
{
	int id;
	uint8_t *bufstart; //buffer start point. readonly.
	int size; // total buffer len.
	int index; //vaild data index from buffer start.
	int len; //valid data len.
} RINGBUFF;

typedef struct PacketQueue
{
	AVPacketList *first_pkt, *last_pkt;
	int nb_packets;
	int size;
	SDL_mutex *mutex;
	SDL_cond *cond;
} PacketQueue;

typedef struct VideoState
{
	AVFormatContext *pFormatCtx;
	int videoStream, audioStream;

	// Audio
	AVStream *audio_st;
	PacketQueue audioq;
	uint8_t audio_buf[(AVCODEC_MAX_AUDIO_FRAME_SIZE * 3) / 2];

unsigned	int audio_buf_size; // data size of last fill. won't change when using it.
	unsigned int audio_buf_index;// after fill data, set to 0, increased to audio_buf_size when using it.
	AVPacket audio_pkt;
	AVPacket audio_pkt_dec;
	AVCodec *acodec;
	AVCodecContext *ac;
	AVFrame *aframe;

	// Video
	PacketQueue videoq;
	AVCodec *vcodec;
	AVFrame *picture;
	AVCodecContext *vc;

	int quit;
} VideoState;

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
RINGBUFF rb_aout;

VideoState *is;

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

/*
 * Audio encoding example
 */
static void audio_encode_example(const char *outfilename, const char *filename)
{
	AVCodec *codec;
	AVCodecContext *c = NULL;
	int frame_size, i, j, out_size, outbuf_size;
	FILE *f, *outfile;
	short *samples;
//	float t, tincr;
	uint8_t *outbuf;

	printf("Audio encoding...writing to %s\n", outfilename);

	/* find the MP2 encoder */
	codec = avcodec_find_encoder(CODEC_ID_MP2);
	if (!codec)
	{
		fprintf(stderr, "codec not found\n");
		exit(1);
	}

	c = avcodec_alloc_context3(codec);

	/* put sample parameters */
	c->bit_rate = 64000;
	c->sample_rate = 44100;
	c->channels = 2;
	c->sample_fmt = AV_SAMPLE_FMT_S16;

	/* open it */
	if (avcodec_open2(c, codec, 0) < 0)
	{
		fprintf(stderr, "could not open codec\n");
		exit(1);
	}

	/* the codec gives us the frame size, in samples */
	frame_size = c->frame_size;
	samples = malloc(frame_size * 2 * c->channels);
	outbuf_size = 10000;
	outbuf = malloc(outbuf_size);

	f = fopen(filename, "rb");
	if (!f)
	{
		fprintf(stderr, "could not open %s\n", filename);
		exit(1);
	}

	outfile = fopen(outfilename, "wb");
	if (!f)
	{
		fprintf(stderr, "could not open %s\n", outfilename);
		exit(1);
	}

	{
		int len;
		while (1)
		{
			// read pcm data.
			len = fread(samples, 1, frame_size * 2 * c->channels, f);
			if (len == 0)
			{
				fprintf(stderr, "Error while reading\n");
				break;
			}
			/* encode the samples */
			out_size = avcodec_encode_audio(c, outbuf, outbuf_size, samples);

			fwrite(outbuf, 1, out_size, outfile);
		}
	}

	fclose(f);
	fclose(outfile);
	free(outbuf);
	free(samples);

	avcodec_close(c);
	av_free(c);
}

/*
 * Audio decoding.
 */
static void audio_decode_example(const char *outfilename, const char *filename)
{
	AVCodec *codec;
	AVCodecContext *c = NULL;
	int len, ending;
	FILE *f, *outfile;
	AVPacket avpkt;
	AVFrame *decoded_frame = NULL;
	uint8_t inbuf[AUDIO_INBUF_SIZE + FF_INPUT_BUFFER_PADDING_SIZE];

printf	("Audio decoding...writing to %s.\n", outfilename);

	av_init_packet(&avpkt);

	/* find the mpeg audio decoder */
	codec = avcodec_find_decoder(CODEC_ID_MP3);
	if (!codec)
	{
		fprintf(stderr, "codec not found\n");
		exit(1);
	}

	// Tommy: here, c have to be allocated. because we don't use avformat.
	// for mp3, as mpeg header contain all the audio informations, so if not init c, still decode ok.
	// but for aac, if input pure stream, not contain ADTS header, we MUST init c to make decode ok.
	c = avcodec_alloc_context3(codec);

	/* open it */
	if (avcodec_open2(c, codec, 0) < 0)
	{
		fprintf(stderr, "could not open codec\n");
		exit(1);
	}

	f = fopen(filename, "rb");
	if (!f)
	{
		fprintf(stderr, "could not open %s\n", filename);
		exit(1);
	}
	outfile = fopen(outfilename, "wb");
	if (!outfile)
	{
		av_free(c);
		exit(1);
	}

	/* decode until eof */
	avpkt.data = inbuf;
	avpkt.size = fread(inbuf, 1, AUDIO_INBUF_SIZE, f);

	ending = FALSE;

	while (avpkt.size > 0)
	{
		int got_audio_frame = 0;

//		printf("avpkt.size is %d \n", avpkt.size);
		if (!decoded_frame)
		{
			if (!(decoded_frame = avcodec_alloc_frame()))
			{
				fprintf(stderr, "out of memory\n");
				exit(1);
			}
		}
		else
			avcodec_get_frame_defaults(decoded_frame);

		// len is the used bytes from the input stream.
		len = avcodec_decode_audio4(c, decoded_frame, &got_audio_frame, &avpkt);
		if (len < 0)
		{
			log("avpkt.size  %d bytes left.\n", avpkt.size);
			fprintf(stderr, "Error while decoding\n");
			if (ending == TRUE)
			{
				avpkt.size = 0;
				break;
			}
//			exit(1);
			avpkt.size -= 1;
			avpkt.data += 1;
			continue;
		}
		if (got_audio_frame)
		{
//			printf("^, ch:%d, samples:%d, fmt:%d\n", c->channels,
//					decoded_frame->nb_samples, c->sample_fmt);
			/* if a frame has been decoded, output it */
			int data_size = av_samples_get_buffer_size(NULL, c->channels, decoded_frame->nb_samples, c->sample_fmt, 1);
			fwrite(decoded_frame->data[0], 1, data_size, outfile);
		}
		avpkt.size -= len;
		avpkt.data += len;
		avpkt.dts = avpkt.pts = AV_NOPTS_VALUE;
		if (avpkt.size < AUDIO_REFILL_THRESH)
		{
			/* Refill the input buffer, to avoid trying to decode
			 * incomplete frames. Instead of this, one could also use
			 * a parser, or use a proper container format through
			 * libavformat. */
			memmove(inbuf, avpkt.data, avpkt.size);
			avpkt.data = inbuf;
			len = fread(avpkt.data + avpkt.size, 1, AUDIO_INBUF_SIZE - avpkt.size, f);
//			printf(" only %d left, read %d \n", avpkt.size, len);
			if (len > 0)
			{
				avpkt.size += len;
			}
			else
			{ // Reach EOF
				ending = TRUE;
			}
		}
	}

	fclose(outfile);
	fclose(f);

	avcodec_close(c);
	av_free(c);
	av_free(decoded_frame);
}

/*
 * Video encoding example
 */
static void video_encode_example(const char *filename, int codec_id)
{
	AVCodec *codec;
	AVCodecContext *c = NULL;
	int i, out_size, size, x, y, outbuf_size;
	FILE *f;
	AVFrame *picture;
	uint8_t *outbuf;

	printf("Video encoding\n");

	/* find the mpeg1 video encoder */
	codec = avcodec_find_encoder(codec_id);
	if (!codec)
	{
		fprintf(stderr, "codec not found\n");
		exit(1);
	}

	c = avcodec_alloc_context3(codec);
	picture = avcodec_alloc_frame();

	/* put sample parameters */
	c->bit_rate = 400000;
	/* resolution must be a multiple of two */
	c->width = 352;
	c->height = 288;
	/* frames per second */
	c->time_base = (AVRational
)			{	1,25};
	c->gop_size = 10; /* emit one intra frame every ten frames */
	c->max_b_frames = 1;
	c->pix_fmt = PIX_FMT_YUV420P;

	if (codec_id == CODEC_ID_H264)
		av_opt_set(c->priv_data, "preset", "slow", 0);

	/* open it */
	if (avcodec_open2(c, codec, 0) < 0)
	{
		fprintf(stderr, "could not open codec\n");
		exit(1);
	}

	f = fopen(filename, "wb");
	if (!f)
	{
		fprintf(stderr, "could not open %s\n", filename);
		exit(1);
	}

	/* alloc image and output buffer */
	outbuf_size = 100000;
	outbuf = malloc(outbuf_size);

	/* the image can be allocated by any means and av_image_alloc() is
	 * just the most convenient way if av_malloc() is to be used */
	av_image_alloc(picture->data, picture->linesize, c->width, c->height, c->pix_fmt, 1);

	/* encode 1 second of video */
	for (i = 0; i < 25; i++)
	{
		fflush(stdout);
		/* prepare a dummy image */
		/* Y */
		for (y = 0; y < c->height; y++)
		{
			for (x = 0; x < c->width; x++)
			{
				picture->data[0][y * picture->linesize[0] + x] = x + y + i * 3;
			}
		}

		/* Cb and Cr */
		for (y = 0; y < c->height / 2; y++)
		{
			for (x = 0; x < c->width / 2; x++)
			{
				picture->data[1][y * picture->linesize[1] + x] = 128 + y + i * 2;
				picture->data[2][y * picture->linesize[2] + x] = 64 + x + i * 5;
			}
		}

		/* encode the image */
		out_size = avcodec_encode_video(c, outbuf, outbuf_size, picture);
		printf("encoding frame %3d (size=%5d)\n", i, out_size);
		fwrite(outbuf, 1, out_size, f);
	}

	/* get the delayed frames */
	for (; out_size; i++)
	{
		fflush(stdout);

		out_size = avcodec_encode_video(c, outbuf, outbuf_size, NULL);
		printf("write frame %3d (size=%5d)\n", i, out_size);
		fwrite(outbuf, 1, out_size, f);
	}

	/* add sequence end code to have a real mpeg file */
	outbuf[0] = 0x00;
	outbuf[1] = 0x00;
	outbuf[2] = 0x01;
	outbuf[3] = 0xb7;
	fwrite(outbuf, 1, 4, f);
	fclose(f);
	free(outbuf);

	avcodec_close(c);
	av_free(c);
	av_free(picture->data[0]);
	av_free(picture);
	printf("\n");
}

/*
 * Video decoding example
 */

static void pgm_save(unsigned char *buf, int wrap, int xsize, int ysize, char *filename)
{
	FILE *f;
	int i;

	f = fopen(filename, "w");
	fprintf(f, "P5\n%d %d\n%d\n", xsize, ysize, 255);
	for (i = 0; i < ysize; i++)
		fwrite(buf + i * wrap, 1, xsize, f);
	fclose(f);
}

static void picture_yuv420_save(FILE *fp, AVFrame *picture, int xsize, int ysize)
{
	int i;

	// Note: xsize <= linesize[x];
	//Y
	for (i = 0; i < ysize; i++)
		fwrite(picture->data[0] + i * picture->linesize[0], 1, xsize, fp);
	//U
	for (i = 0; i < ysize / 2; i++)
		fwrite(picture->data[1] + i * picture->linesize[1], 1, xsize / 2, fp);
	//V
	for (i = 0; i < ysize / 2; i++)
		fwrite(picture->data[2] + i * picture->linesize[2], 1, xsize / 2, fp);
}

static void video_decode_example(const char *outfilename, const char *filename)
{
	AVCodec *codec;
	AVCodecContext *c = NULL;
	int frame, got_picture, len;
	FILE *f, *outfile = NULL;
	AVFrame *picture;
	char buf[1024];
	uint8_t inbuf[VIDEO_DATAIN_SIZE];
	AVPacket avpkt;

	av_init_packet(&avpkt);

	/* set end of buffer to 0 (this ensures that no overreading happens for damaged mpeg streams) */
	memset(inbuf + INBUF_SIZE, 0, FF_INPUT_BUFFER_PADDING_SIZE);

	printf("Video decoding\n");

	/* find the mpeg1 video decoder */
	codec = avcodec_find_decoder(CODEC_ID_MPEG1VIDEO);
	if (!codec)
	{
		fprintf(stderr, "codec not found\n");
		exit(1);
	}

	c = avcodec_alloc_context3(codec);
	picture = avcodec_alloc_frame();

	if (codec->capabilities & CODEC_CAP_TRUNCATED
	)
		c->flags |= CODEC_FLAG_TRUNCATED; /* we do not send complete frames */

	/* For some codecs, such as msmpeg4 and mpeg4, width and height
	 MUST be initialized there because this information is not
	 available in the bitstream. */

	/* open it */
	if (avcodec_open2(c, codec, 0) < 0)
	{
		fprintf(stderr, "could not open codec\n");
		exit(1);
	}

	/* the codec gives us the frame size, in samples */

	f = fopen(filename, "rb");
	if (!f)
	{
		fprintf(stderr, "could not open %s\n", filename);
		exit(1);
	}

	frame = 0;
	for (;;)
	{
		avpkt.size = fread(inbuf, 1, INBUF_SIZE, f);
		if (avpkt.size == 0)
			break;

		/* NOTE1: some codecs are stream based (mpegvideo, mpegaudio)
		 and this is the only method to use them because you cannot
		 know the compressed data size before analysing it.

		 BUT some other codecs (msmpeg4, mpeg4) are inherently frame
		 based, so you must call them with all the data for one
		 frame exactly. You must also initialize 'width' and
		 'height' before initializing them. */

		/* NOTE2: some codecs allow the raw parameters (frame size,
		 sample rate) to be changed at any frame. We handle this, so
		 you should also take care of it */

		/* here, we use a stream based decoder (mpeg1video), so we
		 feed decoder and see if it could decode a frame */
		avpkt.data = inbuf;
		while (avpkt.size > 0)
		{
			len = avcodec_decode_video2(c, picture, &got_picture, &avpkt);
			if (len < 0)
			{
				fprintf(stderr, "Error while decoding frame %d\n", frame);
				exit(1);
			}
			if (got_picture)
			{
//				printf("saving frame %3d\n", frame);
//				fflush(stdout);

				if (outfile == NULL)
				{
					buf[0] = 0;
					sprintf(buf, "%dx%d.yuv", c->width, c->height);
					outfile = fopen(buf, "wb");
					if (!f)
					{
						fprintf(stderr, "could not open %s\n", buf);
						exit(1);
					}
					printf("writing yuv data to %s\n", buf);

					buf[0] = 0;
				}
				/* the picture is allocated by the decoder. no need to
				 free it */
//				snprintf(buf, sizeof(buf), outfilename, frame);
//				pgm_save(picture->data[0], picture->linesize[0], c->width,
//						c->height, buf);
				if (frame == 0)
				{
					printf("yuv420 save: w:%d, h:%d, linesize:%d,%d,%d\n", picture->width, picture->height,
							picture->linesize[0], picture->linesize[1], picture->linesize[2]);
				}
				picture_yuv420_save(outfile, picture, c->width, c->height);

				frame++;
			}
			avpkt.size -= len;
			avpkt.data += len;

		}

		if (frame > 1000)
			break;
	}

#if 0
	// Handle last frame.
	/* some codecs, such as MPEG, transmit the I and P frame with a
	 latency of one frame. You must do the following to have a
	 chance to get the last frame of the video */
	avpkt.data = NULL;
	avpkt.size = 0;
	len = avcodec_decode_video2(c, picture, &got_picture, &avpkt);
	if (got_picture)
	{
		printf("saving last frame %3d\n", frame);
		fflush(stdout);

		/* the picture is allocated by the decoder. no need to
		 free it */
		snprintf(buf, sizeof(buf), outfilename, frame);
		pgm_save(picture->data[0], picture->linesize[0], c->width, c->height,
				buf);
		frame++;
	}
#endif

	fclose(f);
	fclose(outfile);

	avcodec_close(c);
	av_free(c);
	av_free(picture);
	printf("\n");
}

static void avfile_demux_example(const char *filename, int isSDLshow)
{
	AVFormatContext *c;
	AVPacket avpkt;
	FILE *fa, *fv;
	char str[128];
	int i;
	int audioidx, videoidx;

	printf(" avfile decoding ... \n");

	c = avformat_alloc_context();
	if (avformat_open_input(&c, filename, NULL, 0) < 0)
	{
		fprintf(stderr, "could not open file\n");
		return;
	}
	c->flags |= AVFMT_FLAG_GENPTS;

	if (avformat_find_stream_info(c, 0) < 0)
	{
		fprintf(stderr, "find stream failed. \n");
		return;
	}

	log("nb_streams is %d\n", c->nb_streams);
	for (i = 0; i < c->nb_streams; i++)
	{
		printf("\nStream #%d: \n ", i);
		switch (c->streams[i]->codec->codec_type)
		{
		case AVMEDIA_TYPE_VIDEO:
			videoidx = i;
			printf("Video.");
			break;
		case AVMEDIA_TYPE_AUDIO:
			audioidx = i;
			printf("Audio.");
			break;
		default:
			printf("OTHER AVMEDIA. ");
			break;
		}
		printf("codec_name:%s. id:%xH. tag:%xH", c->streams[i]->codec->codec_name, c->streams[i]->codec->codec_id,
				&(c->streams[i]->codec->codec_tag));
	}
	printf("\n");

	// Demux start
	if (!isSDLshow)
	{
		str[0] = 0;
		strcpy(str, filename);
		strcat(str, ".audiostream");
		fa = fopen(str, "wb");
		if (!fa)
		{
			fprintf(stderr, "could not open %s\n", str);
			return;
		}log("open stream files %s to write .\n", str);

		str[0] = 0;
		strcpy(str, filename);
		strcat(str, ".videostream");
		fv = fopen(str, "wb");
		if (!fv)
		{
			fprintf(stderr, "could not open %s\n", str);
			return;
		}
		log("open stream files %s to write .\n", str);

	}

	while (av_read_frame(c, &avpkt) >= 0)
	{
		if (!isSDLshow)
		{
			if (avpkt.stream_index == videoidx)
			{
				fwrite(avpkt.data, 1, avpkt.size, fv);
//				log("write audio %d bytes.\n", avpkt.size);
			}
			if (avpkt.stream_index == audioidx)
			{
				fwrite(avpkt.data, 1, avpkt.size, fa);
			}

		}
	}

	if (!isSDLshow)
	{
		fclose(fa);
		fclose(fv);
	}
	avformat_free_context(c);

}

void packet_queue_init(PacketQueue *q)
{
	memset(q, 0, sizeof(PacketQueue));
	q->mutex = SDL_CreateMutex();
	q->cond = SDL_CreateCond();
}

int packet_queue_put(PacketQueue *q, AVPacket *pkt)
{

	AVPacketList *pkt1;

	logd("pkt data pointer is %p\n", pkt->data);
	if (av_dup_packet(pkt) < 0)
	{
		return -1;
	}
	pkt1 = av_malloc(sizeof(AVPacketList));
	if (!pkt1)
		return -1;
	pkt1->pkt = *pkt;
	pkt1->next = NULL;

	SDL_LockMutex(q->mutex);

	if (!q->last_pkt)
		q->first_pkt = pkt1;
	else
		q->last_pkt->next = pkt1;
	q->last_pkt = pkt1;
	q->nb_packets++;
	q->size += pkt1->pkt.size;
	SDL_CondSignal(q->cond);

	SDL_UnlockMutex(q->mutex);
	return 0;
}

static int packet_queue_get(PacketQueue *q, AVPacket *pkt, int block)
{
	AVPacketList *pkt1;
	int ret;

	SDL_LockMutex(q->mutex);

	for (;;)
	{

//		if (global_video_state->quit)
//		{
//			ret = -1;
//			break;
//		}

		pkt1 = q->first_pkt;
		if (pkt1)
		{
			q->first_pkt = pkt1->next;
			if (!q->first_pkt)
				q->last_pkt = NULL;
			q->nb_packets--;
			q->size -= pkt1->pkt.size;
			*pkt = pkt1->pkt;
			av_free(pkt1);
			ret = 1;
			break;
		}
		else if (!block)
		{
			ret = 0;
			break;
		}
		else
		{
			SDL_CondWait(q->cond, q->mutex);
		}
	}

	SDL_UnlockMutex(q->mutex);
	return ret;
}

static int ringbuff_init(RINGBUFF *rb)
{
	memset(rb, 0, sizeof(RINGBUFF));
}

static int ringbuff_filldata(RINGBUFF *rb, unsigned char *stream, int len)
{
	int tailfree;

	log("ringbuffer#%d, fill %d bytes.  index:%d, len:%d\n", rb->id, len, rb->index, rb->len);
	if ((rb->len + len) < rb->size)
	{ // have free space.
		if ((rb->index + rb->len) > rb->size)
		{ // ring back.
			memcpy(rb->bufstart + (rb->index + rb->len - rb->size), stream, len);
		}
		else
		{
			tailfree = rb->size - (rb->index + rb->len);
			if (len < tailfree)
			{
				memcpy(rb->bufstart + (rb->index + rb->len), stream, len);
			}
			else
			{ // len > tailfree
				memcpy(rb->bufstart + (rb->index + rb->len), stream, tailfree);
				memcpy(rb->bufstart, stream + tailfree, (len - tailfree));
			}

		}
//		rb->index = (rb->index + len) % rb->size;
		rb->len += len;
//		log("ringbuffer#%d, fill done.  index:%d, len:%d\n",
//				rb->id, rb->index, rb->len);
	}
	else
	{
		logd("ringbuffer, overflow !!!\n");
		return 1;
	}
	return 0;
}

static int ringbuff_getdata(RINGBUFF *rb, unsigned char *stream, int len)
{
	int tailfree;

	log("ringbuffer#%d, get %d bytes.  index:%d, len:%d\n", rb->id, len, rb->index, rb->len);
	if (len <= rb->len)
	{ // have enough data.
		tailfree = rb->size - rb->index;
		if (len < tailfree)
		{
			memcpy(stream, rb->bufstart + rb->index, len);
		}
		else
		{
			memcpy(stream, rb->bufstart + rb->index, tailfree);
			memcpy(stream + tailfree, rb->bufstart, (len - tailfree));
		}
		rb->index = (rb->index + len) % rb->size;
		rb->len -= len;
		log("ringbuffer#%d, get done.  index:%d, len:%d\n", rb->id, rb->index, rb->len);
	}
	else
	{
		log("ringbuffer, underflow !!!\n");
		return 1;
	}
	return 0;
}

static int audio_mixer(unsigned char *stream, int len)
{
	logd("mixer. need %d bytes.\n", len);
	ringbuff_getdata(&rb_aout, stream, len);
	return 0;
}

static Uint32 sdl_refresh_timer_cb(Uint32 interval, void *opaque)
{
	SDL_Event event;
	event.type = FF_REFRESH_EVENT;
	event.user.data1 = opaque;
	SDL_PushEvent(&event);
	return 0; /* 0 means stop timer */
}

int audio_decode_frame(VideoState *is, uint8_t *audio_buf, int buf_size, double *pts_ptr)
{
	int len1, data_size, n;
	AVPacket *pkt = &is->audio_pkt;
	double pts;
	int got_audio_frame;

	for (;;)
	{
		while (is->audio_pkt_dec.size > 0)
		{
			avcodec_get_frame_defaults(is->aframe);
			got_audio_frame = 0;

			len1 = avcodec_decode_audio4(is->audio_st->codec, is->aframe, &got_audio_frame, &is->audio_pkt_dec);

			if (len1 < 0)
			{
				/* if error, skip frame */
				is->audio_pkt_dec.size = 0;
				break;
			}
			is->audio_pkt_dec.data += len1;
			is->audio_pkt_dec.size -= len1;

			if (got_audio_frame == 0)
			{
				/* No data yet, get more frames */
				//Tommy: must feed more data until get something decoded.
				continue;
			}

//			pts = is->audio_clock;
//			*pts_ptr = pts;
//			n = 2 * is->audio_st->codec->channels;
//			is->audio_clock += (double) data_size / (double) (n * is->audio_st->codec->sample_rate);

			/* We have decoded data, return it and come back for more later */
			//		char fmt_str[128] = "";
			//		log(
			//				"audio stream: ch:%d, srate:%d, samples:%d, fmt:%s\n",
			//				is->ac->channels, is->ac->sample_rate, is->aframe->nb_samples, av_get_sample_fmt_string(fmt_str, sizeof(fmt_str), is->ac->sample_fmt));

			/* if a frame has been decoded, output it */
			data_size = av_samples_get_buffer_size(NULL, is->ac->channels, is->aframe->nb_samples, is->ac->sample_fmt,
					1);
			memcpy(audio_buf, is->aframe->data[0], data_size);
			logd("get decoded pcm data %d bytes. \n", data_size);

			return data_size;
		}
		//Tommy: all data in packet used, it's time to free it.
		if (pkt->data)
		{
			logd("free audio packet.\n");
			av_free_packet(pkt);
		}

		if (is->quit)
		{
			return -1;
		}
		/* next packet */
		if (packet_queue_get(&is->audioq, pkt, 1) < 0)
		{
			return -1;
		}

		//Tommy: Backup, audio_pkt_dec will be modified when decoding.
		is->audio_pkt_dec = *pkt;

		/* if update, update the audio clock w/pts */
//		if (pkt->pts != AV_NOPTS_VALUE)
//		{
//			is->audio_clock = av_q2d(is->audio_st->time_base) * pkt->pts;
//		}
	}
}

void audio_callback(void *userdata, Uint8 *stream, int len)
{

//	VideoState *is = (VideoState *) userdata;
	int len1, audio_size;
	double pts;

#if 0
	if (0)
	{
		static FILE *fp = 0;
		static FILE *fw = 0;
		if (fp == 0)
		{
			fp = fopen("hero.wav", "rb");
		}
		fread(stream, 1, len, fp);

		AVPacket pkt;
		if (packet_queue_get(&is->audioq, &pkt, 1) >= 0)
		{
			log("pkt size %d", pkt.size);
			if (fw == 0)
			{
				fw = fopen("out.tmp", "wb");
			}
			fwrite(pkt.data, 1, pkt.size, fw);
			av_free_packet(&pkt);
		}
		return;
	}
#endif

	logd("enter audio_callback, need %d bytes\n", len);
	while (len > 0)
	{ //Tommy: loop to make sure all data got.
		if (is->audio_buf_index >= is->audio_buf_size)
		{
			/* We have already sent all our data; get more */
			audio_size = audio_decode_frame(is, is->audio_buf, sizeof(is->audio_buf), &pts);

			if (audio_size < 0)
			{
				/* If error, output silence */
				is->audio_buf_size = 1024;
				memset(is->audio_buf, 0, is->audio_buf_size);
			}
			else
			{ //Tommy: got one frame.
//				audio_size = synchronize_audio(is, (int16_t *) is->audio_buf, audio_size, pts);
				is->audio_buf_size = audio_size;
			}
			is->audio_buf_index = 0; //Tommy: reset index.
			logd("audio_decode_frame got %d bytes.\n", audio_size);
		}

		//Tommy: get valid data size.
		len1 = is->audio_buf_size - is->audio_buf_index;
		if (len1 > len)
			len1 = len; // Tommy: if we have enough data, only send they required.
		memcpy(stream, (uint8_t *) is->audio_buf + is->audio_buf_index, len1);
		len -= len1;
		stream += len1;
		is->audio_buf_index += len1;
	}
	logd("leave audio_callback\n");
}

static void avfile_playback_example(const char *filename, int enable_audio, int enable_video)
{
	AVFormatContext *c;
	int i, frame, pic_displayed;
	AVPacket pkt1, *packet = &pkt1;

	printf("avfile playback start ... \n");

	// AVFORMAT
	c = avformat_alloc_context();
	if (avformat_open_input(&c, filename, NULL, 0) < 0)
	{
		fprintf(stderr, "could not open file\n");
		return;
	}
	c->flags |= AVFMT_FLAG_GENPTS;

	if (avformat_find_stream_info(c, 0) < 0)
	{
		fprintf(stderr, "find stream failed. \n");
		return;
	}

	logi("nb_streams is %d\n", c->nb_streams);
	for (i = 0; i < c->nb_streams; i++)
	{
		AVStream *st = c->streams[i];
		char buf[256];

		logi("Stream #%d: \n", i);
		switch (c->streams[i]->codec->codec_type)
		{
		case AVMEDIA_TYPE_VIDEO:
			is->videoStream = i;
			break;
		case AVMEDIA_TYPE_AUDIO:
			is->audioStream = i;
			break;
		default:
			logi("AVMEDIA TYPE %d: ", st->codec->codec_type);
		}
		avcodec_string(buf, sizeof(buf), st->codec, 1);
		logi(
				"\n[0x%x]:%s, \ncodec_name:'%s'. id:%05xH. tag:%08xH. time_base:%d, %d\n",
				st->id, buf, st->codec->codec_name, st->codec->codec_id, (st->codec->codec_tag), st->codec->time_base.num, st->codec->time_base.den);
	}

	// AVCODEC
	is->pFormatCtx = c;
	is->ac = c->streams[is->audioStream]->codec;
	is->vc = c->streams[is->videoStream]->codec;

	/* find the mpeg audio decoder */
	is->acodec = avcodec_find_decoder(is->ac->codec_id);
	if (!is->acodec)
	{
		fprintf(stderr, "acodec not found\n");
		exit(1);
	}
	is->vcodec = avcodec_find_decoder(is->vc->codec_id);
	if (!is->vcodec)
	{
		fprintf(stderr, "vcodec not found\n");
		exit(1);
	}

	/* open it */
	if (avcodec_open2(is->ac, is->acodec, 0) < 0)
	{
		fprintf(stderr, "could not open acodec\n");
		exit(1);
	}
	if (avcodec_open2(is->vc, is->vcodec, 0) < 0)
	{
		fprintf(stderr, "could not open vcodec\n");
		exit(1);
	}

	AVIO_Init();

//    is->audioStream = stream_index;
	is->audio_st = c->streams[is->audioStream]; //pFormatCtx->streams[stream_index];
	is->audio_buf_size = 0;
	is->audio_buf_index = 0;

	memset(&is->audio_pkt, 0, sizeof(is->audio_pkt));
	memset(&is->audio_pkt_dec, 0, sizeof(is->audio_pkt_dec));
	packet_queue_init(&is->audioq);

	if (!(is->aframe = avcodec_alloc_frame()))
	{
		fprintf(stderr, "failed alloc avframe, out of memory\n");
		exit(1);
	}

	if (enable_audio)
	{
		AVIO_InitAudio(is->ac->channels, is->ac->sample_rate, 16, (void*) audio_callback);
		AVIO_PauseAudio(0);
	}

//	running = TRUE;
	is->quit = 0;
	frame = 0;

	/*
	 *  Main Loop
	 */
	while (is->quit == 0) //  && frame < 2000)
	{
		int got_audio_frame = 0;
		int len;

		// Read Frame
		if (is->audioq.size > MAX_AUDIOQ_SIZE) // || is->videoq.size > MAX_VIDEOQ_SIZE)
		{
			SDL_Delay(10);
			logd("audioq overflow!\n");
			continue;
		}

		if (av_read_frame(c, packet) >= 0)
		{
			//Tommy: notice, packet  must be freed with av_free_packet after used.
			// Is this a packet from the video stream?
			if (packet->stream_index == is->videoStream)
			{
//					packet_queue_put(&is->videoq, packet);
				logd("get video stream %d bytes.\n", packet->size);
				av_free_packet(packet);
			}
			else if (packet->stream_index == is->audioStream)
			{
				logd("get audio stream %d bytes.\n", packet->size);
				packet_queue_put(&is->audioq, packet);
			}
			else
			{
				av_free_packet(packet);
			}
		}
		else
		{
			is->quit = 1;
		}
#if 0
		// VIDEO OUT
		if (0)
		{
			int got_picture;

			// Prepare Packets.
			if (vinpkt.size > 0 && (vinpkt.size + vpkt.size) < VIDEO_INBUF_SIZE)
			{
				logd("prepare video packet, before:%d, after:%d.\n",
						vpkt.size, (vpkt.size +vinpkt.size));
				memmove(videoinbuf, vpkt.data, vpkt.size);
				vpkt.data = videoinbuf;
				memcpy(videoinbuf + vpkt.size, vinpkt.data, vinpkt.size);
				vpkt.size += vinpkt.size;
				vinpkt.size = 0;
				read_new_video_frame = TRUE;
			}

			if (vpkt.size > 0 && pic_displayed)
			{
				len = avcodec_decode_video2(vc, picture, &got_picture, &vpkt);
				if (len < 0)
				{
					fprintf(stderr, "Error while decoding frame %d\n", frame);
					exit(1);
				}

				vpkt.size -= len;
				vpkt.data += len;

				logd("vpkt pts:%lld, dts:%lld, \n ", vpkt.pts, vpkt.dts);logd("pkt_pts:%lld, %lld, av_gettime:%lld\n ", picture->pkt_pts, picture->pkt_dts, av_gettime());
				if (got_picture)
				{
					/* the picture is allocated by the decoder. no need to
					 free it */
					if (frame == 0)
					{
						logd("yuv420 save: w:%d, h:%d, linesize:%d,%d,%d\n",
								picture->width, picture->height,
								picture->linesize[0], picture->linesize[1],
								picture->linesize[2]);
					}
					if (enable_video)
					{
						if (got_video_info == 0)
						{
							AVIO_InitYUV420(picture->width, picture->height, filename);
							got_video_info = 1;
						}
						SDL_AddTimer(33, sdl_refresh_timer_cb, 0);
						pic_displayed = 0;
//						AVIO_ShowYUV420(picture->data, picture->linesize, picture->width, picture->height, 0);
//						SDL_Delay(1);
					}
					frame++;
				}

			}

		}
#endif
		// AUDIO OUT
#if 0
		if (0)
		{
			// Prepare Packets.
			// Input buffer need padding zeros FF_INPUT_BUFFER_PADDING_SIZE. check tutorial for help on this.
			if (ainpkt.size > 0 && (ainpkt.size + apkt.size) < AUDIO_INBUF_SIZE)
			{
//			log("prepare audio packet, before:%d, after:%d.\n",
//					apkt.size, (apkt.size +ainpkt.size));
				memmove(audioinbuf, apkt.data, apkt.size);
				apkt.data = audioinbuf;
				memcpy(audioinbuf + apkt.size, ainpkt.data, ainpkt.size);
				apkt.size += ainpkt.size;
				ainpkt.size = 0;
				read_new_audio_frame = TRUE;
			}

			// Decode Audio
			if (apkt.size > 0)
			{
				avcodec_get_frame_defaults(dec_aframe);
				got_audio_frame = 0;
				len = avcodec_decode_audio4(ac, dec_aframe, &got_audio_frame, &apkt);
				if (len <= 0)
				{
//				log("audio avpkt.size  %d bytes left.\n", apkt.size);
					log( "Error while audio decoding\n");
					if (audio_ending == TRUE)
					{
						apkt.size = 0;
						break;
					}

					// Skip error. as libmad.
					if (ac->codec_id == CODEC_ID_MP3)
					{
						apkt.size -= 1;
						apkt.data += 1;
						continue;
					}
					else
					{ // skip this packet. copy from ffplay.c
						apkt.size = 0;
					}
				}

				if (got_audio_frame)
				{
					// remove the used data.
					apkt.size -= len;
					apkt.data += len;

					if (enable_audio)
					{
						if (got_audio_info == 0)
						{
							char fmt_str[128] = "";
							log(
									"audio stream: ch:%d, srate:%d, samples:%d, fmt:%s\n",
									ac->channels, ac->sample_rate, dec_aframe->nb_samples, av_get_sample_fmt_string(fmt_str, sizeof(fmt_str), ac->sample_fmt));

							AVIO_InitAudio(ac->channels, ac->sample_rate, 0, (void*) audio_mixer);
							AVIO_PauseAudio(0);
							AVIO_ShowYUV420(picture->data, picture->linesize, picture->width, picture->height, 0);
							got_audio_info = 1;
						}

						/* if a frame has been decoded, output it */
						int data_size = av_samples_get_buffer_size(NULL, ac->channels, dec_aframe->nb_samples,
								ac->sample_fmt, 1);
						logd("get decoded pcm data %d bytes. \n", data_size);

						if (ac->sample_fmt != AV_SAMPLE_FMT_S16)
						{ // Need format convert, check swr_convert() for details.
							struct SwrContext *swr_ctx;
							unsigned char swr_tmpbuff[AUDIO_OUTBUF_SIZE];
							int len2;
							unsigned char *in[] =
							{	dec_aframe->data[0]};
							unsigned char *out[] =
							{	swr_tmpbuff};

							logd("enter resample !\n");
							swr_ctx = swr_alloc_set_opts(NULL, ac->channel_layout, AV_SAMPLE_FMT_S16, ac->sample_rate,
									ac->channel_layout, ac->sample_fmt, ac->sample_rate, 0, NULL);
							swr_init(swr_ctx);
							len2 = swr_convert(swr_ctx, out,
									sizeof(swr_tmpbuff) / ac->channels / av_get_bytes_per_sample(AV_SAMPLE_FMT_S16), in,
									dec_aframe->nb_samples);
							swr_free(&swr_ctx);
							logd("resample output %d samples.\n", len2);
							while (ringbuff_filldata(&rb_aout, swr_tmpbuff,
											len2 * ac->channels * av_get_bytes_per_sample(AV_SAMPLE_FMT_S16)) == 1)
							{ // Wait until some audio data used, and free some space in the output buffer.
								SDL_Delay(1);
							}
						}
						else
						{
							while (ringbuff_filldata(&rb_aout, dec_aframe->data[0], data_size) == 1)
							{ // Wait until some audio data used, and free some space in the output buffer.
								SDL_Delay(1);
							}
						}
					}

				}

			} // Audio
		}

#endif

		SDL_Event event;
		if (SDL_PollEvent(&event))
		{
			/* GLOBAL KEYS / EVENTS */
			switch (event.type)
			{
			case FF_REFRESH_EVENT:
//				AVIO_ShowYUV420(picture->data, picture->linesize, picture->width, picture->height, 0);
				pic_displayed = 1;
				break;
			case SDL_KEYDOWN:
				switch (event.key.keysym.sym)
				{
				case SDLK_ESCAPE:
					is->quit = 1;
					break;
				default:
					break;
				}
				break;

			case SDL_QUIT:
				is->quit = 1;
				break;
			}
		}
	}

	AVIO_Exit();

	av_free(is->aframe);
	avformat_free_context(c);


}

static void show_banner(int argc, char **argv)
{
	printf("ffplay lite Version %s by %s\t", VERSION, AUTHOR);
	printf("%sbuilt on %s %s \n", " ", __DATE__, __TIME__);
}

static void show_options(int argc, char **argv)
{
	printf("Options:\n");
	printf(" -i file		Input pcm file\n");
	printf(" -ch x			Channel number, default is 2.\n");
	printf(" -srate xxx		Sample Rate in Hz, default is 44100hz.\n");
	printf(" -bps xxx		Bits per Sample, 8/16(default)/24/32.\n");
	printf("\n");
}

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

int main(int argc, char **argv)
{
	const char *filename;

	show_banner(argc, argv);
	/* must be called before using avcodec lib */
//	avcodec_init();
	/* register all the codecs */
	avcodec_register_all();

// register all the format ?
	av_register_all();

	is = av_mallocz(sizeof(VideoState));

#if 0
	if (argc <= 1)
	{
		audio_encode_example("/tmp/test.mp2");
		audio_decode_example("/tmp/test.sw", "/tmp/test.mp2");

		video_encode_example("/tmp/test.h264", CODEC_ID_H264);
		video_encode_example("/tmp/test.mpg", CODEC_ID_MPEG1VIDEO);
		filename = "/tmp/test.mpg";
	}
	else
	{
		filename = argv[1];
	}

//    audio_decode_example("/tmp/test.sw", filename);
	video_decode_example("/tmp/test%d.pgm", filename);
#else
// Decode mp3 to pcm file.
//	audio_decode_example("./out.pcm", "/srv/stream/001.hero.mp3");
	//	audio_decode_example("./out.pcm", "/srv/stream/love_mv.mpg.audiostream");
	//	audio_decode_example("./out.pcm", "/home/tommy/Desktop/share/vs.mp4.audiostream.aac");

// Encode pcm to mpeg1 audio file.
//	audio_encode_example("./out.mp3", "./out.pcm");

// Decode pure mpeg1video stream file into yuv420 data file.
//	video_decode_example("/tmp/test%d.pgm", "./love_mv.mpeg1video");

// Demux av file into files.
//	avfile_demux_example("/srv/stream/love_mv.mpg", 0);
//	avfile_demux_example("/srv/stream/vs.mp4", 0);

// Playback av file using SDL.
//	avfile_playback_example("/srv/stream/love_mv.mpg", 1, 0);
	avfile_playback_example("/srv/stream/vs.mp4", 1, 0);
//	avfile_playback_example("/srv/stream/CSI.Season11.EP10_S-Files.rmvb", 0, 1);
//	avfile_playback_example("/srv/stream/VIDEO0001.3gp", 1, 1);

#endif

	printf("\nffplay lite exit.\n");
	return 0;
}
