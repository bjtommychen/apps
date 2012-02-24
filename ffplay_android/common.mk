#------------------------------------------------------------------------------
#
#
# common.mk
#
# File Description:
#
# Common defines and rules
#
#------------------------------------------------------------------------------
# Control options
#
# debug - When set to non zero, file will be compiled with -g 
#
# optimize - When set to numeric value, file will be compiled with the specified
#         optimization level
#
# recurse - When set to non zero, file will be compiled recursively
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Options
#------------------------------------------------------------------------------
# recurse
recurse ?= 1

# target
target = arm

#------------------------------------------------------------------------------
# Directories
#------------------------------------------------------------------------------
SOURCE_ROOT := $(ROOT)/src
OBJECT_ROOT := $(ROOT)/obj

TARGET_DIR := $(ROOT)/target
TOOL_DIR := $(ROOT)/tool

INCLUDE_DIR := $(ROOT)/include
OBJECT_DIR := $(patsubst %/,%,$(patsubst %/,%,$(OBJECT_ROOT)/$(target))/$(MODULE:src%=%))

LIBRARY_DIR := $(patsubst %/,%,$(ROOT)/lib/$(target))
BINARY_DIR ?= $(patsubst %/,%,$(ROOT)/exe/$(target))

#------------------------------------------------------------------------------
# Target tools
#------------------------------------------------------------------------------
CC := cc
AS := cc
AR := ar -rc
LD := cc
SIZE := size -t
MAKE := make

#------------------------------------------------------------------------------
# Target specific defines
#------------------------------------------------------------------------------
-include $(TARGET_DIR)/$(target).mk

#------------------------------------------------------------------------------
# Common tools
#------------------------------------------------------------------------------
MKDIR := mkdir -p
ECHO := @echo -e
SED := sed
RM := rm -f
RMALL := rm -rf

#------------------------------------------------------------------------------
# Misc macros
#------------------------------------------------------------------------------
BINARY_SUFFIX ?= .out
INCLUDES = $(addprefix -I,$(INCLUDE_DIR) $(MODULE_INCLUDE_DIR))
DEFINES = $(addprefix -D,$(TARGET_DEFINES) $(MODULE_DEFINES))

ifeq ($(recurse),1)
ifneq ($(SUB_DIR),)
ALL_RECURSE = $(SUB_DIR:%=ALL_%)
CLEAN_RECURSE = $(SUB_DIR:%=CLEAN_%)
CHECK_RECURSE = $(SUB_DIR:%=CHECK_%)
endif
endif

RECURSE = $(ALL_RECURSE) $(CLEAN_RECURSE) $(CHECK_RECURSE)

#------------------------------------------------------------------------------
# Files
#------------------------------------------------------------------------------
SOURCES = $(MODULE_SOURCES)
OBJECTS = $(addprefix $(OBJECT_DIR)/,$(patsubst %.s,%.o,$(MODULE_SOURCES:%.c=%.o)))
LIBRARIES = $(MODULE_LIBRARIES)

LIBRARY_CURRENT = $(LIBRARY_DIR)/lib$(MODULE_NAME).a
BINARY = $(BINARY_DIR)/$(MODULE_NAME)$(BINARY_SUFFIX)
DEPEND = $(OBJECT_DIR)/depends.mk
MAKEFILE = $(ROOT)/common.mk makefile

#------------------------------------------------------------------------------
# Buld flags
#------------------------------------------------------------------------------
TMPCFALGS := $(TARGET_CFLAGS) $(MODULE_CFLAGS)
TMPASFALGS := $(TARGET_ASFLAGS) $(MODULE_ASFLAGS)

# configurable flag
ifdef debug
TMPCFALGS := $(filter-out -g -g1 -g2 -g3,$(TMPCFALGS))
TMPASFALGS := $(filter-out -g -g1 -g2 -g3,$(TMPASFALGS))

ifeq ($(debug),1)
TMPCFALGS := $(TMPCFALGS) -g
TMPASFALGS := $(TMPASFALGS) -g
endif
endif

