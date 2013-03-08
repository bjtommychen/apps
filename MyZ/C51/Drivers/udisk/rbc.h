//
// Copyright (C) 2006-2008, HTCCS
//
// File Name:
//      rbc.h
// Author:
//      luzl
// Date:
//      02/28/2008
// Description:
//      RBC for USB MASS STORAGE.
// History:
//      Date        Author      Modification
//      02/28/2008  luzl        Created.
//
#ifndef __RBC_H__
#define __RBC_H__

#include "stdio.h"
#include "typedef.h"


//
// Logical Unit Number
//
#if 0
#define MAX_LUN             0
#if MAX_LUN >= 0
#define UDISK_NAND          0
#endif
#if MAX_LUN >= 1
#define UDISK_SDMMC         1
#endif
#if MAX_LUN >= 2
#define UDISK_SDRAM         2
#endif

#else	//tommy
#define MAX_LUN             0
#define UDISK_SDRAM          0
#undef UDISK_NAND
//#undef UDISK_SDRAM         
#undef UDISK_SDMMC        
#endif

//
// CBW & CSW signature and error code
//
#ifdef PLATFORM_ZSP
#define CBW_SIGNATURE       0x43425355UL
#define CSW_SIGNATURE       0x53425355UL
#else
#define CBW_SIGNATURE       0x55534243UL        //"USBC"
#define CSW_SIGNATURE       0x55534253UL        //"USBS"
#endif
#define CSW_GOOD            0x00
#define CSW_FAILED          0x01
#define CSW_PHASE_ERROR     0x02


//
// RBC commands
//
#define RBC_CMD_FORMAT                      0x04
#define RBC_CMD_READ10                      0x28
#define RBC_CMD_READCAPACITY                0x25
#define RBC_CMD_STARTSTOPUNIT               0x1b
#define RBC_CMD_SYNCCACHE                   0x35
#define RBC_CMD_VERIFY10                    0x2f
#define RBC_CMD_WRITE10                     0x2a

//
// SPC-2 commands
//
#define SPC_CMD_INQUIRY                     0x12
#define SPC_CMD_MODESELECT6                 0x15
#define SPC_CMD_MODESENSE6                  0x1a
#define SPC_CMD_PERSISTANTRESERVIN          0x5e
#define SPC_CMD_PERSISTANTRESERVOUT         0x5f
#define SPC_CMD_PREVENTALLOWMEDIAREMOVAL    0x1e
#define SPC_CMD_RELEASE6                    0x17
#define SPC_CMD_REQUESTSENSE                0x03
#define SPC_CMD_RESERVE6                    0x16
#define SPC_CMD_TESTUNITREADY               0x00
#define SPC_CMD_WRITEBUFFER                 0x3b
#define SPC_CMD_READFORMATCAPACITY          0x23

//
// HTC commands
//
//#define HTC_CMD_DOWNLOADFIRMWARE            0xe5
//#define HTC_CMD_STARTFIRMWARE               0xe6
//#define HTC_CMD_PHYDEVICEINFO               0xe7
//#define HTC_CMD_PHYERASEBLOCK               0xe8
//#define HTC_CMD_PHYREADPAGE                 0xe9
//#define HTC_CMD_PHYWRITEPAGE                0xea
//#define HTC_CMD_PHYREADSPARE                0xeb
//#define HTC_CMD_PHYWRITESPARE               0xec
//#define HTC_CMD_PHYCONFIGNAND               0xed
//#define HTC_CMD_READREGISTER                0xee
//#define HTC_CMD_WRITEREGISTER               0xef

//
// MYZ commands
// USED BY UDISK FIRMWARE
#define MYZ_CMD_RWMEM                       0xe5
#define MYZ_CMD_ZSP                         0xe6
#define MYZ_CMD_FILEIO                      0xe7
#define MYZ_CMD_LCD                         0xe8


