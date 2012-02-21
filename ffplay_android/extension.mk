#------------------------------------------------------------------------------
#
#
# extension.mk
#
# File Description:
#
# Special defines and rules for release
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
# $Id: extension.mk,v 1.4 2010/08/23 01:54:27 cn9011 Exp $
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Directories
#------------------------------------------------------------------------------
ZVIEW_INCLUDE_DIR := $(subst //,/,$(subst \,/,$(SDSP_HOME))/ide/include)
ROOT_NAME := $(notdir $(abspath $(ROOT)))
REF_ROOT := $(ROOT)/ref/
DOC_ROOT:= $(ROOT)/doc/
TEST_ROOT := $(ROOT)/test/example/
RELEASE_ROOT := $(or $(dest),$(ROOT)/release)
RELEASE_PACKAGE_ROOT := $(RELEASE_ROOT)/$(ROOT_NAME)/
RELEASE_INCLUDE_ROOT := $(RELEASE_PACKAGE_ROOT)include/
RELEASE_SOURCE_ROOT := $(RELEASE_PACKAGE_ROOT)src/
RELEASE_SOURCE_DIR := $(RELEASE_PACKAGE_ROOT)$(MODULE)/
RELEASE_LIBRARY_ROOT := $(RELEASE_PACKAGE_ROOT)lib/$(target)/
RELEASE_TEST_ROOT := $(RELEASE_PACKAGE_ROOT)test/example/
RELEASE_OBJECT_ROOT := $(RELEASE_PACKAGE_ROOT)obj/
RELEASE_TOOL_ROOT := $(RELEASE_PACKAGE_ROOT)tool/
RELEASE_BUILD_ROOT := $(RELEASE_PACKAGE_ROOT)build/
RELEASE_DOC_ROOT := $(RELEASE_PACKAGE_ROOT)doc/
 
#------------------------------------------------------------------------------
# externsion tools
#------------------------------------------------------------------------------
ECD := cd
ELS := ls -pd
ECAT := cat
ECP := cp -fu
ERM := rm -rf
EGREP := grep
ESED := sed
ESORT := sort -bdu -k 1,1 -T $(RELEASE_PACKAGE_ROOT)
ETAR := tar --mode=a+rw --gzip -chvf
EMAKE := make
ECPP := cp -fu --parents
EMV := mv -f
EMGPP := mgpp
ERCSINFO := svn info
EHASH := md5sum
EFIND := find
ECHMOD := chmod

#------------------------------------------------------------------------------
# Misc macros
#------------------------------------------------------------------------------
CONFIG_FILE := $(or $(config),$(SOURCE_ROOT)/aacconfig.h)
SIG_FILE := $(RELEASE_OBJECT_ROOT)$(target)/signature
OTHER_MAKEFILES := $(subst $(lastword $(MAKEFILE_LIST)),,$(MAKEFILE_LIST))
OVERRIDES := $(filter-out dest=$(dest) suffix=% $(suffix) tag=$(tag) testext=$(testext) libext=$(libext),$(MAKEOVERRIDES))
LIST_FILE = $(DEPEND:%.mk=%.lst)
LIB_EXT = $(addprefix $(dir $(LIBRARY_DIR:%/=%)),$(libext))
TEST_SCRIPT = ./run.bat
TEST_EXT = $(testext)
TEST_BIN = $(wildcard $(TEST_ROOT)*.exe)
RELEASE_PACKAGE = $(RELEASE_ROOT)/$(ROOT_NAME)$(if $(target),_$(target))_$(RELEASE_TYPE)_$$(date +%Y%m%d-%H%M%S).tgz
TEST_VECTORS = $(addprefix $(TEST_ROOT)*.,$(or $(suffix),aac))
REF_BIN = $(wildcard $(REF_ROOT)*.exe)
TOOLS = $(addprefix , mkdir echo sed rm make bash cygintl-3.dll cygintl-8.dll cygncurses-9.dll cygreadline6.dll cygwin1 shvars.bat shvars.sh)
BUILD_SCRIPT = build.bat
DOCS = $(addprefix $(DOC_ROOT)*,.pdf .txt)
ZTARGET = sim$(or $(subst g1,,g$(patsubst %__,%,$(patsubst __ZSP_G%,%,$(lastword $(TARGET_DEFINES))))),)

ifneq ($(SUB_DIR),)
EXPORT_RECURSE = $(SUB_DIR:%=EXPORT_%)
endif

#------------------------------------------------------------------------------
# Rules
#------------------------------------------------------------------------------
.PHONY: distsrc distlib distall initenv export buildall checkdist cleanenv packsrc packlib debug exportcurdir signlib

# distsrc
distsrc: initenv exportall buildall checkdist packsrc cleanenv
	$(ECHO) '\nDistribution release process is completed, please make sure the source release package is generated'

# distlib
distlib: initenv exportall buildall checkdist packlib cleanenv
	$(ECHO) '\nDistribution release process is completed, please make sure the lib release package is generated'

# distall
distall: initenv exportall buildall checkdist packsrc packlib cleanenv
	$(ECHO) '\nDistribution process is completed, please make sure both source and lib release packages are generated'

# level 2
initenv: $(RELEASE_ROOT) $(RELEASE_PACKAGE_ROOT) $(RELEASE_SOURCE_ROOT) $(RELEASE_LIBRARY_ROOT) $(RELEASE_TEST_ROOT) $(RELEASE_TOOL_ROOT) $(RELEASE_BUILD_ROOT) $(RELEASE_DOC_ROOT)
	$(ERM) $(addsuffix *,$(RELEASE_SOURCE_ROOT))
	$(ERM) $(addsuffix *,$(RELEASE_TEST_ROOT))
	$(ERM) $(addsuffix *,$(RELEASE_LIBRARY_ROOT))
	$(ERM) $(addsuffix *,$(RELEASE_TOOL_ROOT))
	$(ERM) $(addsuffix *,$(RELEASE_BUILD_ROOT))
	$(ERM) $(addsuffix *,$(RELEASE_DOC_ROOT))
	$(ERM) $(addsuffix *,$(OBJECT_ROOT)/$(target)/)

exportall: initenv
	$(EMAKE) -C $(SOURCE_ROOT) export dest=$(abspath $(RELEASE_ROOT))
	$(EMAKE) -C $(TEST_ROOT) export dest=$(abspath $(RELEASE_ROOT))
	if [[ -f $(CONFIG_FILE) ]]; then\
		$(EMGPP) $(subst -D,+D, $(DEFINES)) $(INCLUDES) -I $(ZVIEW_INCLUDE_DIR) -E +n $(CONFIG_FILE) > $(RELEASE_INCLUDE_ROOT)$(notdir $(CONFIG_FILE)).gpp;\
		$(EMV) $(RELEASE_INCLUDE_ROOT)$(notdir $(CONFIG_FILE)).gpp $(RELEASE_INCLUDE_ROOT)$(notdir $(CONFIG_FILE));\
	fi
	if [[ '$(notdir $(LIB_EXT))' != '' ]]; then $(ECP) $(LIB_EXT) $(dir $(RELEASE_LIBRARY_ROOT:%/=%)); fi
	if [[ '$(REF_BIN)' != '' ]]; then $(MKDIR) $(RELEASE_PACKAGE_ROOT)ref; $(ECP) $(REF_BIN) $(RELEASE_PACKAGE_ROOT)ref/; fi
	if [[ '$(TEST_BIN)$(TEST_EXT)' != '' ]]; then $(ECP) $(TEST_BIN) $(TEST_EXT) $(RELEASE_TEST_ROOT); fi
	$(ECP) $(TEST_VECTORS) $(RELEASE_TEST_ROOT)
	$(ECP) $(TOOLS) $(RELEASE_TOOL_ROOT)
	$(ECP) $(DOCS) $(RELEASE_DOC_ROOT)
	$(ECHO) -n '"../tool/$(notdir $(EMAKE))" -C ../src clean all $(OVERRIDES)' >$(RELEASE_BUILD_ROOT)$(BUILD_SCRIPT)
	$(ECHMOD) a+x $(RELEASE_BUILD_ROOT)$(BUILD_SCRIPT)
	$(ECHO) -n '"../../tool/$(notdir $(EMAKE))" clean all $(OVERRIDES)' >$(RELEASE_TEST_ROOT)$(BUILD_SCRIPT)
	$(ECHMOD) a+x $(RELEASE_TEST_ROOT)$(BUILD_SCRIPT)

buildall: exportall
	$(EMAKE) -C $(RELEASE_SOURCE_ROOT) checkdir all
	$(EMAKE) -C $(RELEASE_TEST_ROOT) all

checkdist:
	$(ECHO) -n '$(ZDB) -x $(target).cmd $(lastword $(shell $(EGREP) 'MODULE_NAME' $(RELEASE_TEST_ROOT)makefile))$(BINARY_SUFFIX)\r\n$(notdir $(TEST_EXT)) $(target)' >$(RELEASE_TEST_ROOT)$(TEST_SCRIPT)
	$(ECHMOD) a+x $(RELEASE_TEST_ROOT)$(TEST_SCRIPT)
	$(ECHO) -n 'target $(ZTARGET)\r\nsim enable codecheck\r\nload\r\nrun\r\nquit' >$(RELEASE_TEST_ROOT)$(target).cmd
	$(ECD) $(RELEASE_TEST_ROOT) && $(TEST_SCRIPT)

packsrc: RELEASE_TYPE = src
packsrc: signsrc
	$(ETAR) $(RELEASE_PACKAGE) --exclude='obj/*' --exclude='exe' -C $(RELEASE_ROOT) $(ROOT_NAME)

packlib: RELEASE_TYPE = lib
packlib: signlib
	$(ETAR) $(RELEASE_PACKAGE) --exclude='obj/*' --exclude='exe' --exclude='src' --exclude='build' -C $(RELEASE_ROOT) $(ROOT_NAME)
	
cleanenv:
	$(ERM) $(RELEASE_PACKAGE_ROOT)

# level 3
$(RELEASE_ROOT) $(RELEASE_PACKAGE_ROOT) $(RELEASE_SOURCE_ROOT) $(RELEASE_LIBRARY_ROOT) $(RELEASE_TEST_ROOT) $(RELEASE_TOOL_ROOT)  $(RELEASE_BUILD_ROOT) $(RELEASE_DOC_ROOT):
	$(MKDIR) $@

export: exportcurdir $(EXPORT_RECURSE)

signsrc signlib:
#	$(ERCSINFO) $(SOURCE_ROOT) | $(EGREP) 'Revision:' | $(EENCRYPT) $(SIG_FILE) > $(SIG_FILE)
	$(ECHO) 'char g_tagname[] __attribute__((section(".signature"))) = "'$(notdir $(RELEASE_PACKAGE))'\\n$(tag)\\n\\' > $(SIG_FILE)
	$(ECD) $(RELEASE_PACKAGE_ROOT) && $(abspath $(EHASH)) `$(abspath $(EFIND)) . -path ./obj -prune -o -type f -print` | $(abspath $(ESED)) 's/\(.*\)/\1\\n\\/' >> $(abspath $(SIG_FILE))
	$(ECHO) '";' >> $(SIG_FILE)
	$(CC) -c -o $(SIG_FILE).o -x c $(SIG_FILE)
	$(AR) $(RELEASE_LIBRARY_ROOT)lib$(lastword $(shell $(EGREP) 'MODULE_NAME' $(RELEASE_SOURCE_ROOT)makefile)).a $(SIG_FILE).o

# level 4
ifneq ($(EXPORT_RECURSE),)
$(EXPORT_RECURSE):
	$(EMAKE) -C $(@:EXPORT_%=%) export
endif

exportcurdir: $(DEPEND)
	$(ESED) -e 's/.*\.o://;s/\\$$//;s/\\/\//g;s/\([^^]\) \([^$$]\)/\1\n\2/g;s/ //g;' $(DEPEND:%.mk=%.tmp) > $(LIST_FILE)
	$(ESORT) $(LIST_FILE) -o $(LIST_FILE)
	[ -d $(RELEASE_SOURCE_DIR) ] || $(MKDIR) $(RELEASE_SOURCE_DIR)
	$(ECPP) `$(ECAT) $(LIST_FILE)` $(RELEASE_SOURCE_DIR)
	for file in `$(ELS) $(addprefix $(RELEASE_SOURCE_DIR)*,.c .C) 2>/dev/null`; do $(EMGPP) $(subst -D,+D, $(DEFINES)) $(INCLUDES) -I $(ZVIEW_INCLUDE_DIR) -E $$file > $$file.gpp; done
	for file in `$(ELS) $(addprefix $(RELEASE_SOURCE_DIR)*,.s .S) 2>/dev/null`; do $(EMGPP) $(subst -D,+D, $(DEFINES)) $(INCLUDES) -I $(ZVIEW_INCLUDE_DIR) -S $$file > $$file.gpp; done
	for file in `$(ELS) $(addprefix $(RELEASE_SOURCE_DIR)*,.gpp) 2>/dev/null`; do $(EMV) $$file $${file%.gpp}; done
	$(ECPP) $(OTHER_MAKEFILES) $(RELEASE_SOURCE_DIR)