optimize=3

ifdef optimize
TMPCFALGS := $(filter-out -O -O0 -O1 -O2 -O3 -Os,$(TMPCFALGS))
TMPASFALGS := $(filter-out -O -O0 -O1 -O2 -O3 -Os,$(TMPASFALGS))
TMPCFALGS := $(TMPCFALGS) -O$(optimize)
TMPASFALGS := $(TMPASFALGS) -O$(optimize)
endif

ASFLAGS = -c $(INCLUDES) $(DEFINES) $(TMPASFALGS) -Wall
CFLAGS = -c $(INCLUDES) $(DEFINES) $(TMPCFALGS) -Wall
DEPFLAGS = -MM $(CFLAGS)
LDFLAGS = $(addprefix -l,$(LIBRARIES)) $(addprefix -L,$(LIBRARY_DIR) $(dir $(LIBRARY_DIR))) $(TARGET_LDFLAGS) $(MODULE_LDFLAGS)

#------------------------------------------------------------------------------
# Explicit rules
#------------------------------------------------------------------------------
.PHONY: exe lib clean superclean checkdir $(RECURSE)

# level 1
# checkdir
checkdir: $(OBJECT_DIR) $(LIBRARY_DIR) $(BINARY_DIR) $(CHECK_RECURSE)

# exe
exe: $(OBJECTS)
	@echo
	@echo [ Making exe $(BINARY) ]
	$(LD) $(OBJECTS) $(LDFLAGS) -o $(BINARY)

# lib
lib: $(LIBRARY_CURRENT) $(ALL_RECURSE)
	$(ECHO) \\nLibraries were updated successfully.\\n

# clean
clean: $(CLEAN_RECURSE)
	$(RM) $(OBJECTS)

# superclean
superclean:
	$(RMALL) $(patsubst %/,%,$(OBJECT_ROOT)/$(target))/*
	$(if $(realpath $(BINARY)),,$(RMALL) $(LIBRARY_CURRENT))
	$(RMALL) $(BINARY)

# level 2
$(OBJECT_DIR) $(LIBRARY_DIR) $(BINARY_DIR):
	$(MKDIR) $@

ifneq ($(CHECK_RECURSE),)
$(CHECK_RECURSE):
	$(MAKE) -C $(@:CHECK_%=%) checkdir
endif

ifneq ($(LIBRARY_CURRENT),)
$(LIBRARY_CURRENT): $(OBJECTS)
	$(AR) $@ $?
	$(SIZE) $@
endif

ifneq ($(ALL_RECURSE),)
$(ALL_RECURSE):
	$(MAKE) -C $(@:ALL_%=%) all
endif

ifneq ($(CLEAN_RECURSE),)
$(CLEAN_RECURSE):
	$(MAKE) -C $(@:CLEAN_%=%) clean
endif

#------------------------------------------------------------------------------
# Implicit rules
#------------------------------------------------------------------------------
$(OBJECT_DIR)/%.o: %.c $(MAKEFILE)
	@echo
	@echo [ Compiling $< ]
	$(CC) $(CFLAGS) -o $@ $<

$(OBJECT_DIR)/%.o: %.s $(MAKEFILE)
	$(AS) $(ASFLAGS) -o $@ $<

#------------------------------------------------------------------------------
# Automatic rules
#------------------------------------------------------------------------------
-include $(DEPEND)

$(DEPEND): $(OBJECT_DIR)  $(LIBRARY_DIR) $(BINARY_DIR) $(MAKEFILE)
	$(CC) $(DEPFLAGS) $(SOURCES) > $(@:%.mk=%.tmp) 
	$(SED) 's,\(.*\.o\)[ :]*,$(OBJECT_DIR)/\1 $@: ,g' < $(@:%.mk=%.tmp) > $(@)

#------------------------------------------------------------------------------
# Extension rules
#------------------------------------------------------------------------------
-include $(ROOT)/extension.mk