#ifdef __cplusplus
extern "C" {
#endif

//
// USB device status
//
extern bool_t _usbd_reset;
extern bool_t _usbd_suspend;
extern bool_t _usbd_tx_done;
extern bool_t _usbd_rx_done;
extern bool_t _usbd_dma_done;
extern bool_t _usbd_connected;
extern u16_t  _usbd_pkt_size;

enum 
{
    MYZ_READ = 1,
    MYZ_WRITE,

    MYZ_ZSPDMEM = 0x10,
    MYZ_ZSPIMEM,
    MYZ_SDRAM,
    MYZ_Z8051,

    MYZ_ZSPCMD_RESET = 0x20,

    MYZ_LCDCMD_SET_FRAMEBUFFER = 0x30,
    MYZ_LCDCMD_REFRESH_RGB = 0x31,
    MYZ_LCDCMD_REFRESH_YUV = 0x32,
    MYZ_LCDCMD_REFRESH_YUV422 = 0x33,
};


// CBW & CSW packet buffer
union _BULK_COMMAND
{

struct
{
    u32_t dCBWSignature;
    u32_t dCBWTag;
    u32_t dCBWDataTransferLength;
    u8_t bmCBWFlags : 8;
    u8_t bCBWLUN : 4;
    u8_t reserved1 : 4;
    u8_t bCBWCBLength : 4;
    u8_t reserved2 : 4;
    u8_t OperationCode : 8;
    union
    {
        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  LogicalBlockAddress4 : 8;
            u8_t  LogicalBlockAddress3 : 8;
            u8_t  LogicalBlockAddress2 : 8;
            u8_t  LogicalBlockAddress1 : 8;
            u8_t  reserved2 : 8;
            u16_t TransferLength;
            u8_t  reserved3 : 8;
        } _RBC_READ10;

        struct
        {
            u8_t  IMMED : 1;
            u8_t  reserved1 : 4;
            u8_t  LogicalUnitNumber : 3;
            u8_t  reserved2 : 8;
            u8_t  reserved3 : 8;
            u8_t  Start : 1;
            u8_t  LoEj : 1;
            u8_t  reserved4 : 6;
            u32_t reserved5;
            u16_t reserved6;
            u8_t  reserved7 : 8;
        } _RBC_STARTSTOPUNIT;

        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  PageCode : 8;
            u8_t  reserved2 : 8;
            u8_t  AllocationLength : 8;
            u8_t  reserved3 : 8;
        } _SPC_INQUIRY;

        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  reserved2 : 8;
            u32_t reserved3;
            u16_t AllocationLength;
            u8_t  reserved4 : 8;
        } _SPC_READFORMATCAPACITY;

        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  PageCode : 6;
            u8_t  PC : 2;
            u8_t  reserved2 : 8;
            u8_t  ParameterListLength : 8;
            u8_t  Control : 8;
        } _SPC_MODESENSE6;

        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  reserved2 : 8;
            u8_t  reserved3 : 8;
            u8_t  Prevent : 1;
            u8_t  reserved4 : 7;
            u8_t  reserved5 : 8;
        } _SPC_PREVENTALLOWMEDIAREMOVAL;

        struct
        {
            u8_t  mode;             // 1:read, 2:write
            u8_t  target;            // 1:ZSP DATA, 2:ZSP CODE, 3:SDRAM, 4:8051
            u8_t  reserved4;
            u32_t StartAddress;
            u32_t Length;           // in bytes.
            //u8_t  reserved5;
        } _MYZ_RWMEM;

        struct
        {
            u8_t  cmd;             
            u8_t  para1;
            u8_t  para2;
            u8_t  para3;
            u8_t  para4;
            u8_t  reserved5;
            u8_t  reserved6;
        } _MYZ_CMD2ZSP;

        struct
        {
            u8_t  cmd;             
            u8_t  para1;
            u32_t  addr0;
            u32_t  addr1;
            u32_t  addr2;
        } _MYZ_CMD2LCD;

