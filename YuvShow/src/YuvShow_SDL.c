/*
 ============================================================================
 Name        : YuvShow_SDL.c
 Author      : ctao
 Version     :
 Copyright   : Your copyright notice
 Description : Hello World in C, Ansi-style
 ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <SDL.h>

/******************************************************************************\
*  Externs
 \******************************************************************************/

/******************************************************************************\
*  Local Macro Definitions
 \******************************************************************************/
//#define DEBUG
#ifdef DEBUG
#define log(a, b...)    printf(a, ##b)
#else
#define log(a, b...)
#endif

#define TRUE 1
#define FALSE 0
#define VERSION "2.01"
#define AUTHOR "Tommy"


enum YUVFORMAT
{
    YUV_420 = 0, YUV_422, YUV_420_NV12, 
};

/******************************************************************************\
*  Local Type Definitions
 \******************************************************************************/
int bRunning = TRUE;
int w = 0, h = 0;
int format = YUV_420;
char filename[256] = "infile";

/******************************************************************************\
*  Local Variables
 \******************************************************************************/

/******************************************************************************\
*  Local Function Declarations
 \******************************************************************************/
static void show_banner(int argc, char **argv)
{
    printf("YUVshow Version %s by %s\t\t", VERSION, AUTHOR);
    printf("%sbuilt on %s %s \n", " ", __DATE__, __TIME__);

}

static void show_options(int argc, char **argv)
{
    printf("Options:\n");
    printf(" -i file			Input file\n");
    printf(" -w width		Width\n");
    printf(" -h height		Height\n");
    printf(" -fmt yuvformat		Specify the input YUV format\n");
    printf("	yuv420_iyuv: 8 bit Y plane followed by 8 bit 2x2 subsampled U and V planes.\n");
    printf("	yuv420_nv12: 8-bit Y plane followed by an interleaved U/V plane with 2x2 subsampling.\n");
    printf("	yuv422:	not implemented.			\n");
    printf("\n");
}

static void Print_videoinfo()
{
    const SDL_VideoInfo *info;
    int i;
    SDL_Rect **modes;
    char driver[128];

    if (SDL_VideoDriverName(driver, sizeof(driver)))
    {
        printf("Video driver: %s\n", driver);
    }
    info = SDL_GetVideoInfo();
    printf("Current display: %dx%d, %d bits-per-pixel\n", info->current_w,
           info->current_h, info->vfmt->BitsPerPixel);
    if (info->vfmt->palette == NULL)
    {
        printf("	Red Mask = 0x%.8x\n", info->vfmt->Rmask);
        printf("	Green Mask = 0x%.8x\n", info->vfmt->Gmask);
        printf("	Blue Mask = 0x%.8x\n", info->vfmt->Bmask);
    }
    /* Print available fullscreen video modes */
    modes = SDL_ListModes(NULL, SDL_FULLSCREEN);
    if (modes == (SDL_Rect **) 0)
    {
        printf("No available fullscreen video modes\n");
    }
    else if (modes == (SDL_Rect **) -1)
    {
        printf("No special fullscreen video modes\n");
    }
    else
    {
        printf("Fullscreen video modes:\n");
        for (i = 0; modes[i]; ++i)
        {
            printf("\t%dx%dx%d\n", modes[i]->w, modes[i]->h,
                   info->vfmt->BitsPerPixel);
        }
    }
    if (info->wm_available)
    {
        printf("A window manager is available\n");
    }
    if (info->hw_available)
    {
        printf("Hardware surfaces are available (%dK video memory)\n",
               info->video_mem);
    }
    if (info->blit_hw)
    {
        printf("Copy blits between hardware surfaces are accelerated\n");
    }
    if (info->blit_hw_CC)
    {
        printf("Colorkey blits between hardware surfaces are accelerated\n");
    }
    if (info->blit_hw_A)
    {
        printf("Alpha blits between hardware surfaces are accelerated\n");
    }
    if (info->blit_sw)
    {
        printf(
            "Copy blits from software surfaces to hardware surfaces are accelerated\n");
    }
    if (info->blit_sw_CC)
    {
        printf(
            "Colorkey blits from software surfaces to hardware surfaces are accelerated\n");
    }
    if (info->blit_sw_A)
    {
        printf(
            "Alpha blits from software surfaces to hardware surfaces are accelerated\n");
    }
    if (info->blit_fill)
    {
        printf("Color fills on hardware surfaces are accelerated\n");
    }

}

