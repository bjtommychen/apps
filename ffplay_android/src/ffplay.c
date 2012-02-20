
#include "libavutil/avstring.h"
//#include "libavutil/colorspace.h"
#include "libavutil/mathematics.h"
#include "libavutil/pixdesc.h"
#include "libavutil/imgutils.h"
#include "libavutil/dict.h"
#include "libavutil/parseutils.h"
#include "libavutil/samplefmt.h"
#include "libavutil/avassert.h"
#include "libavformat/avformat.h"
#include "libavdevice/avdevice.h"
#include "libswscale/swscale.h"
//#include "libavcodec/audioconvert.h"
#include "libavutil/opt.h"
#include "libavcodec/avfft.h"
#include "libswresample/swresample.h"


/* Called from the main */
int main2(int argc, char **argv)
{
    int flags;
    AVPacket *is;


    /* register all codecs, demux and protocols */
    avcodec_register_all();

    av_register_all();
//    avformat_network_init();

    printf("avcodec version %d\n", avcodec_version());
    printf("avcodec config:\n %s\n", avcodec_configuration());
    printf("avcodec license:\n %s\n", avcodec_license());

    printf("avformat version %d\n", avformat_version());
    printf("avformat config:\n %s\n", avformat_configuration());
    printf("avformat license:\n %s\n", avformat_license());

//    show_banner(argc, argv, 0);
    
}