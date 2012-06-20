
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

#thumb arm
LOCAL_ARM_MODE := arm
#armeabi armeabi-v7a x86
TARGET_ARCH_ABI := armeabi-v7a
#TARGET_PLATFORM = android-7

LOCAL_MODULE    := cpp_test.out
LOCAL_C_INCLUDES := $(LOCAL_PATH)/../src $(LOCAL_PATH)/../include
LOCAL_CFLAGS := -DHAVE_CONFIG_H

ifeq ($(TARGET_ARCH_ABI),armeabi-v7a)
	LOCAL_CFLAGS += -DOPT_TOMMY_NEON -mfloat-abi=softfp -mfpu=neon -DHAVE_NEON=1
endif

LOCAL_SRC_FILES := ../src/hello.cpp
				   
# for logging
LOCAL_LDLIBS    += -llog

include $(BUILD_EXECUTABLE)