static void YUVshow_waitkey()
{
    bRunning = 1;

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
                            bRunning = 0;
                            break;
                        default:
                            break;
                    }
                    break;

                case SDL_QUIT:
                    bRunning = 0;
                    break;
            }
            SDL_Delay(1);
        }
        SDL_Delay(1);
    }

}

static int check_exit_key()
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
                bRunning = 0;
                break;
        }
    }

    return bExit;
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
                    case 'w':
                        argv++;
                        w = atoi(*argv);
                        break;
                    case 'h':
                        argv++;
                        h = atoi(*argv);
                        break;
                }
            }
            else
            {
                if (strcmp(p, "fmt") == 0)
                {
//                  log("get fmt\n");
                    argv++;
                    if (strcmp(*argv, "yuv420_nv12")==0)
                        format = YUV_420_NV12;
                    if (strcmp(*argv, "yuv420_iyuv")==0)
                        format = YUV_420;
                    if (strcmp(*argv, "yuv422")==0)
                        format = YUV_422;

                    
                }
            }
        }
        argv++;
    }
}

static int get_framesize_in_bytes(int w, int h, int format)
{
    int size = 0;

    switch (format)
    {
        case YUV_420:
        case YUV_420_NV12:
            size = w * h * 3 / 2;
            break;
        case YUV_422:
            size = w * h * 2;
            break;
    }
    return size;
}

// Return 1 if reach end of file.
static int get_frame_yuv422(FILE *fp, SDL_Overlay *overlay)
{
    int x, y;
    unsigned char *p, *dst;
    unsigned char buff[150000];


//  log("ready to YUV\n");
    // Y
    for (y = 0; y < h; y++)
    {
        if (!fread(buff, overlay->pitches[0], 1, fp))
        {
            return 1;
        }

//      log("do Y\n");
        dst = overlay->pixels[0] + overlay->pitches[0] * y;
        p = buff;
        for (x = 0; x < w; x++)
        {
            // IYUV,
            *dst++ = *p++; //y
        }
    }

    // U
    for (y = 0; y < h / 2; y++)
    {
        if (!fread(buff, overlay->pitches[1], 1, fp))
        {
            return 1;
        }

//      log("do U\n");
        dst = overlay->pixels[1] + overlay->pitches[1] * y;
        p = buff;
        for (x = 0; x < w; x++)
        {
            // IYUV,
            *dst++ = *p++; //y
        }
    }

    // V
    for (y = 0; y < h / 2; y++)
    {
        if (!fread(buff, overlay->pitches[2], 1, fp))
        {
            return 1;
        }

        dst = overlay->pixels[2] + overlay->pitches[2] * y;
        p = buff;
        for (x = 0; x < w; x++)
        {
            // IYUV,
            *dst++ = *p++; //y
        }
    }

    return 0;
}


static int get_frame_yuv420(FILE *fp, SDL_Overlay *overlay)
{
    int x, y;
    unsigned char *p, *dst;
    unsigned char buff[150000];


//  log("ready to YUV\n");
    // Y
    for (y = 0; y < h; y++)
    {
        if (!fread(buff, overlay->pitches[0], 1, fp))
        {
            return 1;
        }

//      log("do Y\n");
        dst = overlay->pixels[0] + overlay->pitches[0] * y;
        p = buff;
        for (x = 0; x < overlay->pitches[0]; x++)
        {
            // IYUV,
            *dst++ = *p++; //y
        }
    }

    // U
    for (y = 0; y < h /2; y++)
    {
        if (!fread(buff, overlay->pitches[1], 1, fp))
        {
            return 1;
        }

        //printf("do U\n");
        dst = overlay->pixels[1] + overlay->pitches[1] * y;
        p = buff;
        for (x = 0; x < overlay->pitches[1]; x++)
        {
            // IYUV,
            *dst++ = *p++; //y
        }
    }


    // V
    for (y = 0; y < h / 2; y++)
    {
        if (!fread(buff, overlay->pitches[2], 1, fp))
        {
            return 1;
        }

        dst = overlay->pixels[2] + overlay->pitches[2] * y;
        p = buff;
        for (x = 0; x < overlay->pitches[2]; x++)
        {
            // IYUV,
            *dst++ = *p++; //y
        }
    }

    return 0;
}


