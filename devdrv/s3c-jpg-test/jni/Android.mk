
#dir of JNI
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

#thumb arm
LOCAL_ARM_MODE := arm
#armeabi armeabi-v7a x86
TARGET_ARCH_ABI := armeabi-v7a

LOCAL_MODULE    := s3cjpgtest.out
LOCAL_C_INCLUDES := $(LOCAL_PATH)/../src $(LOCAL_PATH)/../include 
LOCAL_CFLAGS := -DTOMMY_ANDROID_DEMO 

ifeq ($(TARGET_ARCH_ABI), armeabi-v7a)
	LOCAL_CFLAGS += -DOPT_TOMMY_NEON -mfloat-abi=softfp -mfpu=neon -DHAVE_NEON=1
endif

LOCAL_SRC_FILES := ../src/s3cjpgtest.c
				   

# for logging
#LOCAL_LDLIBS    += -Lprebuilt  -llog -lavformat  -lavcodec  -lavutil -lz

#include $(BUILD_SHARED_LIBRARY)
include $(BUILD_EXECUTABLE)

