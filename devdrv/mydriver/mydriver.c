
#if 1

/****************hellomod.c*******************************/
#include <linux/module.h> //所有模块都需要的头文件
#include <linux/init.h> // init&exit相关宏
MODULE_LICENSE("GPL");
static int __init hello_init (void)
{
    printk("Hello china init/n");
    return 0;
}

static void __exit hello_exit (void)
{
    printk("Hello china exit/n");
}

module_init(hello_init);
module_exit(hello_exit);

#endif
/****************hellomod.c*******************************/


#if 0

//#define  __NO_VERSION__
#include<linux/version.h> /*以下是本程序包含的头文件*/
#include<linux/module.h>
#include<linux/config.h>
#include<asm-generic/uaccess.h>
#include<linux/types.h>
#include<linux/fs.h>
#include<linux/mm.h>
#include<linux/errno.h>
#include<asm-generic/segment.h>


#include "linux/kernel.h"  
#include "linux/module.h"  
#include "linux/fs.h"  
#include "linux/init.h"  
#include "linux/types.h"  
#include "linux/errno.h"  
#include "linux/uaccess.h"  
#include "linux/kdev_t.h" 

//#include <linux/module.h> 
//#include <linux/init.h>
//#include <linux/kernel.h>

#define BUFSIZE 256  /*设备中包含的最大字符数*/

char * temp;  /*该指针用于为这个虚拟的设备分配内存空间*/
unsigned int major = 0;


#if 1
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
        __put_user(temp[i],buf);
        buf++;
    }
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
        __get_user(temp[i],buf);
        buf++;
    }
    return count;
}

static int device_open(struct inode * inode,struct file * file) /*打开设备函数*/
{
    temp = (char *)kmalloc(BUFSIZE,GFP_KERNEL);  /*为设备分配内存空间*/
    MOD_INC_USE_COUNT;
    return 0;
}

static int device_release(struct inode * inode,struct file * file)
{
    kfree(temp);   /*释放设备占用内存空间*/
    MOD_DEC_USE_COUNT;
    return 0;
}

struct file_operations fops =   /*填充file_operations结构*/
{
read:
    device_read,
write:
    device_write,
open:
    device_open,
release:
    device_release
};

int init_module(void)  /*登记设备函数,insmod时调用*/
{
    int num;
    num = register_chrdev(0,"mydriver",&fops); /*系统自动返回一个未被占用的设备号*/
    if(num < 0)      /*登记未成功,提示并返回*/
    {
        printk("Can't Got the Major Number !\n");
        return num;
    }
    if(major == 0)
        major = num;
    return 0;
}

void cleanup_module(void)  /*释放设备函数,rmmod时调用*/
{
    unregister_chrdev(major,"mydriver");
}
#endif
#endif

