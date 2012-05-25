LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)

LOCAL_SRC_FILES := \
        MP3Decoder_tommy.cpp \
		src/bit.c src/decoderapi.c src/frame.c src/huffman.c src/layer12.c \
		src/layer3.c src/stream.c src/synth.c src/vbrtag.c src/version.c 
	

ifeq ($(TARGET_ARCH),arm)
LOCAL_SRC_FILES += \

else
LOCAL_SRC_FILES += \

endif
 
LOCAL_C_INCLUDES := \
        frameworks/base/media/libstagefright/include \
        $(LOCAL_PATH)/src \
        $(LOCAL_PATH)/include


LOCAL_CFLAGS := \
         -DSYNTH_USE_TABLE_EVEN_ODD_NEW -D_MSC_VER -DHAVE_CONFIG_H -DFPM_DEFAULT -DDECODE_GRANULE -DHUFF_OPT -DRMS_TEST 

LOCAL_MODULE := libstagefright_mp3dec_tommy

include $(BUILD_STATIC_LIBRARY)

