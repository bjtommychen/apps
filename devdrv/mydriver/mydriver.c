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

#include "linux/kernel.h"
#include "linux/module.h"
#include "linux/fs.h"
#include "linux/init.h"
#include "linux/types.h"
#include "linux/errno.h"
#include "linux/uaccess.h"
#include "linux/kdev_t.h"

/******************************************************************************/
/*  Externs                                                                   */
/******************************************************************************/


/******************************************************************************/
/*  Local Macro Definitions                                                   */
/******************************************************************************/
MODULE_LICENSE("GPL");

/******************************************************************************/
/*  Local Type Definitions                                                    */
/******************************************************************************/

/******************************************************************************/
/*  Local Variables                                                           */
/******************************************************************************/
#define BUFSIZE 256  /*设备中包含的最大字符数*/

char * work_buffer;  /*该指针用于为这个虚拟的设备分配内存空间*/
unsigned int devid_major = 0;

/******************************************************************************/
/*  Local Function Declarations                                               */
/******************************************************************************/

/******************************************************************************/
/*  Function Definitions                                                      */
/******************************************************************************/

static ssize_t device_read(struct file * file,char * buf,size_t count,loff_t * f_pos)
{
    int i;

    if(count>BUFSIZE)   /*如果要求读出的数目多于设备固有的数目则提示并返回*/
    {
        printk("Can't Read , the Count is to Big !\n");
        return  -EFAULT;
    }
    for(i = 0; i < count; i++) /*否则,进行读出操作*/
    {
        //__put_user(work_buffer[i],buf);
        *buf = work_buffer[i]+1;
        buf++;
    }
    printk("device_read %d bytes.\n", count);
    return count;
}


static ssize_t device_write(struct file * file,const char * buf,size_t count,loff_t * f_pos)
{
    int i;
    if(count>BUFSIZE)   /*要求写入的数目比设备的容量大则提示并返回*/
    {
        printk("Can't Write , the Count is to Big\n");
        return  -EFAULT;
    }
    for(i = 0; i < count; i++) /*否则,进行写入操作*/
    {
        __get_user(work_buffer[i],buf);
        buf++;
    }
    printk("device_write %d bytes.\n", count);
    return count;
}

static int device_ioctl (struct inode * inode, struct file *file, unsigned int cmd, unsigned long arg)
{
    printk("device_ioctl cmd 0x%x, argu is 0x%lx.\n", cmd, arg);
    return 0;
}

static int device_open(struct inode * inode,struct file * file) /*打开设备函数*/
{
    work_buffer = (char *)kmalloc(BUFSIZE,GFP_KERNEL);  /*为设备分配内存空间*/
//    MOD_INC_USE_COUNT;
    printk("device_open.\n");
    return 0;
}

static int device_release(struct inode * inode,struct file * file)
{
    kfree(work_buffer);   /*释放设备占用内存空间*/
//    MOD_DEC_USE_COUNT;
    printk("device_release.\n");
    return 0;
}

struct file_operations fops =   /*填充file_operations结构*/
{
    .owner = THIS_MODULE,
    .read = device_read,
     .write = device_write,
      .open = device_open,
       .release = device_release,
       .ioctl = device_ioctl,

    };

static int __init  device_init_module(void)  /*登记设备函数,insmod时调用*/
{
    int num;

    num = register_chrdev(0,"mydriver",&fops); /*系统自动返回一个未被占用的设备号*/
    if(num < 0)      /*登记未成功,提示并返回*/
    {
        printk("Can't Got the devid_major Number !\n");
        return num;
    }
    if(devid_major == 0)
        devid_major = num;

    printk(KERN_INFO"\n\ndevice_init_module, major is %d. init at %s, %s\n", devid_major, __DATE__ ,__TIME__);

    return 0;
}

static void __exit  device_cleanup_module(void)  /*释放设备函数,rmmod时调用*/
{
    unregister_chrdev(devid_major,"mydriver");
    printk(KERN_INFO"device_cleanup_module.\n");
}

module_init(device_init_module);
module_exit(device_cleanup_module);

