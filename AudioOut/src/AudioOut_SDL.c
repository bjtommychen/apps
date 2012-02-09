/*
 ============================================================================
 Name        : AudioOut_SDL.c
 Author      : ctao
 Version     :
 Copyright   : Your copyright notice
 Description : Hello World in C, Ansi-style
 ============================================================================
 */

// AudioOut.cpp : Defines the entry point for the application.
//
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "SDL.h"
#include "SDL_main.h"

/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/
#define DEBUG
#ifdef DEBUG
#define log(a, b...)	printf(a, ##b)
#else
#define log(a, b...)
#endif

#define TRUE 1
#define FALSE 0
#define VERSION "2.00"
#define AUTHOR "Tommy"

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
int bRunning = TRUE;

unsigned int outputAudioBufferSize = 0;
char filename[256] = "infile";
int bytes_per_component;
int chNum = 2, SampleRate = 44100, Bits_per_Sample = 16;
SDL_Surface *screen, *bitmap;
int average;

FILE *fp;
unsigned char *buff;
int bMixAudioEntered = FALSE;

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

static void show_banner(int argc, char **argv)
{
	printf("AudioOut Version %s by %s\t\t", VERSION, AUTHOR);
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

static void parse_options(int argc, char *argv[])
{
	int i;
	char *p;

	argv++;
	for (i = 1; i < argc && *argv != NULL; i++)
	{
		log("No.%d, checking %s\n", i, *argv);
		p = *argv;
		if (*p == '-')
		{
			p++;
			if (strlen(p) == 1)
			{
				switch (*p)
				{
				case 'i':
					argv++;
					strcpy(filename, *argv);
					break;
				}
			}
			else
			{
				if (strcmp(p, "ch") == 0)
				{
					argv++;
					chNum = atoi(*argv);
				}
				if (strcmp(p, "srate") == 0)
				{
					argv++;
					SampleRate = atoi(*argv);
				}
				if (strcmp(p, "bps") == 0)
				{
					argv++;
					Bits_per_Sample = atoi(*argv);
				}

			}
		}
		argv++;
	}
}

static draw_average_point()
{
	static x=0;
	SDL_Rect rect;

	if(x>=bitmapw)
		x=0;


	SDL_LockSurface(screen);

	rect.w = 1;
	rect.h = bitmaph;
	rect.x=x;
	rect.y=0;
	SDL_FillRect(screen, &rect, SDL_MapRGB(bitmap->format, 0,0,0));

	rect.w = rect.h = 1;
	rect.x=x;
	rect.y=(bitmaph-1)*(1.0 - (float)average/(65536.0/2));
	SDL_FillRect(screen, &rect, SDL_MapRGB(bitmap->format, 180,0,0));

	SDL_UnlockSurface(screen);
	SDL_UpdateRect(screen, 0, 0, 0, 0);
	x++;
}


static int get_audio_average(Sint16 *p, int len)
{
	Uint32 sum = 0;
	int i;
	for (i = 0; i < len / 2; i++)
		sum += abs(*p++);
	return (sum / (len / 2));
}

//#define AudioOutTitle "AudioOut Version 1.00 -Press ESC to quit !"

/* linker options: -lmingw32 -lSDLmain -lSDL -mwindows */

/* This function is called when the audio device needs more data.
 'stream' is a pointer to the audio data buffer
 'len' is the length of that buffer in bytes.
 Once the callback returns, the buffer will no longer be valid.
 Stereo samples are stored in a LRLRLR ordering.
 */
static void mixaudio(void *usr_used, Uint8 * stream, int len)
{

	int i;
//	int ch0, ch1;
//	Uint16 outputValue;
	Uint16 *p16out = (Uint16 *) stream;
	Uint16 *pSrc16 = (Uint16 *) buff;

	if (!fread(buff, len, 1, fp))
	{
		printf("\n file end !\n");
		bRunning = FALSE;
		return;
	}
	else if (bMixAudioEntered == FALSE)
	{
		bMixAudioEntered = TRUE;
		printf(" mixaudio Read %d bytes \n", len);
	}
	else
	{
//		printf(".");
	}

	average = get_audio_average(buff, len);
//	printf(" average is %d\n", average);
	draw_average_point();

	if (Bits_per_Sample == 16)
	{
		for (i = 0; i < len / 2; i++)
		{
			p16out[i] = pSrc16[i];
		}
	}
	else
	{
		for (i = 0; i < len; i++)
		{
			stream[i] = buff[i];
		}
	}
}



/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

int main(int argc, char *argv[])
{

	int fileSize = 0;

// Show info & Get arguments.
	show_banner(argc, argv);
	parse_options(argc, argv);

	if (argc < 2)
	{
		//printf(" Usage: AudioOut pcmfile channel(1,2) samplerate(Hz) bits_per_sample(8,16) \n");
		show_options(argc, argv);
		exit(0);
	}

	if ((fp = fopen(filename, "rb")) == NULL)
	{
		fprintf(stderr, "can 't open %s\n", filename);
		exit(1);
	}

//    chNum = atoi(argv[2]);
//    SampleRate = atoi(argv[3]);
//    Bits_per_Sample = atoi(argv[4]);

// Get file size
	fseek(fp, 0, SEEK_END);
	fileSize = ftell(fp);
	fseek(fp, 0, SEEK_SET);

	if (SDL_Init(SDL_INIT_TIMER | SDL_INIT_AUDIO) < 0)
	{
		//cout << "Unable to init SDL: " << SDL_GetError() << endl;
		printf("Unable to init SDL: %s\n", SDL_GetError());
		return 1;
	}

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
		exit(1);
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

	/* Show a window */
	screen = SDL_SetVideoMode(bitmapw, bitmaph, bitmapbpp, bitmapflags);
	bitmap = SDL_CreateRGBSurface(bitmapflags, bitmapw, bitmaph, bitmapbpp,
			bitmaprmask, bitmapgmask, bitmapbmask, bitmapamask);

	SDL_WM_SetCaption((filename), 0);

	// Play Audio start
	SDL_Delay(1000);
	printf("\nStart to play ... ");
	SDL_PauseAudio(0);

	// Wait key input
	SDL_Event event;
	while (bRunning)
	{
		while (SDL_PollEvent(&event))
		{

			/* GLOBAL KEYS / EVENTS */
			switch (event.type)
			{
			case SDL_KEYDOWN:
				switch (event.key.keysym.sym)
				{
				case SDLK_ESCAPE:
					bRunning = FALSE;
					break;
				default:
					break;
				}
				break;

			case SDL_QUIT:
				bRunning = FALSE;
				break;
			}
			SDL_Delay(1);
		}
		SDL_Delay(1);
	}

	printf("\nEnd!\n ");

	SDL_FreeSurface(screen);
	SDL_FreeSurface(bitmap);

	SDL_CloseAudio();
	SDL_Quit();

	free(buff);

	return EXIT_SUCCESS;

}

