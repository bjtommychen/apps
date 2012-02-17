#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "SDL.h"
#include "SDL_main.h"

#include "av_io.h"

/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/
//#define USE2YUVOVERLAY
//#define USERGBSURFACE

//#define DEBUG

#ifdef DEBUG
#define log(a, b...)	fprintf(stdout, "AVIO: "a, ##b)
#else
#define log(a, b...)
#endif

enum YUVFORMAT
{
	YUV_420 = 0, YUV_422,
};

#define TRUE 1
#define FALSE 0

/* SDL audio buffer size, in samples. Should be small to have precise
 A/V sync as SDL does not have hardware buffer fullness info. */
#define SDL_AUDIO_BUFFER_SIZE 1024

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
SDL_AudioSpec *desired, *obtained;
SDL_Surface *screen, *bitmap;
SDL_Overlay *overlay = 0;
SDL_Overlay *overlay1 = 0;

// Audio
int chNum = 2, SampleRate = 44100, Bits_per_Sample = 16;
int average;
int outputAudioabufferSize = 0;
unsigned char *abuff = NULL;

// Video

// RGB
#if 0   // RGB565
Uint32 bitmapbpp = 16;
Uint32 bitmaprmask = 0x0000F800;
Uint32 bitmapgmask = 0x000007E0;
Uint32 bitmapbmask = 0x0000001F;
#else   // RGB888
Uint32 bitmapbpp = 24;
Uint32 bitmaprmask = 0x00FF0000;
Uint32 bitmapgmask = 0x0000FF00;
Uint32 bitmapbmask = 0x000000FF;
#endif
Uint32 bitmapamask = 0x00000000;
Uint32 bitmapflags = 0;
int bitmapw = 320;
int bitmaph = 240;

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

//void (SDLCALL *callback)(void *userdata, Uint8 *stream, int len);
static void sdl_audio_callback(void *userdata, Uint8 *stream, int len)
{
	int (*filldata)(void*userdata, Uint8 *stream, int len);

	log("enter sdl_audio_callback().\n");
	filldata = userdata;
	(*filldata)(userdata, stream, len);
	log("leave sdl_audio_callback().\n");
}

static int avio_get_frame_yuv420(SDL_Overlay *overlay, char *data[], int linesize[], int xsize, int ysize)
{
	int x, y;
	unsigned char *src, *dst;

	// Y
	src = data[0];
	for (y = 0; y < ysize; y++)
	{
		dst = overlay->pixels[0] + overlay->pitches[0] * y;
		memcpy(dst, src, xsize);
		src += linesize[0];
	}

	// U
	src = data[1];
	for (y = 0; y < ysize / 2; y++)
	{
		dst = overlay->pixels[1] + overlay->pitches[1] * y;
		memcpy(dst, src, xsize / 2);
		src += linesize[1];
	}

	// V
	src = data[2];
	for (y = 0; y < ysize / 2; y++)
	{
		dst = overlay->pixels[2] + overlay->pitches[2] * y;
		memcpy(dst, src, xsize / 2);
		src += linesize[2];
	}

	return 0;
}

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

int AVIO_Init()
{
	if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_TIMER) < 0)
	{
		log("Unable to init SDL: %s\n", SDL_GetError());
		return 1;
	}log("AVIO init.\n");
	return 0;
}

int AVIO_Exit()
{
	//Audio
	if (abuff != 0)
		free(abuff);
	SDL_CloseAudio();

	//Video
	if (overlay)
		SDL_FreeYUVOverlay(overlay);

	SDL_Quit();
	return 0;
}

/*
 * Init SDL Audio, notice the callback setting.
 */