static int get_frame_yuv420_nv12(FILE *fp, SDL_Overlay *overlay)
{
    int x, y;
    unsigned char *p, *dst, *dst2;
    unsigned char buff[150000];

//    printf(" get_frame_yuv420_nv12. ");

//  log("ready to YUV\n");
    // Y
    for (y = 0; y < h; y++)
    {
        if (!fread(buff, overlay->pitches[0], 1, fp))
        {
            return 1;
        }

//      log("do Y\n");
        dst = overlay->pixels[0] + overlay->pitches[0] * y;
        p = buff;
        for (x = 0; x < overlay->pitches[0]; x++)
        {
            // IYUV,
            *dst++ = *p++; //y
        }
    }

    // UV
    for (y = 0; y < h /2; y++)
    {
        if (!fread(buff, overlay->pitches[1]*2, 1, fp))
        {
            return 1;
        }

        dst = overlay->pixels[1] + overlay->pitches[1] * y;
        dst2= overlay->pixels[2] + overlay->pitches[2] * y;
        p = buff;
        for (x = 0; x < overlay->pitches[1]; x++)
        {
            // IYUV,
            *dst++ = *p++; //y
            *dst2++ = *p++; //y
        }
    }

    return 0;
}


/******************************************************************************\
*  Function Definitions
 \******************************************************************************/

int main(int argc, char *argv[])
{
    SDL_Surface *screen;
    SDL_Overlay *overlay;
    int i, j, frames = 1;
    int fileSize = 0;
    Uint32 video_flags, desired_bpp, overlay_format;
    FILE *fp;
//  const SDL_VideoInfo *VideoInfo;
    int bytes_per_component = 1; // 1: 8bit  2: 16bit
    char titlebar[255] = "";

// Show info & Get arguments.
    show_banner(argc, argv);

    if (argc < 2)
    {
        show_options(argc, argv);
        exit(0);
    }

    parse_options(argc, argv);

// Checking arguments
    if (w == 0 || h == 0)
        exit(0);

// Open file
    if ((fp = fopen(filename, "rb")) == NULL)
    {
        fprintf(stderr, "can 't open %s\n", filename);
        exit(1);
    }

// Get file size
    fseek(fp, 0, SEEK_END);
    fileSize = ftell(fp);
    fseek(fp, 0, SEEK_SET);

//  bytes_per_component = 1; //atoi(argv[2]);
//  if (bytes_per_component != 1 && bytes_per_component != 2)
//  {
//      printf(" Error: must be 1 or 2 \n");
//      exit(0);
//  }

//  h = atoi(argv[3]);
//  if (argc > 4)
//      w = atoi(argv[4]);

//h = ((h+15)/16)*16;

//  if (w == 0)
//  {
//      pitch = fileSize / h;
//      w = 2 * pitch / (3 * bytes_per_component);
//      skip_bytes = pitch - w * (3 * bytes_per_component);
//      //pitch = w*(3 * bytes_per_component);
//      printf("pitch %d , skip %d \n", pitch, skip_bytes);
//
//  }
//  else
//  {
//      pitch = /*3*/1.5 * w * bytes_per_component;
//      frames = fileSize / (pitch * h);
//  }

    if (get_framesize_in_bytes(w, h, format))
        frames = fileSize / get_framesize_in_bytes(w, h, format);

    printf("width %d , height %d , frames %d\n", w, h, frames);
	if (frames == 0)
		frames = 1;
//  getchar();
//  exit(0);

// width must be Even !!!
    if (w % 2)
        w++;

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER | SDL_INIT_NOPARACHUTE) < 0)
    {
        fprintf(stderr, "Couldn' t initialize SDL:%s \n ", SDL_GetError());
        return (1);
    }

