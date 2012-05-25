LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)
#LOCAL_MODULE    := libpcap 
#LOCAL_SRC_FILES := $(LOCAL_PATH)/prebuilt/libavformat.a $(LOCAL_PATH)/prebuilt/libavcodec.a 
#include $(PREBUILT_STATIC_LIBRARY)



include $(CLEAR_VARS)
LOCAL_SRC_FILES := ff_codec.cpp 


ifeq ($(TARGET_ARCH),arm)
LOCAL_SRC_FILES += \

else
LOCAL_SRC_FILES += \

endif


LOCAL_C_INCLUDES := \
        frameworks/base/media/libstagefright/include \
        $(LOCAL_PATH)/src \
        $(LOCAL_PATH)/include\
	frameworks/base/include/media/stagefright/openmax


LOCAL_CFLAGS := -DHAVE_CONFIG_H 

#LOCAL_STATIC_LIBRARIES := avformat 
#LOCAL_LDLIBS    := -Lprebuilt  -llog -lavformat  -lavcodec  -lavutil -lz
#LOCAL_SHARED_LIBRARIES := libpcap

LOCAL_MODULE := libstagefright_ffcodec


include $(BUILD_STATIC_LIBRARY)
