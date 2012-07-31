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
*   $Id$
*******************************************************************************/

/*********************************************************
tommy@tu:/$ cat /proc/driver/rtc
rtc_time        : 08:20:19
rtc_date        : 2012-07-31
alrm_time       : 00:00:00
alrm_date       : ****-**-**
alarm_IRQ       : no
alrm_pending    : no
24hr            : yes
periodic_IRQ    : no
update_IRQ      : no
HPET_emulated   : no
DST_enable      : no
periodic_freq   : 1024
batt_status     : okay

rtc device drive:  ./home/tommy/cm7src/kernel/samsung/aries/drivers/char/rtc.c

ref:
http://blog.csdn.net/yuanlulu/article/details/6817099

**********************************************************/

#include "stdio.h"
#include "stdlib.h"
#include "string.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include "linux/rtc.h"

/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/
#define TRUE 1
#define FALSE 0
#define VERSION "1.00"
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
static void show_banner(int argc, char **argv)
{
    printf("RTC demo v %s by %s.\t", VERSION, AUTHOR);
    printf("%sbuilt on %s %s \n", " ", __DATE__, __TIME__);
}

static int rtc_open()
{
    int fd;

    fd = open("/dev/rtc", O_RDONLY);
    if(fd >=0)
        return fd;

    fd = open("/dev/rtc0", O_RDONLY);
    if(fd >=0)
        return fd;
}

void rtc_read_tm(struct rtc_time *ptm, int fd)
{
    memset(ptm, 0, sizeof(*ptm));
    ioctl(fd, RTC_RD_TIME, ptm);
    //ptm->tm_isdst = -1; /* Day Saving Time */
}


void rtc_read_alarm(struct rtc_wkalrm *ptm, int fd)
{
    int err;
    memset(ptm, 0, sizeof(*ptm));
    err = ioctl(fd, /*RTC_RD_TIME*/ RTC_WKALM_RD, ptm);
    if (err != 0)
        printf(" read alarm error!\n");
}

void rtc_show_tm(struct rtc_time *ptm)
{
    struct rtc_time tm = *ptm;
    printf(
        "rtc_time\t: %02d:%02d:%02d\n"
        "rtc_date\t: %04d-%02d-%02d\n",
        tm.tm_hour, tm.tm_min, tm.tm_sec,
        tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday);

}
/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

int main(int argc, char **argv)
{
    int fd_rtc;
    struct rtc_time tm;
    struct rtc_wkalrm alrm;

    show_banner(argc, argv);

    fd_rtc = rtc_open();

    rtc_read_tm(&tm, fd_rtc);
    rtc_read_alarm(&alrm, fd_rtc);

    rtc_show_tm(&tm);

    printf("Alarm is %s.\n", alrm.enabled? "true":"false");
    rtc_show_tm(&(alrm.time));

    printf("Done.\n");
}



