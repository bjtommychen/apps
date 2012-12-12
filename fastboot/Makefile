#-------------------------------------------------------------------------
# Makefile
#
# Copyright (c) VeriSilicon Beijing
# All rights reserved.
#-------------------------------------------------------------------------

CC=gcc -m32
LINKER=gcc -m32 
AS=as -g3 
AR=ar
MD=mkdir -p
SIZE=size -t 
RM=rm -f
CFLAGS=-O2 -Wall -I. -I../include -I./inc 
LD_FLAGS= -Map

LIBS2LINK = ./libzipfile.a ./libunz.a

FEATURES = -DHAVE_CONFIG_H -DDEBUG

#SRC DIR
SRC_DIR = .

#OBJ DIR
OBJ_DIR = obj
OUT_FILE =fastboot
DEPFILE =local.d

#LIB DIR
LIB_DIR = lib
LIB_FILE = libfastboot.a

#MAP
MAP_FILE = fastboot.map

# OBJECT FILES
SRC_FILES := protocol.c engine.c bootimg.c usb_linux.c util_linux.c
OBJECTS = $(addprefix $(OBJ_DIR)/, $(patsubst %.c,%.o, $(SRC_FILES)))

APP_FILES := fastboot.c 
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
	$(RM) $(OBJ_DIR)/*.o
	$(RM) $(OUT_FILE)
	$(RM) $(LIB_DIR)/$(LIB_FILE)
	$(RM) $(MAP_FILE)

mkdep : deldep $(patsubst %.o,%.d, $(OBJECTS))
.PHONY : mkdep

test:
	echo $(addprefix $(SRC_DIR)/, $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$(OBJECTS))))

deldep:
	$(RM) $(DEFILE)

$(OUT_FILE) : $(LIB_DIR)/$(LIB_FILE) $(APP_OBJECTS)
	$(CC) -o $(OUT_FILE) $(APP_OBJECTS) $(LIB_DIR)/$(LIB_FILE) $(LIBS2LINK) 
	@echo "--------  Build done ---------!!!"
	@echo ""

$(patsubst %.o,%.d, $(OBJECTS)) : 
	$(CC) -MM $(patsubst %.d,%.c, $(patsubst $(OBJ_DIR)/%,%,$@))  >> $(DEPFILE)

$(OBJECTS)  : $(addprefix $(SRC_DIR)/, $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$(OBJECTS))))
	$(CC) $(CFLAGS) $(CFLAGS_OPT) $(FEATURES) -o $@ -c $(addprefix $(SRC_DIR)/, $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$@)))

$(APP_OBJECTS)  : $(addprefix $(SRC_DIR)/, $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$(APP_OBJECTS))))
	$(CC) $(CFLAGS) $(CFLAGS_OPT) $(FEATURES) -o $@ -c $(addprefix $(SRC_DIR)/, $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$@)))
	
../obj/example.o : $(patsubst %.o,%.c, $@)
#	mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) $(CFLAGS_OPT) $(FEATURES) -o $@ -c $(patsubst %.o,%.c, 

$(LIB_DIR)/$(LIB_FILE) : $(OBJECTS)
	mkdir -p $(LIB_DIR)
	$(AR) -r $(LIB_DIR)/$(LIB_FILE) $(OBJECTS)
	@echo "--------  Make libary done ---------!!!"
	@echo ""
	$(SIZE) $(LIB_DIR)/$(LIB_FILE)
