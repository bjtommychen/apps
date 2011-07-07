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

#thumb arm
LOCAL_ARM_MODE := arm
#armeabi armeabi-v7a x86
TARGET_ARCH_ABI := armeabi-v7a
#TARGET_PLATFORM = android-7

LOCAL_MODULE    := mp3dec
LOCAL_C_INCLUDES := $(LOCAL_PATH)/src $(LOCAL_PATH)/include
LOCAL_CFLAGS := -DHAVE_CONFIG_H -DFPM_DEFAULT -DDECODE_GRANULE -DHUFF_OPT -DRMS_TEST \
				-DSYNTH_USE_TABLE_EVEN_ODD_NEW -D_MSC_VER 

ifeq ($(TARGET_ARCH_ABI),armeabi-v7a)
	LOCAL_CFLAGS += -DOPT_TOMMY_NEON -mfloat-abi=softfp -mfpu=neon -DHAVE_NEON=1
#    LOCAL_SRC_FILES += helloneon-intrinsics.c.neon
endif

LOCAL_SRC_FILES := src/bit.c src/decoderapi.c src/frame.c src/huffman.c src/layer12.c src/layer3.c \
				   src/stream.c src/synth.c src/vbrtag.c src/version.c src/mp3dec-jni.c
				   

# for logging
LOCAL_LDLIBS    += -llog

include $(BUILD_SHARED_LIBRARY)
