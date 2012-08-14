/*******************************************************************************
*
*    mydriver.c    -   mydriver source file
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
#include "linux/device.h"
#include "linux/module.h"
#include "linux/fs.h"
#include "linux/init.h"
#include "linux/types.h"
#include "linux/errno.h"
#include "linux/uaccess.h"
#include "linux/kdev_t.h"
#include <linux/platform_device.h>
#include <linux/miscdevice.h>

//add for android
#include <linux/slab.h>             // kmalloc


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
#define BUFSIZE 256  /*设备中包含的最大字符数*/

static char * work_buffer;  /*该指针用于为这个虚拟的设备分配内存空间*/
static unsigned int devid_major = 0;

static struct resource		*s3cc_jpeg_mem;
static void __iomem			*s3cc_jpeg_base;

static struct class *my_class;

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

static int device_open(struct inode * inode,struct file * file)
{
    work_buffer = (char *)kmalloc(BUFSIZE,GFP_KERNEL);
//    MOD_INC_USE_COUNT;
    printk("device_open.\n");
    return 0;
}

static int device_release(struct inode * inode,struct file * file)
{
    kfree(work_buffer);
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

static struct miscdevice s3cc_jpeg_miscdev = {
	minor:		MISC_DYNAMIC_MINOR,
	name:		"myDriver",
	fops:		&fops
};


static int s3cc_jpeg_probe(struct platform_device *pdev)
{
	struct resource 	*res;
    static int		ret;
	static int		size;

    printk(KERN_INFO"mydriver: s3cc_jpeg_probe enter.");
    
    res = platform_get_resource(pdev, IORESOURCE_MEM, 0);
	if (res == NULL) {
		printk(KERN_INFO "failed to get memory region resouce\n");
		return -ENOENT;
	}

	size = (res->end - res->start) + 1;
	s3cc_jpeg_mem = request_mem_region(res->start, size, pdev->name);

	if (s3cc_jpeg_mem == NULL) {
		printk(KERN_INFO "failed to get memory region\n");
		return -ENOENT;
	}    
	//s3cc_jpeg_base = ioremap(s3cc_jpeg_mem->start, size);

	if (s3cc_jpeg_base == 0) {
		printk(KERN_INFO "failed to ioremap() region\n");
		return -EINVAL;
	}    
	ret = misc_register(&s3cc_jpeg_miscdev);

    printk(KERN_INFO"mydriver: s3cc_jpeg_probe exit.");

	return 0;
}

static int s3cc_jpeg_remove(struct platform_device *dev)
{
	misc_deregister(&s3cc_jpeg_miscdev);
	return 0;
}



static struct platform_driver s3cc_jpeg_driver = {
	.probe		= s3cc_jpeg_probe,
	.remove		= s3cc_jpeg_remove,
	.shutdown	= NULL,
	.suspend	= NULL,
	.resume		= NULL,
	.driver		= {
			.owner	= THIS_MODULE,
			.name	= "myDriver",
	},
};

static char banner[] __initdata = KERN_INFO "Android Virtual Demo Driver, (c) 2012 TommyChen , Build on " __DATE__ ", "__TIME__;

#define AUTO_MKNOD              // no need 'mknod' if needed.
#define DEV_MAJOR_NUM       (249)


static int __init  device_init(void)  /*登记设备函数,insmod时调用*/
{
    int num;

    printk(KERN_INFO"\n\n%s", banner);

#ifdef AUTO_MKNOD
    num = register_chrdev(0 /*0*/,"mydriver",&fops); /*系统自动返回一个未被占用的设备号*/
    my_class = class_create(THIS_MODULE, "test_class_mydriver");
    device_create(my_class, NULL, MKDEV(num, 0), NULL, "%s", "myDriver");
#else
    num = register_chrdev(0,"mydriver",&fops); /*系统自动返回一个未被占用的设备号*/
#endif
    if(num < 0)      /*登记未成功,提示并返回*/
    {
        printk("Can't Got the devid_major Number !\n");
        return num;
    }
    if(devid_major == 0)
        devid_major = num;

    printk(KERN_INFO"device_init_module, major is %d.\n", devid_major );

    return 0;
}

static void __exit  device_exit(void)  /*释放设备函数,rmmod时调用*/
{
    unregister_chrdev(devid_major,"mydriver");
#ifdef AUTO_MKNOD
    device_destroy(my_class, MKDEV(devid_major, 0));
    class_destroy(my_class);
#endif
    printk(KERN_INFO"device_cleanup_module.\n");
}


static int __init s3cc_jpeg_init(void)
{
    printk(KERN_INFO"\n\n%s", banner);
    printk(KERN_INFO"mydriver: s3cc_jpeg_init.");
	return platform_driver_register(&s3cc_jpeg_driver);
}

static void __exit s3cc_jpeg_exit(void)
{
	platform_driver_unregister(&s3cc_jpeg_driver);
    printk(KERN_INFO"mydriver: s3cc_jpeg_exit.");
}

module_init(device_init);
module_exit(device_exit);
//module_init(s3cc_jpeg_init);
//module_exit(s3cc_jpeg_exit);


MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("Tommy, August 2012");
MODULE_DESCRIPTION("Demo module driver for Ubuntu/Android");

