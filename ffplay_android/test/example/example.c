/*******************************************************************************
 *
 *    Template.c    -   Template source file
 *
 *    Copyright (c) 2012 Tommy
 *    All Rights Reserved.
 *
 *    Use of Tommy's code is governed by terms and conditions
 *    stated in the accompanying licensing statement.
 *
 *    Description:
 *
 *    Rivision Table
 * ------------------------------------------------------------------------------
 *    Name            Date            Summary
 * ------------------------------------------------------------------------------
 *    Tommy  2/27/2012  created this file.
 *
 *	$Id$
 *******************************************************************************/
#include "libffplay_ndk.h"

/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/
#define APPNAME "ffplay_android"
#define VERSION "0.01"
#define AUTHOR "Tommy"

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/
static void show_libinfo(int argc, char **argv)
{
	printf("%s version %s by %s\t", APPNAME, VERSION, AUTHOR);
	printf("%sbuilt on %s %s \n", " ", __DATE__, __TIME__);
}

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/



/* Called from the main */
int main(int argc, char **argv)
{
//	show_libinfo(argc, argv);

//	show_banner(argc, argv, 0);

	FFNDK_init();
//	FFNDK_showlibinfo();

//	FFNDK_decode_video("/sdcard/srv/stream/love_mv.mpg.videostream", 0);
//	FFNDK_decode_video("/sdcard/srv/stream/BBC10m.videostream", 0);
//	FFNDK_decode_video("/sdcard/srv/stream/vs.mp4.videostream", 0);

//	FFNDK_demux_example("/sdcard/srv/stream/vs.mp4", 0);

//	FFNDK_decode_avfile("/sdcard/srv/stream/love_mv.mpg", 0);
//	FFNDK_decode_avfile("/sdcard/srv/stream/vs.mp4", 0);
//	FFNDK_decode_avfile("/sdcard/srv/stream/BBC-10m_1.mkv", 0);
	FFNDK_decode_avfile("/sdcard/srv/stream/VIDEO0001.3gp", 0);

	return 0;
}
