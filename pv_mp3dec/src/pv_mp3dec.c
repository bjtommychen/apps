//============================================================================
// Name        : pv_mp3dec.cpp
// Author      : ctao
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include "stdio.h"
#include "stdlib.h"
#include "string.h"

#include "pvmp3decoder_api.h"

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
#define VERSION "0.01"
#define AUTHOR "Tommy"

#define INPUT_BUFSZ				(1024*2)
#define OUTPUT_BUFSZ			(4608 * 2)
/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
FILE *fin, *fout;
char fin_name[256] = "/srv/stream/spring_mud.mp3";
char fout_name[256] = "out.pcm";
int chNum = 2, SampleRate = 44100, Bits_per_Sample = 16;

tPVMP3DecoderExternal *mConfig;
void *mDecoderBuf;

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

static void show_banner(int argc, char **argv)
{
	printf("PacketVideo_mp3dec version %s by %s.\t", VERSION, AUTHOR);
	printf("%sbuilt on %s %s \n", " ", __DATE__, __TIME__);
}

static void show_options(int argc, char **argv)
{
	printf("Options:\n");
	printf(" -i file		Input mp3 file\n");
	printf(" -o file		Output pcm file\n");
	printf("\n");
}

static void parse_options(int argc, char **argv)
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
					log("argv:%s\n", *argv);
					strcpy(fin_name, *argv);
					break;
				}
			}
			else
			{
				if (strcmp(p, "ch") == 0)
				{
//					argv++;
//					chNum = atoi(*argv);
				}
			}
		}
		argv++;
	}
	log("parse_options done.");
}

/*******************************************************************************************************************/

int main(int argc, char **argv)
{
	int loop = TRUE;
	int bEOF = FALSE;
	char *inbuf, *outbuf;
	int remainbytes = 0;

	show_banner(argc, argv);

	if (argc < 2)
	{
		show_options(argc, argv);
//		exit(0);
	}

	parse_options(argc, argv);

	printf("check parameter done.");

	if ((fin = fopen(fin_name, "rb")) == NULL)
	{
		printf(" Can't open input file.\n");
		exit(1);
	}

	if ((fout = fopen(fout_name, "wb")) == NULL)
	{
		printf(" Can't open output file.\n");
		fclose(fin);
		exit(1);
	}



	inbuf = malloc(INPUT_BUFSZ);
	outbuf = malloc(OUTPUT_BUFSZ);
	mConfig->equalizerType = flat;
	mConfig->crcEnabled = FALSE;
	uint32_t memRequirements = pvmp3_decoderMemRequirements();
	log("mem need %d bytes.\n", memRequirements);
	mDecoderBuf = malloc(memRequirements);
	pvmp3_InitDecoder(mConfig, mDecoderBuf);

	while (loop)
	{
		int readlen, len;
		ERROR_CODE decoderErr;

		readlen = INPUT_BUFSZ - remainbytes;
		len = fread(inbuf + remainbytes, 1, readlen, fin);
		log("fread %d bytes.\n", len);
		if (len < readlen)
			bEOF = TRUE;

		mConfig->pInputBuffer = inbuf;
		mConfig->inputBufferCurrentLength = INPUT_BUFSZ;
		mConfig->inputBufferMaxLength = 0;
		mConfig->inputBufferUsedLength = 0;
		mConfig->outputFrameSize = OUTPUT_BUFSZ / sizeof(int16_t);
		mConfig->pOutputBuffer = outbuf;

		if ((decoderErr = pvmp3_framedecoder(mConfig, mDecoderBuf)) != NO_DECODING_ERROR)
		{
			log("mp3 decoder returned error %d", decoderErr);
			if (bEOF == TRUE)
				loop = FALSE;
		}
		else
		{
			log("decode got %d samples .\n", mConfig->outputFrameSize);
			fwrite(outbuf, 1, mConfig->outputFrameSize * sizeof(int16), fout);
		}

		log("inputBufferUsedLength %d bytes.\n", mConfig->inputBufferUsedLength);
		remainbytes = INPUT_BUFSZ - mConfig->inputBufferUsedLength;
		memmove(inbuf, inbuf + mConfig->inputBufferUsedLength, remainbytes);
	}
	fclose(fin);
	fclose(fout);

	return 0;

}
