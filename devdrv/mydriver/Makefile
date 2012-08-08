obj-m:=mydriver.o

ifneq ($(KERNELRELEASE),)
# kbuild part of makefile
obj-m := mydriver.o

else
# normal makefile
    KDIR ?= /lib/modules/`uname -r`/build

all:
	$(MAKE) -C $(KDIR) M=$$PWD
	
clean:
	make -C $(KDIR) M=$$PWD clean
	
install:
	insmod mydriver.ko

uninstall:
	rmmod mydriver
	
	
endif
