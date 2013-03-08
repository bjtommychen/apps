#-------------------------------------------------------------------------
# Makefile
#
# Copyright (c) VeriSilicon Beijing
# All rights reserved.
#-------------------------------------------------------------------------

CC=gcc
LINKER=gcc 
AS=as -g3 
AR=ar
MD=mkdir -p
SIZE=size -t 
RM=rm
CFLAGS=-std=gnu99 -DHAVE_CONFIG_H -I. -I./include -I./src -W -Wall -Wextra -Wcast-align -Wnested-externs -Wshadow -Wstrict-prototypes 
LD_FLAGS=-std=gnu99 -O2 -fvisibility=hidden -W -Wall -Wextra -Wcast-align -Wnested-externs -Wshadow -Wstrict-prototypes 
CFLAGS_OPT=-g -O2 
GCCVERSIONGTEQ4 := $(shell expr `gcc -dumpversion | cut -f1 -d.` \>= 4)
ifeq "$(GCCVERSIONGTEQ4)" "1"
    CFLAGS += -fvisibility=hidden
endif

LIBS2LINK = -lm

FEATURES += -DDECODE_ONLY

#SRC DIR
SRC_DIR = .

#OBJ DIR
OBJ_DIR = obj
OUT_FILE =libusb_test
DEPFILE =local.d

#LIB DIR
LIB_DIR = lib
#/$(TARGET)
LIB_FILE = libusb_test.a

#PREBUILT LIB
PREBUILT_LIB_FILE = prebuilt/libusb.a

#MAP
MAP_FILE = libusb_test.map

# OBJECT FILES
SRC_FILES += 

		
OBJECTS = $(addprefix $(OBJ_DIR)/, $(patsubst %.c,%.o, $(SRC_FILES)))

APP_FILES := src/bulk.c 
APP_OBJECTS = $(addprefix $(OBJ_DIR)/, $(patsubst %.c,%.o, $(APP_FILES)))

#PHONY
.PHONY : all 

all : out

out : mkworkdir showtarget $(OUT_FILE)
	
showtarget:
	@echo "*** Make object for "$(TARGET)" ***"
	@echo ""
	
info:
	@echo "--------  Makefile for ZSP V 1.1---------!!!"
	@echo "make info/mkdep/clean/all/sdnm/zdnm/mklib"
	@echo ""

mkworkdir:
	$(MD) $(OBJ_DIR)
	
mklib : $(LIB_DIR)/$(LIB_FILE)

mkmap : $(LIB_DIR)/$(LIB_FILE) $(APP_OBJECTS)
	$(LINKER) -T mmp_rom.lcf $(LD_FLAGS) $(MAP_FILE) -o $(OUT_FILE) $(APP_OBJECTS) $(LIB_DIR)/$(LIB_FILE) $(LIBS4MAP)

clean:
	$(RM) -rf $(OBJ_DIR)/*
	$(RM) -f $(OUT_FILE)
	$(RM) -f $(LIB_DIR)/$(LIB_FILE)
	$(RM) -f $(MAP_FILE)

mkdep : deldep $(patsubst %.o,%.d, $(OBJECTS)) $(patsubst %.o,%.d, $(APP_OBJECTS))
.PHONY : mkdep

test:
	echo $(addprefix $(SRC_DIR)/, $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$(OBJECTS))))

deldep:
	$(RM) -f $(DEPFILE)

$(OUT_FILE) : $(LIB_DIR)/$(LIB_FILE) $(APP_OBJECTS)
	@echo ""
	$(LINKER) $(LD_FLAGS) -o $(OUT_FILE) $(APP_OBJECTS) $(LIB_DIR)/$(LIB_FILE) $(PREBUILT_LIB_FILE) $(LIBS2LINK) 
	@echo "--------  Build done ---------!!!"
	@echo ""

$(patsubst %.o,%.d, $(OBJECTS)) : 
	echo '$(@D)/\' >> $(DEPFILE)
	$(CC) $(CFLAGS) $(CFLAGS_OPT) -MM $(patsubst %.d,%.c, $(patsubst $(OBJ_DIR)/%,%,$@))  >> $(DEPFILE)

$(patsubst %.o,%.d, $(APP_OBJECTS)) : 
	echo '$(@D)/\' >> $(DEPFILE)
	$(CC) $(CFLAGS) $(CFLAGS_OPT) -MM $(patsubst %.d,%.c, $(patsubst $(OBJ_DIR)/%,%,$@))  >> $(DEPFILE)

$(OBJECTS): 
	@echo "CC " $@
	@mkdir -p $(@D) 
	@$(CC) $(CFLAGS) $(CFLAGS_OPT) $(FEATURES) -o $@ -c $(addprefix $(SRC_DIR)/, $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$@))) 

$(APP_OBJECTS): 
	@echo "CC " $@
	@mkdir -p $(@D) 
	@$(CC) $(CFLAGS) $(CFLAGS_OPT) $(FEATURES) -o $@ -c $(addprefix $(SRC_DIR)/, $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$@)))
	
$(LIB_DIR)/$(LIB_FILE) : $(OBJECTS)
	mkdir -p $(LIB_DIR)
	$(AR) -r $(LIB_DIR)/$(LIB_FILE) $(OBJECTS)
	@echo "--------  Make libary done ---------!!!"
	@echo ""
	$(SIZE) $(LIB_DIR)/$(LIB_FILE)

#Created by 'make mkdep'
-include local.d
	
