LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE    := ffplay_jni
LOCAL_C_INCLUDES := $(LOCAL_PATH)/src $(LOCAL_PATH)/include
LOCAL_CFLAGS := -DHAVE_CONFIG_H 

ifeq ($(TARGET_ARCH_ABI), armeabi-v7a)
	LOCAL_CFLAGS += -DOPT_TOMMY_NEON -mfloat-abi=softfp -mfpu=neon -DHAVE_NEON=1
#    LOCAL_SRC_FILES += helloneon-intrinsics.c.neon
endif

LOCAL_SRC_FILES := src/ffplay-jni.c
				   

# for logging
LOCAL_LDLIBS    += -L$(LOCAL_PATH)/prebuilt  -llog -lavformat  -lavcodec  -lavutil -lswresample -lz

include $(BUILD_SHARED_LIBRARY)
