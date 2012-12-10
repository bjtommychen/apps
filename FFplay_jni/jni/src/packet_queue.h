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


#ifndef _AV_PACKET_QUEUE_H
#define _AV_PACKET_QUEUE_H

#ifdef __cplusplus
extern "C" {
#endif

#include "libavformat/avformat.h"



/******************************************************************************/
/*  Macro Definitions                                                         */
/******************************************************************************/


/******************************************************************************/
/*  Type Definitions                                                          */
/******************************************************************************/
typedef struct PacketQueue
{
	AVPacketList *first_pkt, *last_pkt;
	int nb_packets;
	int size; // total bytes of all nb_packets.
	int abort_request;
//	SDL_mutex *mutex;
//	SDL_cond *cond;
} PacketQueue;


/******************************************************************************/
/*  Enums Definitions                                                         */
/******************************************************************************/


/******************************************************************************/
/*  Structures Definitions                                                    */
/******************************************************************************/


/******************************************************************************/
/*  Function Declarations                                                     */
/******************************************************************************/
void packet_queue_init(PacketQueue *q);
int packet_queue_put(PacketQueue *q, AVPacket *pkt);
int packet_queue_get(PacketQueue *q, AVPacket *pkt, int block);
void packet_queue_flush(PacketQueue *q);
void packet_queue_end(PacketQueue *q);
void packet_queue_abort(PacketQueue *q);

/******************************************************************************/
/*  End of Header file                                                        */
/******************************************************************************/

#ifdef __cplusplus
}
#endif

#endif /* _TEMPLATEH_ */