//  Print_videoinfo();

    video_flags = SDL_HWSURFACE | SDL_ASYNCBLIT | SDL_HWACCEL;
    if (0)
        video_flags |= SDL_FULLSCREEN;
    else
        video_flags |= SDL_RESIZABLE;
    desired_bpp = 0;

    /* Initialize the display */
    screen = SDL_SetVideoMode(w, h, desired_bpp, video_flags);
    if (screen == NULL)
    {
        fprintf(stderr, " Couldn 't set %dx%dx%d video mode: %s\n", w, h,
                desired_bpp, SDL_GetError());
        exit(1);
    }
    printf("Set%s %dx%dx%d mode\n",
           screen->flags & SDL_FULLSCREEN ? " fullscreen" : "", screen->w,
           screen->h, screen->format->BitsPerPixel);
    printf("(video surface located in %s memory)\n",
           (screen->flags & SDL_HWSURFACE) ? "video" : "system");
    if (screen->flags & SDL_DOUBLEBUF)
    {
        printf("Double-buffering enabled\n");
        //flip = 1;
    }

    /* Set the window manager title bar */
    strcpy(titlebar, "file: ");
    strcat(titlebar, filename);
    SDL_WM_SetCaption(titlebar, "by tommy");

    /* Create the overlay */
#if 0
#define SDL_YV12_OVERLAY  0x32315659  /* Planar mode: Y + V + U */
#define SDL_IYUV_OVERLAY  0x56555949  /* Planar mode: Y + U + V */
#define SDL_YUY2_OVERLAY  0x32595559  /* Packed mode: Y0+U0+Y1+V0 */
#define SDL_UYVY_OVERLAY  0x59565955  /* Packed mode: U0+Y0+V0+Y1 */
#define SDL_YVYU_OVERLAY  0x55595659  /* Packed mode: Y0+V0+Y1+U0 */

I420	0x30323449	12	8 bit Y plane followed by 8 bit 2x2 subsampled U and V planes.
IYUV	0x56555949	12	Duplicate FOURCC, identical to I420.
NV12	0x3231564E	12	8-bit Y plane followed by an interleaved U/V plane with 2x2 subsampling
http://www.fourcc.org/yuv.php

#endif
    overlay_format =  SDL_IYUV_OVERLAY; // YUYV
    overlay = SDL_CreateYUVOverlay(w, h, overlay_format, screen);

    printf(
        "Created %dx%dx%d %s %s overlay\n",
        overlay->w,
        overlay->h,
        overlay->planes,
        overlay->hw_overlay ? "hardware" : "software",
        overlay->format == SDL_YV12_OVERLAY ? "YV12" :
        overlay->format == SDL_IYUV_OVERLAY ? "IYUV" :
        overlay->format == SDL_YUY2_OVERLAY ? "YUY2" :
        overlay->format == SDL_UYVY_OVERLAY ? "UYVY" :
        overlay->format == SDL_YVYU_OVERLAY ? "YVYU" : "Unknown");
    for (i = 0; i < overlay->planes; i++)
    {
        printf("  plane %d: pitch=%d\n", i, overlay->pitches[i]);
    }

////////////////////// Draw start ////////////////////////////////
    j = frames;
    i = 0;
//  j = 10;
    bytes_per_component--;
    while (j-- && bRunning)
    {
//      printf("frame no. %d/%d, format: %d \n", i++, frames, format);
        SDL_LockYUVOverlay(overlay);

        switch (format)
        {
            case YUV_420:
                get_frame_yuv420(fp, overlay);
                break;

            case YUV_420_NV12:
                get_frame_yuv420_nv12(fp, overlay);
                break;

            case YUV_422:
                get_frame_yuv422(fp, overlay);
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

////////////////////// Draw end ////////////////////////////////
        if (frames < 2)
            YUVshow_waitkey();
        else
//          SDL_Delay(5 * 10);
            SDL_Delay(33);
        if (check_exit_key())
            bRunning = FALSE;
    }

    fclose(fp);
    SDL_FreeYUVOverlay(overlay);
    SDL_Quit();
    return 0;
}