/*
        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  StartAddress4 : 8;
            u8_t  StartAddress3 : 8;
            u8_t  StartAddress2 : 8;
            u8_t  StartAddress1 : 8;
            u8_t  reserved2 : 8;
            u16_t TransferLength;
            u8_t  reserved3 : 8;
        } _HTC_DOWNLOADFIRMWARE;

        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  reserved2 : 8;
            u8_t  reserved3 : 8;
            u8_t  reserved4 : 8;
            u8_t  reserved5 : 8;
            u8_t  reserved6 : 8;
            u16_t AllocationLength;
            u8_t  reserved7 : 8;
        } _HTC_PHYDEVICEINFO;

        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  LogicalBlockAddress5 : 8;
            u8_t  LogicalBlockAddress4 : 8;
            u8_t  LogicalBlockAddress3 : 8;
            u8_t  LogicalBlockAddress2 : 8;
            u8_t  LogicalBlockAddress1 : 8;
            u16_t TransferLength;
            u8_t  reserved2 : 8;
        } _HTC_PHYREADPAGE;

        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  reserved2 : 8;
            u8_t  reserved3 : 8;
            u8_t  reserved4 : 8;
            u8_t  reserved5 : 8;
            u8_t  reserved6 : 8;
            u16_t ParameterListLength;
            u8_t  reserved7 : 8;
        } _HTC_PHYCONFIGNAND;

        struct
        {
            u8_t  reserved1 : 5;
            u8_t  LogicalUnitNumber : 3;
            u8_t  Address4 : 8;
            u8_t  Address3 : 8;
            u8_t  Address2 : 8;
            u8_t  Address1 : 8;
            u8_t  reserved2 : 8;
            u16_t BusWidth;
            u8_t  reserved3 : 8;
        } _HTC_WRITEREGISTER;
*/
    } _CBWCB;

} _CBW;

struct
{
    u32_t dCSWSignature;
    u32_t dCSWTag;
    u32_t dCSWDataResidue;
    u8_t  bCSWStatus : 8;

} _CSW;

    u16_t reserved[16];
};

struct _SENSE
{
    u8_t ErrorCode : 7;
    u8_t Valid : 1;
    u8_t reserved1 : 8;
    u8_t SenseKey : 4;
    u8_t reserved2 : 4;
    u8_t Information4 : 8;
    u8_t Information3 : 8;
    u8_t Information2 : 8;
    u8_t Information1 : 8;
    u8_t AdditionalSenseLength : 8;
    u32_t reserved3;
    u8_t AdditionalSenseCode : 8;
    u8_t AdditionalSenseCodeQualifier : 8;
    u32_t reserved4;
};

extern struct _SENSE __udisk_sense_data;
extern union  _BULK_COMMAND __udisk_BULK_COMMAND;

#define CBW                             __udisk_BULK_COMMAND._CBW
#define CSW                             __udisk_BULK_COMMAND._CSW
#define RBC_READ10                      __udisk_BULK_COMMAND._CBW._CBWCB._RBC_READ10
#define RBC_WRITE10                     __udisk_BULK_COMMAND._CBW._CBWCB._RBC_READ10
#define RBC_VERIFY10                    __udisk_BULK_COMMAND._CBW._CBWCB._RBC_READ10
#define RBC_READCAPACITY                __udisk_BULK_COMMAND._CBW._CBWCB._RBC_READ10
#define RBC_STARTSTOPUNIT               __udisk_BULK_COMMAND._CBW._CBWCB._RBC_STARTSTOPUNIT
#define SPC_INQUIRY                     __udisk_BULK_COMMAND._CBW._CBWCB._SPC_INQUIRY
#define SPC_TESTUNITREADY               __udisk_BULK_COMMAND._CBW._CBWCB._SPC_INQUIRY
#define SPC_READFORMATCAPACITY          __udisk_BULK_COMMAND._CBW._CBWCB._SPC_READFORMATCAPACITY
#define SPC_MODESENSE6                  __udisk_BULK_COMMAND._CBW._CBWCB._SPC_MODESENSE6
#define SPC_MODESELECT6                 __udisk_BULK_COMMAND._CBW._CBWCB._SPC_MODESENSE6
#define SPC_PREVENTALLOWMEDIAREMOVAL    __udisk_BULK_COMMAND._CBW._CBWCB._SPC_PREVENTALLOWMEDIAREMOVAL
#define SPC_REQUESTSENSE                __udisk_BULK_COMMAND._CBW._CBWCB._SPC_INQUIRY

#define MYZ_RWMEM                  __udisk_BULK_COMMAND._CBW._CBWCB._MYZ_RWMEM
#define MYZ_CMD2ZSP                __udisk_BULK_COMMAND._CBW._CBWCB._MYZ_CMD2ZSP
#define MYZ_CMD2LCD                __udisk_BULK_COMMAND._CBW._CBWCB._MYZ_CMD2LCD

