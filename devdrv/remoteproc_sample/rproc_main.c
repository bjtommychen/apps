#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/notifier.h>
#include <linux/pm.h>
//#include <plat/remoteproc.h>
#include <linux/remoteproc.h>

#if 0
int dummy_rproc_example(void)
{
    struct rproc *my_rproc;

    /* let's power on and boot the image processing unit */
    my_rproc = rproc_get("ipu");
    if (!my_rproc)
    {
        /*
         * something went wrong. handle it and leave.
         */
    }

    printf(" my_proc is %xH\n", my_rproc);
    /*
     * the 'ipu' remote processor is now powered on, and we have a
     * valid handle.... let it work !
     */

    /* if we no longer need ipu's services, power it down */
    rproc_put(my_rproc);
}


int main()
{
    dummy_rproc_example();
}
#endif

char *rproc_dev_string[] = {
"ipu",
"ducati-proc0",
"dsp",
"tesla-dsp",
"tesla-c0",

};


//struct omap_rproc *rproc;
struct rproc *rproc;

static int rproc_callbck_fn(struct notifier_block *nb, unsigned long val,
                            void *data)
{
    switch(val)
    {
        case PM_EVENT_SUSPEND:
            printk(KERN_INFO "%s PM_EVENT_SUSPEND\n", __func__);
            break;
        case PM_EVENT_RESUME:
            printk(KERN_INFO "%s PM_EVENT_RESUME\n", __func__);
            break;
        default:
            printk(KERN_ERR "%s RPM_RESUMING\n", __func__);
            break;
    }
    return 0;
}
static struct notifier_block rproc_nb =
{
    .notifier_call = rproc_callbck_fn,
};

static int __init omap_rproc_test_init(void)
{
//    rproc = rproc_get("ducati-proc0");
//    rproc_event_register (rproc, &rproc_nb);

    int i, num;
    num = sizeof (rproc_dev_string)/ sizeof (char*);
    printk(" Total rproc is %d.\n", num);
    for(i=0; i<num; i++)
    {
        printk("\nNo.%d .... \n", i);
        printk("Try get rproc %s .\n", rproc_dev_string[i]);
        rproc = rproc_get(rproc_dev_string[i]);
        if (!rproc)
        {
            printk("Get failed .\n");
        }
        else
        {
            printk("Get %s OK. put it now.\n", rproc_dev_string[i]);
            rproc_put(rproc);
        }
    }

    return 0;
}

static void __exit omap_rproc_test_exit(void)
{
    rproc_event_unregister (rproc, &rproc_nb);
    rproc_put(rproc);
}
module_init(omap_rproc_test_init);
module_exit(omap_rproc_test_exit);

MODULE_LICENSE("GPL v2");
MODULE_DESCRIPTION("remote proc usage debug function");
MODULE_AUTHOR("Tommy Chen");