int AVIO_InitAudio(int ch, int srate, int bps, void *callback)
{
	/* setup audio */

	if (ch)
		chNum = ch;
	if (srate)
		SampleRate = srate;
	if (bps)
		Bits_per_Sample = bps;

	log("Init SDL Audio, ch:%d, srate:%d, bps:%d\n", chNum, SampleRate, Bits_per_Sample);

	/* Allocate a desired SDL_AudioSpec */
	desired = (SDL_AudioSpec *) malloc(sizeof(SDL_AudioSpec));

	/* Allocate space for the obtained SDL_AudioSpec */
	obtained = (SDL_AudioSpec *) malloc(sizeof(SDL_AudioSpec));

	/* choose a samplerate and audio-format */
	desired->freq = SampleRate; //8000;//44100;

	if (Bits_per_Sample == 16)
		desired->format = AUDIO_S16LSB;
	else
	{
		Bits_per_Sample = 8;
		desired->format = AUDIO_S8;
	}

	/* Large audio abuffers reduces risk of dropouts but increases response time.

	 * You should always check if you actually GOT the audioabuffer size you wanted,
	 * note that not hardware supports all abuffer sizes (< 2048 bytes gives problems with some
	 * hardware). Older versions of SDL had a bug that caused many configuration to use a
	 * abuffersize of 11025 bytes, if your sdl.dll is approx. 1 Mb in stead of 220 Kb, download
	 * v1.2.8 of SDL or better...)
	 */
	desired->samples = SDL_AUDIO_BUFFER_SIZE;

	/* Our callback function */
	desired->callback = callback; //sdl_audio_callback;
	desired->userdata = 0; //callback;

	desired->channels = chNum;

	/* Open the audio device and start playing sound! */
	if (SDL_OpenAudio(desired, obtained) < 0)
	{
		log("AudioMixer, Unable to open audio: %s\n", SDL_GetError());
//		SDL_Quit();
		return (1);
	}

	log("Obtained samples:%d, freq:%dHz, channel:%d \n", obtained->samples, obtained->freq, obtained->channels);
	log( "Obtained->format: %s %d bits\n",
			(obtained->format & 0x8000) ? "signed":"unsigned", (obtained->format & 0x00ff));

	/* if the format is 16 bit, two bytes are written for every sample */
	if (obtained->format == AUDIO_U8 || obtained->format == AUDIO_S8)
	{
		outputAudioabufferSize = obtained->samples;
	}
	else
	{
		outputAudioabufferSize = obtained->samples * 2;
	}

	if (obtained->channels == 2)
		outputAudioabufferSize *= 2;

//	abuff = (unsigned char *) malloc(outputAudioabufferSize + 10);
//	if (abuff == 0)
//	{
//		log("Can't alloc mem for abuff.\n");
//		return (1);
//	}

//	SDL_Pause?Audio(0);
//	while (1)
	{
//		SDL_Delay(1);
	}

	return 0;
}

int AVIO_PauseAudio(int pause)
{
	log("PauseAudio %d\n", pause);
	SDL_PauseAudio(pause);
//	SDL_Delay(1);
	return 0;
}

/*
 * w, h is the overlay size
 */
int AVIO_InitYUV420(int w, int h, char *title)
{
	int i;
	char titlebar[255] = "";
	Uint32 video_flags, desired_bpp, overlay_format;

	video_flags = SDL_HWSURFACE | SDL_ASYNCBLIT | SDL_HWACCEL;
	if (0)
		video_flags |= SDL_FULLSCREEN;
	else
		video_flags |= SDL_RESIZABLE;
	desired_bpp = 0;

	/* Initialize the display */
#ifndef USE2YUVOVERLAY
	screen = SDL_SetVideoMode(w, h, desired_bpp, video_flags);
#else
	screen = SDL_SetVideoMode(w * 2, h * 2, desired_bpp, video_flags);
#endif

#ifdef USERGBSURFACE
	bitmap = SDL_CreateRGBSurface(bitmapflags, bitmapw, bitmaph, bitmapbpp,
			bitmaprmask, bitmapgmask, bitmapbmask, bitmapamask);
#endif

	if (screen == NULL)
	{
		fprintf(stderr, " Couldn 't set %dx%dx%d video mode: %s\n", w, h, desired_bpp, SDL_GetError());
		exit(1);
	}

	log( "Set%s %dx%dx%d mode\n",
			screen->flags & SDL_FULLSCREEN ? " fullscreen" : "", screen->w, screen->h, screen->format->BitsPerPixel);
	log("(video surface located in %s memory)\n", (screen->flags & SDL_HWSURFACE) ? "video" : "system");
	if (screen->flags & SDL_DOUBLEBUF)
	{
		log("Double-buffering enabled\n");
		//flip = 1;
	}

	/* Set the window manager title bar */
	strcpy(titlebar, "file: ");
	strcat(titlebar, title);
	SDL_WM_SetCaption(titlebar, "by tommy");

	/* Create the overlay */
	overlay_format = SDL_IYUV_OVERLAY; // YUYV
	overlay = SDL_CreateYUVOverlay(w, h, overlay_format, screen);
#ifdef USE2YUVOVERLAY
	overlay1 = SDL_CreateYUVOverlay(w, h, overlay_format, screen);
#endif

//	SDL_FillRect(screen, 0, SDL_MapRGB(screen->format, 0,55,0));

//	SDL_LockYUVOverlay(overlay);
	// SDL deault set YUV to green.
//	memset(overlay->pixels[0], 0,  overlay->pitches[0] * overlay->h);
//	memset(overlay->pixels[1], 128,  overlay->pitches[1] * overlay->h/2);
//	memset(overlay->pixels[2], 128,  overlay->pitches[2] * overlay->h/2);
//	SDL_UnlockYUVOverlay(overlay);

	/* show */
//	{
//		SDL_Rect rect;
//
//		rect.w = overlay->w;
//		rect.h = overlay->h;
//		rect.x = 0;
//		rect.y = 0;
//		SDL_DisplayYUVOverlay(overlay, &rect);
//	}
//
//	SDL_Delay(5000);
	log(
			"Created %dx%dx%d %s %s overlay\n",
			overlay->w, overlay->h, overlay->planes, overlay->hw_overlay ? "hardware" : "software", overlay->format == SDL_YV12_OVERLAY ? "YV12" : overlay->format == SDL_IYUV_OVERLAY ? "IYUV" : overlay->format == SDL_YUY2_OVERLAY ? "YUY2" : overlay->format == SDL_UYVY_OVERLAY ? "UYVY" : overlay->format == SDL_YVYU_OVERLAY ? "YVYU" : "Unknown");
	for (i = 0; i < overlay->planes; i++)
	{
		log("  plane %d: pitch=%d\n", i, overlay->pitches[i]);
	}

	return 0;
}

