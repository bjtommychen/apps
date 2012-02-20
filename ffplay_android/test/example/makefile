#------------------------------------------------------------------------------
#
#
# makefile
#
# File Description:
#
# Special defines and rules for this directory
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
# Basic variables
#------------------------------------------------------------------------------
SHELL = bash
COMMAND_DEFINES = $(subst DEF_,,$(filter DEF_%,$(MAKEOVERRIDES)))
MODULE := $(lastword $(subst /test,/ test,$(CURDIR)))

#------------------------------------------------------------------------------
# Directories
#------------------------------------------------------------------------------
ROOT := $(shell echo $(MODULE) | sed 's/[a-zA-Z0-9_]\+/../g')

#------------------------------------------------------------------------------
# Preset variables
#------------------------------------------------------------------------------
MODULE_SOURCES := example.c
MODULE_LIBRARIES := ffplay_lib ffmpeg_armv7_neon
MODULE_INCLUDE_DIR :=

MODULE_NAME := example

MODULE_DEFINES = HAVE_CONFIG_H FPM_DEFAULT DECODE_GRANULE HUFF_OPT RMS_TEST
ifeq ($(asm),1)
#C_BITEXACT
MODULE_DEFINES += USE_ALIAS_ASM USE_IMDCTS_ASM USE_REORDER_ASM

#NOT_BITEXACT
MODULE_DEFINES += USE_IMDCTL_ASM USE_DCT32_ASM\
					USE_HUFF_ASM USE_IIIDECODE_ASM USE_SYNTH_ASM
					
ifneq ($(target),zsp400)
#C_BITEXACT
MODULE_DEFINES += USE_BIT_ASM
endif

ifneq ($(target),zsp500)
#C_BITEXACT
MODULE_DEFINES += SYNTH_USE_TABLE_EVEN_ODD_NEW
endif
endif
ifeq ($(RELEASE_TYPE_MP3),)
MODULE_DEFINES += SKIP_ERROR
endif
MODULE_DEFINES += $(COMMAND_DEFINES)
MODULE_CFLAGS := -Wunused-function -DNDEBUG -O2
MODULE_ASFLAGS := -Wunused-function -O3 -masm_opt
MODULE_LDFLAGS := -Wl,-Map,example.map
ifdef lcf
MODULE_LDFLAGS := $(MODULE_LDFLAGS) -Wl,-T,$(or $(lcf),example.lcf)
endif

BINARY_DIR = $(CURDIR)

#------------------------------------------------------------------------------
# Rules
#------------------------------------------------------------------------------
.PHONY: all clean

all: exe

clean:

#------------------------------------------------------------------------------
# Common defines and rules
#------------------------------------------------------------------------------
include $(ROOT)/common.mk

