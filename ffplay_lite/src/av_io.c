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
#define DEBUG

#ifdef DEBUG
#define log(a, b...)	fprintf(stdout, "AVIO: "a, ##b)
#else
#define log(a, b...)
#endif

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
SDL_AudioSpec *desired, *obtained;
SDL_Surface *screen, *bitmap;

int chNum = 2, SampleRate = 44100, Bits_per_Sample = 16;
int average;
int outputAudioabufferSize = 0;
unsigned char *abuff;

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

//void (SDLCALL *callback)(void *userdata, Uint8 *stream, int len);
static void sdl_audio_callback(void *userdata, Uint8 *stream, int len)
{
	int i;
	int (*filldata)(Uint8 *stream, int len);

	log("enter sdl_audio_callback().\n");
	filldata = userdata;
	(*filldata)(stream, len);
	log("leave sdl_audio_callback().\n");
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
	}
	log("AVIO init.\n");
}

int AVIO_Exit()
{
	//Audio
	free(abuff);
	SDL_CloseAudio();

	//Video
	SDL_Quit();
}

int AVIO_InitAudio(int ch, int srate, int bps, void *callback)
{
	/* setup audio */

	if (ch)
		chNum = ch;
	if (srate)
		SampleRate = srate;
	if (bps)
		Bits_per_Sample = bps;

	log("Init SDL Audio, ch:%d, srate:%d, bps:%d\n",
			chNum, SampleRate, Bits_per_Sample);

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
	desired->samples = 2048;

	/* Our callback function */
	desired->callback = sdl_audio_callback;
	desired->userdata = callback;

	desired->channels = chNum;

	/* Open the audio device and start playing sound! */
	if (SDL_OpenAudio(desired, obtained) < 0)
	{
		log("AudioMixer, Unable to open audio: %s\n", SDL_GetError());
//		SDL_Quit();
		return (1);
	}

	log("Obtained samples:%d, freq:%dHz, channel:%d \n",
			obtained->samples, obtained->freq, obtained->channels);
	log(
			"Obtained->format: %s %d bits\n",
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

	abuff = (unsigned char *) malloc(outputAudioabufferSize + 10);
	if (abuff == 0)
	{
		log("Can't alloc mem for abuff.\n");
		return (1);
	}

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
