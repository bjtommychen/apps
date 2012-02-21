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
MODULE := $(lastword $(subst /src,/ src,$(CURDIR)))

#------------------------------------------------------------------------------
# Directories
#------------------------------------------------------------------------------
ROOT := $(shell echo $(MODULE) | sed 's/[a-zA-Z0-9_]\+/../g')

#------------------------------------------------------------------------------
# Preset variables
#------------------------------------------------------------------------------
MODULE_SOURCES := ffplay.c

MODULE_LIBRARIES :=
MODULE_INCLUDE_DIR :=

MODULE_NAME := ffplay_lib

MODULE_DEFINES = HAVE_CONFIG_H 

MODULE_DEFINES +=


MODULE_DEFINES += $(COMMAND_DEFINES)
MODULE_CFLAGS = -Wunused-function -DNDEBUG -O2
MODULE_ASFLAGS = -Wunused-function
MODULE_LDFLAGS = -Wl,-Map,ffplay_lib.map

#------------------------------------------------------------------------------
# Rules
#------------------------------------------------------------------------------
.PHONY: all clean

all: lib

clean:

#------------------------------------------------------------------------------
# Common defines and rules
#------------------------------------------------------------------------------
include $(ROOT)/common.mk