//#define HTC_DOWNLOADFIRMWARE            __udisk_BULK_COMMAND._CBW._CBWCB._HTC_DOWNLOADFIRMWARE
//#define HTC_STARTFIRMWARE               __udisk_BULK_COMMAND._CBW._CBWCB._HTC_DOWNLOADFIRMWARE
//#define HTC_PHYDEVICEINFO               __udisk_BULK_COMMAND._CBW._CBWCB._HTC_PHYDEVICEINFO
//#define HTC_PHYERASEBLOCK               __udisk_BULK_COMMAND._CBW._CBWCB._HTC_PHYREADPAGE
//#define HTC_PHYREADPAGE                 __udisk_BULK_COMMAND._CBW._CBWCB._HTC_PHYREADPAGE
//#define HTC_PHYWRITEPAGE                __udisk_BULK_COMMAND._CBW._CBWCB._HTC_PHYREADPAGE
//#define HTC_PHYREADSPARE                __udisk_BULK_COMMAND._CBW._CBWCB._HTC_PHYREADPAGE
//#define HTC_PHYWRITESPARE               __udisk_BULK_COMMAND._CBW._CBWCB._HTC_PHYREADPAGE
//#define HTC_PHYCONFIGNAND               __udisk_BULK_COMMAND._CBW._CBWCB._HTC_PHYCONFIGNAND
//#define HTC_WRITEREGISTER               __udisk_BULK_COMMAND._CBW._CBWCB._HTC_WRITEREGISTER
//#define HTC_READREGISTER                __udisk_BULK_COMMAND._CBW._CBWCB._HTC_WRITEREGISTER

#ifdef UDISK_NAND
extern bool_t __udisk_nand_present;
#endif
#ifdef UDISK_SDMMC
extern bool_t __udisk_sdmmc_present;
#endif
#ifdef UDISK_SDRAM
extern bool_t __udisk_sdram_present;
#endif

extern bool_t __udisk_CBW_valid;
extern bool_t __udisk_IN_stall;
extern bool_t __udisk_OUT_stall;

extern void __udisk_init_usbd(void);
extern void __udisk_process_CSW(u32_t length, u8_t status);
extern void __udisk_write_usb(u8_t *buffer, u16_t length);
extern void __udisk_stall_usb(void);
extern void __udisk_build_sense(u8_t key, u8_t asc, u8_t ascq);

extern void __RBC_Read10(void);
extern void __RBC_Write10(void);
extern void __RBC_Verify10(void);
extern void __RBC_ReadCapacity(void);
extern void __RBC_StartStopUnit(void);
extern void __SPC_Inquiry(void);
extern void __SPC_TestUnitReady(void);
extern void __SPC_ReadFormatCapacity(void);
extern void __SPC_ModeSense6(void);
extern void __SPC_ModeSelect6(void);
extern void __SPC_PreventAllowMediaRemoval(void);
extern void __SPC_RequestSense(void);

/*
extern void __HTC_ReadCapacity(void);
extern void __HTC_StartStopUnit(void);
extern void __HTC_Inquiry(void);
extern void __HTC_TestUnitReady(void);
extern void __HTC_ReadFormatCapacity(void);
extern void __HTC_ModeSense6(void);
extern void __HTC_ModeSelect6(void);
extern void __HTC_PreventAllowMediaRemoval(void);
extern void __HTC_RequestSense(void);
extern void __HTC_DownloadFirmware(void);
extern void __HTC_StartFirmware(void);
extern void __HTC_PhyDeviceInfo(void);
extern void __HTC_PhyEraseBlock(void);
extern void __HTC_PhyReadPage(void);
extern void __HTC_PhyWritePage(void);
extern void __HTC_PhyReadSpare(void);
extern void __HTC_PhyWriteSpare(void);
extern void __HTC_PhyConfigNand(void);
extern void __HTC_WriteRegister(void);
extern void __HTC_ReadRegister(void);
*/

extern void __MYZ_ProcCmd_rwmem(void);
extern void __MYZ_ProcCmd_zsp(void);
extern void __MYZ_ProcCmd_fileio(void);
extern void __MYZ_ProcCmd_lcd(void);



#ifdef __cplusplus
}
#endif


#endif // __RBC_H__
