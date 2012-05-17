/************************************************************************
* Use of this software is covered by the terms and conditions
* of the ZSP License Agreement under which it is provided.
*
* Copyright (C) 2009 Verisilicon, Inc.  All rights reserved.
* $Id: config.h,v 1.4 2009-11-25 07:00:12 cn9014 Exp $
************************************************************************/

/* Define to enable diagnostic debugging support. */
/* #undef DEBUG */

#define LOG_NDEBUG 0
#define LOG_TAG "mp3dec codec"

//#include <android/log.h>
//#define TAG LOG_TAG
//#define LOGV(...) __android_log_print(ANDROID_LOG_VERBOSE, TAG, __VA_ARGS__)
#include <utils/Log.h>  


#ifndef __ZSP__
#define SIZEOF_INT 4
#else
#define SIZEOF_INT 2
#endif

/* Define as `__inline' if that's what the C compiler calls it, or to nothing
   if it is not supported. */
#define inline __inline


#ifdef __ZSP__
#define PRINTVAL(val)       printf(" "#val" is %u \n", (unsigned int)(val))
#define PRINTVALL(val)       printf(" "#val" is %ld \n", (unsigned long)(val))
#define PRINTARRAY(ptr, len)    { int iprint;\
                                for(iprint=0;iprint<len;iprint++)printf(" "#ptr" [%0d], %0lxH\n", (unsigned int)iprint, (long)(ptr[iprint]));    \
                                }

#else
#define PRINTVAL(val)       printf(" "#val" is %d \n", val)
#define PRINTVALL(val)       PRINTVAL(val) 
#define PRINTARRAY(ptr, len)    { int i;\
                                for(i=0;i<len;i++)printf(" "#ptr" [%d], %xH\n", i, ptr[i]);    \
                                }
#endif




 
//SMART way, got from Internet
#ifdef DEBUG
extern void mylog(char *fmt);
#define DbgPrintf(...)		{char str[256];sprintf(str, __VA_ARGS__); mylog(str);}
#else
#define DbgPrintf /\
/DbgPrintf
#endif


#if i386 == 1

#elif mips == 1

#else

#ifndef __ARM_EABI__
static inline long DMUL(long x, long y)
{
	register long rval;

	__asm
	{
		SMMULR rval, x, y
	}

    return rval;
}
#else
static inline long DMUL(long x, long y)
{
	register long rval;
    __asm__ volatile ("smmulr %[Rd],%[Rn],%[Rm]" : [Rd]"+r" (rval) : [Rn]"r" (x), [Rm]"r" (y));
    return rval;
}
#endif
#endif






