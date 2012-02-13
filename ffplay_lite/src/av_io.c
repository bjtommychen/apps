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
#define log(a, b...)	fprintf(stdout, a, ##b)
#else
#define log(a, b...)
#endif

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
int bytes_per_component;
int chNum = 2, SampleRate = 44100, Bits_per_Sample = 16;
SDL_Surface *screen, *bitmap;
int average;
int outputAudioBufferSize = 0;
unsigned char *buff;
/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/
static void mixaudio(void *usr_used, Uint8 * stream, int len)
{
	int i;
//	int ch0, ch1;
//	Uint16 outputValue;
	Uint16 *p16out = (Uint16 *) stream;
	Uint16 *pSrc16 = (Uint16 *) buff;

}


static int avio_init_audio()
{
	/* setup audio */
	SDL_AudioSpec *desired, *obtained;

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

	/* Large audio buffers reduces risk of dropouts but increases response time.

	 * You should always check if you actually GOT the audiobuffer size you wanted,
	 * note that not hardware supports all buffer sizes (< 2048 bytes gives problems with some
	 * hardware). Older versions of SDL had a bug that caused many configuration to use a
	 * buffersize of 11025 bytes, if your sdl.dll is approx. 1 Mb in stead of 220 Kb, download
	 * v1.2.8 of SDL or better...)
	 */
	desired->samples = 2048;

	/* Our callback function */
	desired->callback = mixaudio;
	desired->userdata = NULL;

	desired->channels = chNum;

	/* Open the audio device and start playing sound! */
	if (SDL_OpenAudio(desired, obtained) < 0)
	{
		printf("AudioMixer, Unable to open audio: %s\n", SDL_GetError());
		SDL_Quit();
		return(1);
	}

	printf(" Obtained samples:%d, freq:%dHz, channel:%d \n", obtained->samples,
			obtained->freq, obtained->channels);
	printf(
			" Obtained->format: %s %d bits\n",
			(obtained->format & 0x8000) ? "signed":"unsigned", (obtained->format & 0x00ff));

	/* if the format is 16 bit, two bytes are written for every sample */
	if (obtained->format == AUDIO_U8 || obtained->format == AUDIO_S8)
	{
		outputAudioBufferSize = obtained->samples;
	}
	else
	{
		outputAudioBufferSize = obtained->samples * 2;
	}

	if (obtained->channels == 2)
		outputAudioBufferSize *= 2;

	buff = (unsigned char *) malloc(outputAudioBufferSize + 10);
	if (buff == 0)
		exit(1);
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

}

int AVIO_Exit()
{
	SDL_CloseAudio();
	SDL_Quit();
}

