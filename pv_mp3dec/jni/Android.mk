# Copyright (C) 2009 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE    := libpvmp3dec
LOCAL_SRC_FILES :=         \
	src/pvmp3_normalize.cpp \
 	src/pvmp3_alias_reduction.cpp \
 	src/pvmp3_crc.cpp \
 	src/pvmp3_decode_header.cpp \
 	src/pvmp3_decode_huff_cw.cpp \
 	src/pvmp3_getbits.cpp \
 	src/pvmp3_dequantize_sample.cpp \
 	src/pvmp3_framedecoder.cpp \
 	src/pvmp3_get_main_data_size.cpp \
 	src/pvmp3_get_side_info.cpp \
 	src/pvmp3_get_scale_factors.cpp \
 	src/pvmp3_mpeg2_get_scale_data.cpp \
 	src/pvmp3_mpeg2_get_scale_factors.cpp \
 	src/pvmp3_mpeg2_stereo_proc.cpp \
 	src/pvmp3_huffman_decoding.cpp \
 	src/pvmp3_huffman_parsing.cpp \
 	src/pvmp3_tables.cpp \
 	src/pvmp3_imdct_synth.cpp \
 	src/pvmp3_mdct_6.cpp \
 	src/pvmp3_dct_6.cpp \
 	src/pvmp3_poly_phase_synthesis.cpp \
 	src/pvmp3_equalizer.cpp \
 	src/pvmp3_seek_synch.cpp \
 	src/pvmp3_stereo_proc.cpp \
 	src/pvmp3_reorder.cpp \

ifneq ($(TARGET_ARCH_ABI),armeabi-v7a)
LOCAL_CFLAGS := -DHAVE_NEON=1 -DTOMMYTEST
LOCAL_SRC_FILES += \
 	src/pvmp3_polyphase_filter_window.cpp \
 	src/pvmp3_mdct_18.cpp \
 	src/pvmp3_dct_9.cpp \
 	src/pvmp3_dct_16.cpp
else
LOCAL_SRC_FILES += \
	src/asm/pvmp3_polyphase_filter_window_gcc.S \
 	src/asm/pvmp3_mdct_18_gcc.S \
 	src/asm/pvmp3_dct_9_gcc.S \
	src/asm/pvmp3_dct_16_gcc.S
endif


LOCAL_C_INCLUDES := \
        $(LOCAL_PATH)/src \
        $(LOCAL_PATH)/include

include $(BUILD_STATIC_LIBRARY)

# BUILD SHARED LIB
include $(CLEAR_VARS)
LOCAL_MODULE    := libpvmp3dec_shared
LOCAL_STATIC_LIBRARIES := libpvmp3dec
include $(BUILD_SHARED_LIBRARY)


# BUILD EXE
include $(CLEAR_VARS)
LOCAL_C_INCLUDES := \
        $(LOCAL_PATH)/src \
        $(LOCAL_PATH)/include
LOCAL_MODULE := pv_mp3dec.out
LOCAL_SRC_FILES := ../src/pv_mp3dec.c
LOCAL_STATIC_LIBRARIES :=libpvmp3dec
include $(BUILD_EXECUTABLE)
