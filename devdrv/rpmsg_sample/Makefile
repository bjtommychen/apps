obj-m:=rpmsg_sample.o

rpmsg_sample-objs := rpmsg_client_sample.o

ARCH=$(BUILD_ARCH)

ifeq ($(ARCH),)
ARCH=arm
endif

ifeq ($(ARCH),arm)
	#KDIR ?= /mnt/nfs/bejquad4/andev/cm9src/kernel/samsung/p1
	#KDIR ?= /mnt/nfs/bejquad4/andev/panda/android/kernel/
	KDIR ?= /mnt/nfs/bejquad3/home/schai/android/kernel
	
	PWD := $(shell pwd)
	CROSS_COMPILE=/mnt/nfs/bejquad4/andev/cm9src/prebuilt/linux-x86/toolchain/arm-eabi-4.4.3/bin/arm-eabi-
	EXTRA_CFLAGS += -DTOMMY_MADE
	MODFLAGS       = -DMODULE
	CFLAGS_MODULE   = $(MODFLAGS)  
	AFLAGS_MODULE   = $(MODFLAGS)  
	LDFLAGS_MODULE  = -T $(srctree)/scripts/module-common.lds  
 
all:
	@echo "*** \033[1mBuild for ARM \033[0m ***" 
	$(MAKE) ARCH=arm CROSS_COMPILE=$(CROSS_COMPILE) -C $(KDIR) M=$$PWD modules 
	@echo "*** \033[1mBuild done!\033[0m ***" 

	
clean:
	$(MAKE) -C $(KDIR) M=$$PWD clean ARCH=arm CROSS_COMPILE=$(CROSS_COMPILE)
endif
