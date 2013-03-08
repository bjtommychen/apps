


#ifndef __INFO_DEF_H__
#define __INFO_DEF_H__

#ifndef Z8051_MEM_BASE
#define ZSP_DATA_BASE           0x00000000 // ZSP memory of data (128K)
#define ZSP_CODE_BASE           0x04000000 // ZSP memory of code (64K)
#define Z8051_MEM_BASE          0x02070000 // Z8051 memory (48K)
#define AMBA_REG_BASE           0x02000000 // Peripheral register
#endif

//message center
#define MSGC_XDATA_BASE			(0xBA00)            // XDATA IN Z8051

#ifdef __ZSP__
#define MSGC_CTX_BASE             	(Z8051_MEM_BASE+MSGC_XDATA_BASE)
#define SDRAM_MEM_BASE          0x01000000 // External SDRAM memory
#else
#define MSGC_CTX_BASE             	(MSGC_XDATA_BASE)
#define SDRAM_MEM_BASE          0x03000000 // External SDRAM memory
#endif

typedef struct 
{		
    unsigned long magic_id;         //"MSGX"
    unsigned short status;
    unsigned short mode;
    unsigned long rev2;
    unsigned short rev3;
    unsigned short syslooptime;

    // to zsp
    unsigned short status_in;
    unsigned short bufin_flag;      //0: normal,  1: include offset.
    unsigned long bufin_addr;       //sdram address
    unsigned long bufin_size;   // in words
    unsigned long bufin_len;    // in words

    // from zsp
    unsigned short status_out;
    unsigned short bufout_flag;
    unsigned long bufout_addr;      //sdram address
    unsigned long bufout_size;   // in words
    unsigned long bufout_len;    // in words

    unsigned short status_bak[32];
    
}MSGXCHG, *PMSGXCHG;

enum {
    STATUS_IDLE = 0,
 
    //status
    STATUS_PC_READY = 0x10,
    STATUS_ZSP_READY,
    STATUS_ALL_FINISHED,

    //status_in
    STATUS_INBUF_IDLE = 0x20,
    STATUS_INBUF_PC_FILLED,
    STATUS_INBUF_PC_FILLED_LASTONE,
    STATUS_INBUF_ZSP_READING,
    STATUS_INBUF_ZSP_READ_FINISHED,

    //status_out
    STATUS_OUTBUF_IDLE = 0x30,
    STATUS_OUTBUF_ZSP_FILLED,
    STATUS_OUTBUF_ZSP_FILLED_LASTONE,
    STATUS_OUTBUF_PC_READING,
    STATUS_OUTBUF_PC_READ_FINISHED,

};


#define MKFCC(A,B,C,D)   (((unsigned long)D << 24) | ((unsigned long)C << 16) | (B << 8) | A)



#endif //__INFO_DEF_H__
