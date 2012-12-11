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
SIZE=size -t 
RM=rm -f
CFLAGS= -O2 -Wall -I. -I../include -I./inc 
LD_FLAGS  = -Map

LIBS = 

FEATURES = -DHAVE_CONFIG_H -DDEBUG

#OBJ DIR
OBJ_DIR = .
OUT_FILE =fastboot
DEPFILE =local.d

#LIB DIR
LIB_DIR = .
LIB_FILE = libfastboot.a

#MAP
MAP_FILE = fastboot.map

# OBJECT FILES
OLD_OBJECTS = \
 		protocol.o engine.o bootimg.o usb_linux.o util_linux.o
 		
OLD_APP_OBJECTS = fastboot.o

OBJECTS = $(addprefix $(OBJ_DIR)/, $(OLD_OBJECTS))
APP_OBJECTS = $(addprefix $(OBJ_DIR)/, $(OLD_APP_OBJECTS))
OBJECTS_ASM = $(addprefix $(OBJ_DIR)/, $(OLD_OBJECTS_ASM))

#PHONY
.PHONY : all 

all : out

out : showtarget $(OUT_FILE)
	
showtarget:
	@echo "*** Make object for "$(TARGET)" ***"
	@echo ""
	
info:
	@echo "--------  Makefile for ZSP V 1.1---------!!!"
	@echo "make info/mkdep/clean/all/sdnm/zdnm/mklib"
	@echo ""
	
mklib : $(LIB_DIR)/$(LIB_FILE)

mkmap : $(LIB_DIR)/$(LIB_FILE) $(APP_OBJECTS)
	$(LINKER) -T mmp_rom.lcf $(LD_FLAGS) $(MAP_FILE) -o $(OUT_FILE) $(APP_OBJECTS) $(LIB_DIR)/$(LIB_FILE) $(LIBS4MAP)

clean:
	$(RM) $(OBJ_DIR)/*.o
	$(RM) $(OUT_FILE)
	$(RM) $(LIB_DIR)/libfastboot.a
	$(RM) $(MAP_FILE)

mkdep : deldep $(patsubst %.o,%.d, $(OBJECTS))
.PHONY : mkdep

deldep:
	$(RM) $(DEFILE)

$(OUT_FILE) : $(LIB_DIR)/$(LIB_FILE) $(APP_OBJECTS)
	$(CC) -o $(OUT_FILE) $(APP_OBJECTS) $(LIB_DIR)/$(LIB_FILE) ./libzipfile.a ./libunz.a
	@echo "--------  Build done ---------!!!"
	@echo ""

$(patsubst %.o,%.d, $(OBJECTS)) : 
	$(CC) -MM $(patsubst %.d,%.c, $(patsubst $(OBJ_DIR)/%,%,$@))  >> $(DEPFILE)

$(OBJECTS)  : $(patsubst %.o,%.c, $@)
	mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) $(CFLAGS_OPT) $(FEATURES) -o $@ -c $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$@))

../obj/example.o : $(patsubst %.o,%.c, $@)
	mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) $(CFLAGS_OPT) $(FEATURES) -o $@ -c $(patsubst %.o,%.c, $(patsubst $(OBJ_DIR)/%,%,$@))

$(LIB_DIR)/$(LIB_FILE) : $(OBJECTS) $(OBJECTS_ASM)
	mkdir -p $(LIB_DIR)
	$(AR) -r $(LIB_DIR)/$(LIB_FILE) $(OBJECTS) $(OBJECTS_ASM)
	@echo "--------  Make libary done ---------!!!"
	@echo ""
	$(SIZE) $(LIB_DIR)/$(LIB_FILE)