/*
 * xsize, ysize is the decoded yuv display size.
 */

int AVIO_ShowYUV420(char *data[], int linesize[], int xsize, int ysize, int format)
{
	SDL_LockYUVOverlay(overlay);

	switch (format)
	{
//	case YUV_420:
	default:
		avio_get_frame_yuv420(overlay, data, linesize, xsize, ysize);
		break;
	}

	SDL_UnlockYUVOverlay(overlay);

	/* show */
	{
		SDL_Rect rect;

		rect.w = overlay->w;
		rect.h = overlay->h;
		rect.x = 0;
		rect.y = 0;
		SDL_DisplayYUVOverlay(overlay, &rect);
	}

#ifdef USE2YUVOVERLAY
	SDL_LockYUVOverlay(overlay1);

	avio_get_frame_yuv420(overlay1, data, linesize, xsize, ysize);

	SDL_UnlockYUVOverlay(overlay1);

	{
		SDL_Rect rect;

		rect.w = overlay1->w;
		rect.h = overlay1->h;
		rect.x = overlay1->w;
		rect.y = overlay1->h;
		SDL_DisplayYUVOverlay(overlay1, &rect);
	}
#endif

#ifdef USERGBSURFACE

	{
		SDL_Rect rect;
		SDL_LockSurface(screen);

//		rect.w = bitmap->w;
//		rect.h = bitmap->h;
//		rect.x = 0;
//		rect.y = overlay->h;
//		SDL_FillRect(screen, &rect, SDL_MapRGB(bitmap->format, 0, 0, 0));

		rect.w = rand() % bitmap->w;
		rect.h = rand() % bitmap->h;
		rect.x = 0;
		rect.y = overlay->h;
		SDL_FillRect(screen, &rect, SDL_MapRGB(bitmap->format, rand()%255, rand()%255, rand()%255));

		SDL_UnlockSurface(screen);
//		SDL_UpdateRect(screen, 0, 0, 0, 0);
		rect.w = bitmap->w;
		rect.h = bitmap->h;
		SDL_UpdateRects(screen, 1, &rect);
	}
#endif

}

int AVIO_CheckESC()
{
	int bExit = FALSE;

	// Wait key input
	SDL_Event event;
	if (SDL_PollEvent(&event))
	{
		/* GLOBAL KEYS / EVENTS */
		switch (event.type)
		{
		case SDL_KEYDOWN:
			switch (event.key.keysym.sym)
			{
			case SDLK_ESCAPE:
				bExit = TRUE;
				break;
			default:
				break;
			}
			break;

		case SDL_QUIT:
			bExit = TRUE;
			break;
		}
	}

	return bExit;
}
