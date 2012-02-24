/*******************************************************************************
*
*    Template.h    -    Template header file
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
*    Name        Date        Summary
* ------------------------------------------------------------------------------
*    Tommy  2/27/2012  created this file.
*
*	$Id$	
*******************************************************************************/
  

/*!
 *  /file Template.h
 *  /brief 
*/
/* /mainpage Template Module Interface Specification
 *
 *  /section scope Scope
 *
 *  This document is used to introduce the application programming interface of AVI Demuxer of
 *
 *  /section license License
 *  Copyright (c) 2006 Tommy
 *  All Rights Reserved.
 *
 *  Use of Tommy Inc. Ltd. code is governed by terms and conditions
 *  stated in the accompanying licensing statement.
 */
 
/* /page author Authors
 *
 *  Here are authors of this software module
 *
 *  /section ctao Tommy Chen
 *  email: <B> <I> chen.tao.tommy@gmail.com </I> </B>.
 *
 */


#ifndef _FFPLAY_NDK_H_
#define _FFPLAY_NDK_H_

#ifdef __cplusplus
extern "C" {
#endif

//#include <xxxxxxxxxxxx.h>



/******************************************************************************/
/*  Macro Definitions                                                         */
/******************************************************************************/


/******************************************************************************/
/*  Type Definitions                                                          */
/******************************************************************************/


/******************************************************************************/
/*  Enums Definitions                                                         */
/******************************************************************************/


/******************************************************************************/
/*  Structures Definitions                                                    */
/******************************************************************************/


/******************************************************************************/
/*  Function Declarations                                                     */
/******************************************************************************/
int FFNDK_init();
int FFNDK_showlibinfo();
void FFNDK_decode_videostream(const char *filename, int write_output);
void FFNDK_demux_example(const char *filename, int isSDLshow);
void FFNDK_decode_avfile(const char *filename, int write_output);

/******************************************************************************/
/*  End of Header file                                                        */
/******************************************************************************/

#ifdef __cplusplus
}
#endif

#endif /* _FFPLAY_NDK_H_ */
