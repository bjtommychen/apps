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

#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<sys/types.h>
#include<sys/stat.h>
#include<fcntl.h>


/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/

/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

int main(void)
{
    int fd;
    int i;
    int len;
    char *buf="we love duanduan! god bless our family!\n";
    char buf1[200];

    fd = open("/dev/myDriver",O_RDWR); 
    if (fd == -1)
    {
        printf("Can't open file \n");
        exit(-1);
    }
    len = strlen(buf);

    write(fd,buf,len);
    read(fd,buf1,len);

    printf("\n");
    for(i=0; i<len; i++)
        printf("%c",buf1[i]);
    printf("\n");

    for(i=0;i<len;i++)
    {
        buf1[i] = buf[i] - 1;
    }

    write(fd,buf1,len);
    read(fd,buf1,len);

    printf("\n");
    for(i=0; i<len; i++)
        printf("%c",buf1[i]);
    printf("\n");

    ioctl(fd, 0x2011, 0x0310);

    close(fd);

    return 0;

}
