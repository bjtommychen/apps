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
MODULE_LIBRARIES := ffplay_lib avformat  avcodec  avutil m c z
MODULE_INCLUDE_DIR := /home/tommy/ffmpeg/android/armv7_neon/lib/

MODULE_NAME := ffplay_android

MODULE_DEFINES = HAVE_CONFIG_H 

MODULE_DEFINES += $(COMMAND_DEFINES)
MODULE_CFLAGS := -Wunused-function -DNDEBUG -O2
MODULE_ASFLAGS := -Wunused-function -O3 -masm_opt
MODULE_LDFLAGS := -Wl,-Map,example.map 


BINARY_DIR = $(CURDIR)

#------------------------------------------------------------------------------
# Rules
#------------------------------------------------------------------------------
.PHONY: all clean

all: exe
	@echo
	@echo 'Build done !!!'
	@echo -e "*** \033[1mBuild done.\n$(BINARY)\033[0m ***" 
clean:

#------------------------------------------------------------------------------
# Common defines and rules
#------------------------------------------------------------------------------
include $(ROOT)/common.mk

