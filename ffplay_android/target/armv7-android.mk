#------------------------------------------------------------------------------
#
#
# x86.mk
#
# File Description:
#
# Target defines and rules for x86
#
#------------------------------------------------------------------------------
#
# This document contains proprietary information of VeriSilicon Microelectronics
# Co., Ltd. The information contained herein is confidential and
# is not to be used by or disclosed to third parties.
#
# Copyright (C) 2001 Verisilicon Microelectronics Co., Ltd. 
# All rights reserved.
#
#------------------------------------------------------------------------------
# Change History
#
# $Id$
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Target tools
#------------------------------------------------------------------------------
CC := arm-eabi-gcc -mcpu=cortex-a8 
AS := arm-eabi-gcc 
AR := arm-eabi-ar -rc
LD := arm-eabi-gcc -mcpu=cortex-a8 
SIZE := arm-eabi-size -t
ZDB := gdb

#------------------------------------------------------------------------------
# Target defines
#------------------------------------------------------------------------------
TARGET_CFLAGS := -I/usr/local/include --sysroot /srv/android-ndk-r5b/platforms/android-5/arch-arm -fPIC -mandroid -DANDROID -DOS_ANDROID
TARGET_ASFLAGS := 
TARGET_LDFLAGS := -L/home/tommy/ffmpeg/android/armv7_neon/lib/ --sysroot /srv/android-ndk-r5b/platforms/android-5/arch-arm -fPIC -mandroid -DANDROID -DOS_ANDROID
TARGET_DEFINES :=
