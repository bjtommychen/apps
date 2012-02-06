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

void Print_videoinfo();
void YUVshow_waitkey();

int main(int argc, char *argv[])
{
    SDL_Surface *screen, *pic;
    SDL_Overlay *overlay;
    int i, j, w=0, h, pitch, frames =1;
    int fileSize = 0;
    Uint32 video_flags, desired_bpp, overlay_format;
    FILE *fp;
    const SDL_VideoInfo *VideoInfo;
    int bytes_per_component = 1;        // 1: 8bit  2: 16bit
    int skip_bytes = 0;
    char titlebar[255] = "";

    printf(" YUV420show Version 1.00\n");

    if (argc < 4)
    {
        printf(" Usage: YUV420show yuvfile bytes_per_component(1,2) height [width:for frames] \n");
        exit(0);
    }

    if ((fp = fopen(argv[1], "rb")) == NULL)
    {
        fprintf(stderr, "can 't open %s\n", argv[1]);
        exit(1);
    }

    fileSize = filelength(fileno(fp));

    bytes_per_component=atoi(argv[2]);
    if (bytes_per_component != 1 && bytes_per_component !=2)
    {
        printf(" Error: must be 1 or 2 \n");
        exit(0);
    }


    h = atoi(argv[3]);
    if (argc > 4)
        w =atoi(argv[4]);

	//h = ((h+15)/16)*16;

    if (w == 0)
    {
        pitch = fileSize / h;
        w = 2 * pitch / (3 * bytes_per_component);
        skip_bytes = pitch - w*(3 * bytes_per_component);
        //pitch = w*(3 * bytes_per_component);
        printf("pitch %d , skip %d \n", pitch, skip_bytes);

    }
    else
    {
        pitch = 3 * w * bytes_per_component;
        frames = fileSize / (pitch * h);
    }

    printf("width %d , height %d , frames %d\n", w, h, frames);

        // width must be Even !!!
    if (w%2)
        w++;

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_NOPARACHUTE) < 0)
    {
        fprintf(stderr, "Couldn' t initialize SDL:%s \n ", SDL_GetError());
        return (1);
    }

    //Print_videoinfo();

    video_flags = 0;//SDL_HWSURFACE;
    desired_bpp = 0;

    /* Initialize the display */
    screen = SDL_SetVideoMode(w, h, desired_bpp, video_flags);
    if (screen == NULL)
    {
        fprintf(stderr, " Couldn 't set %dx%dx%d video mode: %s\n", w, h, desired_bpp, SDL_GetError());
        exit(1);
    }
    printf("Set%s %dx%dx%d mode\n",
           screen->flags & SDL_FULLSCREEN ? " fullscreen" : "",
           screen->w, screen->h, screen->format->BitsPerPixel);
    printf("(video surface located in %s memory)\n", (screen->flags & SDL_HWSURFACE) ? "video" : "system");
    if (screen->flags & SDL_DOUBLEBUF)
    {
        printf("Double-buffering enabled\n");
        //flip = 1;
    }

    /* Set the window manager title bar */
    strcpy(titlebar, "YUV420 show v1.0 - ");
    strcat(titlebar, argv[1]);
    SDL_WM_SetCaption(titlebar, "by tommy");

    /* Create the overlay */
    overlay_format = SDL_IYUV_OVERLAY;  // YUYV
    overlay = SDL_CreateYUVOverlay(w, h, overlay_format, screen);

    printf("Created %dx%dx%d %s %s overlay\n", overlay->w, overlay->h, overlay->planes,
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
    bytes_per_component --;
    while(j--)
    {
    {
        int x, y, len, i;
        unsigned char *p;
        Uint8 *op[3];
        unsigned char buff[150000];
        int tempu, tempv;

        SDL_LockYUVOverlay(overlay);

        for (y = 0; y < h; y++)
        {
            if (!fread(buff, overlay->pitches[0], 1, fp))
            {
                printf(" file end !\n");
                break;
            }

            op[0] = overlay->pixels[0] + overlay->pitches[0] * y;
            p = buff;
            for (x = 0; x < w; x++)
            {
                // IYUV,
                *(op[0]++) = *p++;     //y
                p+=bytes_per_component;
            }
        }


        for (y = 0; y < h; y++)
        {
            if (!fread(buff, overlay->pitches[1], 1, fp))
            {
                printf(" file end !\n");
                break;
            }

            op[1] = overlay->pixels[1] + overlay->pitches[1] * y;
            p = buff;
            for (x = 0; x < w; x++)
            {
                // IYUV,
                *(op[1]++) = *p++;     //y
                p+=bytes_per_component;
            }
        }

        for (y = 0; y < h; y++)
        {
            if (!fread(buff, overlay->pitches[2], 1, fp))
            {
                printf(" file end !\n");
                break;
            }

            op[2] = overlay->pixels[2] + overlay->pitches[2] * y;
            p = buff;
            for (x = 0; x < w; x++)
            {
                // IYUV,
                *(op[2]++) = *p++;     //y
                p+=bytes_per_component;
            }
        }


        SDL_UnlockYUVOverlay(overlay);
    }

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
    if (frames == 1)
        YUVshow_waitkey();
    else
        SDL_Delay(5 * 10);
    }
    SDL_Quit();
    return 0;
}

void Print_videoinfo()
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
    printf("Current display: %dx%d, %d bits-per-pixel\n",
           info->current_w, info->current_h, info->vfmt->BitsPerPixel);
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
    else if (modes == (SDL_Rect **) - 1)
    {
        printf("No special fullscreen video modes\n");
    }
    else
    {
        printf("Fullscreen video modes:\n");
        for (i = 0; modes[i]; ++i)
        {
            printf("\t%dx%dx%d\n", modes[i]->w, modes[i]->h, info->vfmt->BitsPerPixel);
        }
    }
    if (info->wm_available)
    {
        printf("A window manager is available\n");
    }
    if (info->hw_available)
    {
        printf("Hardware surfaces are available (%dK video memory)\n", info->video_mem);
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
        printf("Copy blits from software surfaces to hardware surfaces are accelerated\n");
    }
    if (info->blit_sw_CC)
    {
        printf("Colorkey blits from software surfaces to hardware surfaces are accelerated\n");
    }
    if (info->blit_sw_A)
    {
        printf("Alpha blits from software surfaces to hardware surfaces are accelerated\n");
    }
    if (info->blit_fill)
    {
        printf("Color fills on hardware surfaces are accelerated\n");
    }

}

void YUVshow_waitkey()
{
    int bRunning = 1;

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
