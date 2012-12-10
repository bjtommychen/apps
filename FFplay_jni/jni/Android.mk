LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE    := ffplay_jni

LOCAL_C_INCLUDES := $(LOCAL_PATH)/src $(LOCAL_PATH)/include
LOCAL_CFLAGS := -DHAVE_CONFIG_H 
ifeq ($(TARGET_ARCH_ABI), armeabi-v7a)
	LOCAL_CFLAGS += -DOPT_TOMMY_NEON -mfloat-abi=softfp -mfpu=neon -DHAVE_NEON=1
endif

LOCAL_SRC_FILES := src/ffplay-jni.c src/packet_queue.c

# for logging
LOCAL_LDLIBS    := -llog  -lz
LOCAL_LDLIBS    += -L$(LOCAL_PATH)/prebuilt  -lavformat  -lavcodec  -lavutil -lswresample 

include $(BUILD_SHARED_LIBRARY)
