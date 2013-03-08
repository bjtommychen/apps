/*++

Copyright (c) 1997-1998  Microsoft Corporation

Module Name:

    RWBulk.c

Abstract:

    Console test app for BulkUsb.sys driver

Environment:

    user mode only

Notes:

  THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
  KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
  PURPOSE.

  Copyright (c) 1997-1998 Microsoft Corporation.  All Rights Reserved.


Revision History:

        11/17/97: created

--*/

#include <windows.h>

#include <conio.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <time.h>

#include "devioctl.h"

#include <setupapi.h>
#include <basetyps.h>
#include "BulkUsr.h"

#include "usbdi.h"

// tommy
#include <windows.h>
#include <devioctl.h>
#include <ntdddisk.h>
#include <ntddscsi.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include "spti.h"

#include "myz_msgctx_def.h"

#define DEBUG
#define DEVNAME_MATCH  "usbstor#disk&ven_usb2zsp"
//#define OPEN_DEVIE_FAST				//Open faster, using CreateFile.

char devname_string[256]="";


#define NOISY(_x_) printf _x_ ;
typedef struct
{
    UCHAR dir;                  // 0: out  1:in
    ULONG len;
    UCHAR CDB[16];

} SCSI_CMD_BLOCK;

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

typedef signed char s8_t;
typedef unsigned char u8_t;
typedef signed short s16_t;
typedef unsigned short u16_t;
typedef signed long s32_t;
typedef unsigned long u32_t;

// CBW & CSW packet buffer
typedef struct
{
    union
    {
        struct
        {
            u8_t reserved1[16];
        } _SPC_NULL;

        struct
        {
            u8_t OperationCode;
            u8_t mode;          // 1:read, 2:write
            u8_t target;        // 1:ZSP DATA, 2:ZSP CODE, 3:SDRAM, 4:8051
            u8_t reserved4;
            u32_t StartAddress;
            u32_t Length;       // in bytes.
            u32_t reserved5;
        } _MYZ_RWMEM;

        struct
        {
            u8_t OperationCode;
            u8_t cmd;
            u8_t para1;
            u8_t para2;
            u8_t para3;
            u8_t para4;
            u8_t reserved5;
            u8_t reserved6;
        } _MYZ_CMD2ZSP;

        struct
        {
            u8_t OperationCode;
            u8_t  cmd;             
            u8_t  para1;
            u32_t  addr0;
            u32_t  addr1;
            u32_t  addr2;
        } _MYZ_CMD2LCD;

    } _CBWCB;

} CBW, *PCBW;


#ifndef OPEN_DEVIE_FAST
char completeDeviceName[256] = ""; //generated from the GUID registered by the driver itself
#else
char completeDeviceName[256] = 
"\\\\?\\usbstor#disk&ven_usb2zsp&prod_virtual_swapdisk&rev_1.00#1.00&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}"; //generated from the GUID registered by the driver itself
#endif

BOOL fScsiTest = FALSE;
int gDebugLevel = 0;            // higher == more verbose, default is 1, 0 turns off all
int WriteLen = 0;               // #bytes to write
int ReadLen = 0;                // #bytes to read
HANDLE hDEV = 0;

#define USBBUF_SIZE         (0x10000) //64k
UCHAR USBbuffer[USBBUF_SIZE];
SCSI_CMD_BLOCK scsicmd;

/*++
Routine Description:

    Given the HardwareDeviceInfo, representing a handle to the plug and
    play information, and deviceInfoData, representing a specific usb device,
    open that device and fill in all the relevant information in the given
    USB_DEVICE_DESCRIPTOR structure.

Arguments:

    HardwareDeviceInfo:  handle to info obtained from Pnp mgr via SetupDiGetClassDevs()
    DeviceInfoData:      ptr to info obtained via SetupDiEnumDeviceInterfaces()

Return Value:

    return HANDLE if the open and initialization was successfull,
        else INVLAID_HANDLE_VALUE.

--*/
HANDLE
OpenOneDevice(IN HDEVINFO HardwareDeviceInfo, IN PSP_DEVICE_INTERFACE_DATA DeviceInfoData, IN char *devName)
{
    PSP_DEVICE_INTERFACE_DETAIL_DATA functionClassDeviceData = NULL;
    ULONG predictedLength = 0;
    ULONG requiredLength = 0;
    HANDLE hOut = INVALID_HANDLE_VALUE;

    //
    // allocate a function class device data structure to receive the
    // goods about this particular device.
    //
    SetupDiGetDeviceInterfaceDetail(HardwareDeviceInfo, DeviceInfoData, NULL, // probing so no output buffer yet
                                    0, // probing so output buffer length of zero
                                    &requiredLength, NULL); // not interested in the specific dev-node


    predictedLength = requiredLength;
    // sizeof (SP_FNCLASS_DEVICE_DATA) + 512;

    functionClassDeviceData = malloc(predictedLength);
    functionClassDeviceData->cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA);

    //
    // Retrieve the information from Plug and Play.
    //
    if (!SetupDiGetDeviceInterfaceDetail(HardwareDeviceInfo,
                                         DeviceInfoData,
                                         functionClassDeviceData, predictedLength, &requiredLength, NULL))
    {
        free(functionClassDeviceData);
        return INVALID_HANDLE_VALUE;
    }

    strcpy(devName, functionClassDeviceData->DevicePath);
    
	#ifdef DEBUG
	printf("\nAttempting to open... \n%s\n", functionClassDeviceData->DevicePath);
	printf(" %s, %s\n", devName, devname_string);
	#endif
	
    // search 'usb', if not found, return now. used to skip ide....
    if (strstr(devName, devname_string) == 0)
        return hOut;

    hOut = CreateFile(devName, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, // no SECURITY_ATTRIBUTES structure
                      OPEN_EXISTING, // No special create flags
                      FILE_ATTRIBUTE_NORMAL, // No special attributes
                      NULL);    // No template file

    if (INVALID_HANDLE_VALUE == hOut)
    {
        printf("FAILED to open %s\n", devName);
    }
    else
    {
        printf(" OpenOneDevice():Device handle is %XH\n", hOut);

    }

    free(functionClassDeviceData);
    return hOut;

}

/*++
Routine Description:

   Do the required PnP things in order to find
   the next available proper device in the system at this time.

Arguments:

    pGuid:      ptr to GUID registered by the driver itself
    outNameBuf: the generated name for this device

Return Value:

    return HANDLE if the open and initialization was successful,
        else INVLAID_HANDLE_VALUE.
--*/
HANDLE OpenUsbDevice(LPGUID pGuid, char *outNameBuf)
{
    ULONG NumberDevices;
    HANDLE hOut = INVALID_HANDLE_VALUE;
    HDEVINFO hardwareDeviceInfo;
    SP_DEVICE_INTERFACE_DATA deviceInfoData;
    ULONG i;
    BOOLEAN done;
    PUSB_DEVICE_DESCRIPTOR usbDeviceInst;
    PUSB_DEVICE_DESCRIPTOR *UsbDevices = &usbDeviceInst;

    *UsbDevices = NULL;
    NumberDevices = 0;

    //
    // Open a handle to the plug and play dev node.
    // SetupDiGetClassDevs() returns a device information set that contains info on all
    // installed devices of a specified class.
    //
    hardwareDeviceInfo = SetupDiGetClassDevs(pGuid, NULL, // Define no enumerator (global)
                                             NULL, // Define no
                                             (DIGCF_PRESENT | // Only Devices present
                                              DIGCF_DEVICEINTERFACE)); // Function class devices.

    //
    // Take a wild guess at the number of devices we have;
    // Be prepared to realloc and retry if there are more than we guessed
    //
    NumberDevices = 40;
    done = FALSE;
    deviceInfoData.cbSize = sizeof(SP_DEVICE_INTERFACE_DATA);

    i = 0;
    while (!done)
    {
        NumberDevices *= 2;

        if (*UsbDevices)
        {
            *UsbDevices = realloc(*UsbDevices, (NumberDevices * sizeof(USB_DEVICE_DESCRIPTOR)));
        }
        else
        {
            *UsbDevices = calloc(NumberDevices, sizeof(USB_DEVICE_DESCRIPTOR));
        }

        if (NULL == *UsbDevices)
        {

            // SetupDiDestroyDeviceInfoList destroys a device information set
            // and frees all associated memory.

            SetupDiDestroyDeviceInfoList(hardwareDeviceInfo);
            return INVALID_HANDLE_VALUE;
        }

        usbDeviceInst = *UsbDevices + i;

        for (; i < NumberDevices; i++)
        {

            // SetupDiEnumDeviceInterfaces() returns information about device interfaces
            // exposed by one or more devices. Each call returns information about one interface;
            // the routine can be called repeatedly to get information about several interfaces
            // exposed by one or more devices.
			#ifdef DEBUG
			printf("Open device No.%d -------- ", i);
			#endif
			
            if (SetupDiEnumDeviceInterfaces(hardwareDeviceInfo, 0, // We don't care about specific PDOs
                                            pGuid, i, &deviceInfoData))
            //if (SetupDiEnumDeviceInfo(hardwareDeviceInfo,i,&deviceInfoData))													
            {

                hOut = OpenOneDevice(hardwareDeviceInfo, &deviceInfoData, outNameBuf);
                if (hOut != INVALID_HANDLE_VALUE)
                {
                    done = TRUE;
                    break;
                }
            }
            else
            {
                if (ERROR_NO_MORE_ITEMS == GetLastError())
                {
                    done = TRUE;
                    break;
                }
            }
        }
    }

    NumberDevices = i;

    // SetupDiDestroyDeviceInfoList() destroys a device information set
    // and frees all associated memory.

    SetupDiDestroyDeviceInfoList(hardwareDeviceInfo);
    free(*UsbDevices);
    return hOut;
}



/*++
Routine Description:

    Given a ptr to a driver-registered GUID, give us a string with the device name
    that can be used in a CreateFile() call.
    Actually briefly opens and closes the device and sets outBuf if successfull;
    returns FALSE if not

Arguments:

    pGuid:      ptr to GUID registered by the driver itself
    outNameBuf: the generated zero-terminated name for this device

Return Value:

    TRUE on success else FALSE

--*/
BOOL GetUsbDeviceFileName(LPGUID pGuid, char *outNameBuf)
{
    HANDLE hDev = OpenUsbDevice(pGuid, outNameBuf);
    if (hDev != INVALID_HANDLE_VALUE)
    {
        CloseHandle(hDev);
        return TRUE;
    }
    return FALSE;

}

/*++
Routine Description:

    Called by dumpUsbConfig() to open an instance of our device

Arguments:

    None

Return Value:

    Device handle on success else NULL

--*/
HANDLE Open_MyZdev()
{

#ifndef OPEN_DEVIE_FAST
    HANDLE hDEV = OpenUsbDevice((LPGUID) & GUID_CLASS_I82930_BULK,
                                completeDeviceName);

#else
    HANDLE hDEV = CreateFile(completeDeviceName, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, // no SECURITY_ATTRIBUTES structure
                      OPEN_EXISTING, // No special create flags
                      FILE_ATTRIBUTE_NORMAL, // No special attributes
                      NULL);    // No template file
#endif
    if (hDEV == INVALID_HANDLE_VALUE)
    {
        printf("Failed to found MyZ device !\n");
    }
    else
    {
        printf("Found MyZ device !\n");
    }

    return hDEV;
}


/*++
Routine Description:

    Called by main() to dump usage info to the console when
    the app is called with no parms or with an invalid parm

Arguments:

    None

Return Value:

    None

--*/
void usage()
{
    static int i = 1;

    if (i)
    {
        printf("\n*********** USB Commander v1.0 **********\n");
/*
        printf("Usage for Communicate with Z51/ZSP board:\n");
        printf("-rwmem (r/w) (dmem/imem/sdram/z51) (addr) (len)sectors (file)\n");
        printf("-zspcmd (reset) (0/1)\n");
        printf("-fileio infile outfile\n");
        printf("-lcdcmd setfb addr0 addr1 addr2\n");
        printf("-lcdcmd refresh (rgb/yuv/yuv422),  Note: rgb is 555, yuv is yuv420.\n");
*/
		printf("-list\n\tList all the devices until find the matched one.\n");
		printf("-resetdevice devicestring\n\tSend ResetPort cmd to matched device.\n");
        i = 0;
    }
}



#define NPERLN 8
void dump(UCHAR * b, int len)
/*++
Routine Description:

    Called to do formatted ascii dump to console of the io buffer

Arguments:

    buffer and length

Return Value:

    none

--*/
{
    ULONG i;
    ULONG longLen = (ULONG) len / sizeof(ULONG);
    PULONG pBuf = (PULONG) b;

    // dump an ordinal ULONG for each sizeof(ULONG)'th byte
    printf("\n****** BEGIN DUMP LEN decimal %d, 0x%x\n", len, len);
    for (i = 0; i < longLen; i++)
    {
        printf("%04X ", *pBuf++);
        if (i % NPERLN == (NPERLN - 1))
        {
            printf("\n");
        }
    }
    if (i % NPERLN != 0)
    {
        printf("\n");
    }
    printf("\n****** END DUMP LEN decimal %d, 0x%x\n", len, len);
}


VOID PrintSenseInfo(PSCSI_PASS_THROUGH_WITH_BUFFERS psptwb)
{
    int i;

    printf("Scsi status: %02Xh\n\n", psptwb->spt.ScsiStatus);
    if (psptwb->spt.SenseInfoLength == 0)
    {
        return;
    }
    printf("Sense Info -- consult SCSI spec for details\n");
    printf("-------------------------------------------------------------\n");
    for (i = 0; i < psptwb->spt.SenseInfoLength; i++)
    {
        printf("%02X ", psptwb->ucSenseBuf[i]);
    }
    printf("\n\n");
}

VOID PrintError(ULONG ErrorCode)
{
    UCHAR errorBuffer[80];
    ULONG count;

    count = FormatMessage(FORMAT_MESSAGE_FROM_SYSTEM,
                          NULL, ErrorCode, 0, errorBuffer, sizeof(errorBuffer), NULL);

    if (count != 0)
    {
        printf("%s\n", errorBuffer);
    }
    else
    {
        printf("Format message failed.  Error: %d\n", GetLastError());
    }
}

VOID PrintDataBuffer(PUCHAR DataBuffer, ULONG BufferLength)
{
    ULONG Cnt;

    printf("      00  01  02  03  04  05  06  07   08  09  0A  0B  0C  0D  0E  0F\n");
    printf("      ---------------------------------------------------------------\n");
    for (Cnt = 0; Cnt < BufferLength; Cnt++)
    {
        if ((Cnt) % 16 == 0)
        {
            printf(" %03X  ", Cnt);
        }
        printf("%02X  ", DataBuffer[Cnt]);
        if ((Cnt + 1) % 8 == 0)
        {
            printf(" ");
        }
        if ((Cnt + 1) % 16 == 0)
        {
            printf("\n");
        }
    }
    printf("\n");
}

VOID PrintInquiryData(PCHAR DataBuffer)
{
    PSCSI_ADAPTER_BUS_INFO adapterInfo;
    PSCSI_INQUIRY_DATA inquiryData;
    ULONG i, j;

    adapterInfo = (PSCSI_ADAPTER_BUS_INFO) DataBuffer;

    printf("Bus\n");
    printf("Num TID LUN Claimed String                       Inquiry Header\n");
    printf("--- --- --- ------- ---------------------------- -----------------------\n");

    for (i = 0; i < adapterInfo->NumberOfBuses; i++)
    {
        inquiryData = (PSCSI_INQUIRY_DATA) (DataBuffer + adapterInfo->BusData[i].InquiryDataOffset);
        while (adapterInfo->BusData[i].InquiryDataOffset)
        {
            printf(" %d   %d  %3d    %s    %.28s ",
                   i,
                   inquiryData->TargetId,
                   inquiryData->Lun, (inquiryData->DeviceClaimed) ? "Y" : "N", &inquiryData->InquiryData[8]);
            for (j = 0; j < 8; j++)
            {
                printf("%02X ", inquiryData->InquiryData[j]);
            }
            printf("\n");
            if (inquiryData->NextInquiryDataOffset == 0)
            {
                break;
            }
            inquiryData = (PSCSI_INQUIRY_DATA) (DataBuffer + inquiryData->NextInquiryDataOffset);
        }
    }

    printf("\n\n");
}

PUCHAR AllocateAlignedBuffer(ULONG size, ULONG Align)
{
    PUCHAR ptr;

    UINT_PTR Align64 = (UINT_PTR) Align;

    if (!Align)
    {
        ptr = malloc(size);
    }
    else
    {
        ptr = malloc(size + Align);
        ptr = (PUCHAR) (((UINT_PTR) ptr + Align64) & ~Align64);
    }
    if (ptr == NULL)
    {
        printf("Memory allocation error.  Terminating program\n");
        exit(1);
    }
    else
    {
        return ptr;
    }
}

VOID PrintStatusResults(BOOL status, DWORD returned, PSCSI_PASS_THROUGH_WITH_BUFFERS psptwb, ULONG length)
{
    ULONG errorCode;

    if (!status)
    {
        printf("Error: %d  ", errorCode = GetLastError());
        PrintError(errorCode);
        return;
    }
    if (psptwb->spt.ScsiStatus)
    {
        PrintSenseInfo(psptwb);
        return;
    }
    else
    {
        printf("Scsi status: %02Xh, Bytes returned: %Xh, ", psptwb->spt.ScsiStatus, returned);
        printf("Data buffer length: %Xh\n\n\n", psptwb->spt.DataTransferLength);
        PrintDataBuffer((PUCHAR) psptwb, length);
    }
}


//by tommy
VOID PrintStatusResults_Direct(BOOL status, DWORD returned, PSCSI_PASS_THROUGH_DIRECT_WITH_BUFFER psptdwb,
                               ULONG length)
{
    ULONG errorCode;

    if (!status)
    {
        printf("Error: %d  ", errorCode = GetLastError());
        PrintError(errorCode);
        return;
    }
    if (psptdwb->sptd.ScsiStatus)
    {
        //PrintSenseInfo(psptdwb);
        return;
    }
    else
    {
        printf("Scsi status: %02Xh, Bytes returned: %Xh, ", psptdwb->sptd.ScsiStatus, returned);
        printf("Data buffer length: %Xh\n\n\n", psptdwb->sptd.DataTransferLength);
        PrintDataBuffer((PUCHAR) psptdwb->sptd.Cdb, 16);
        PrintDataBuffer((PUCHAR) psptdwb, length);
        PrintDataBuffer((PUCHAR) psptdwb->sptd.DataBuffer, psptdwb->sptd.DataTransferLength);
    }
}


//UCHAR Cdb_read1fromlba0[16] = { SCSIOP_READ, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0 };
//UCHAR Cdb_write1tolba0[16] = { SCSIOP_WRITE, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0 };
//UCHAR Cdb_HTCCS_PHYINFO[16] = { 0Xe7, 0, 0, 0, 0, 0, 0, 0, 0x12, 0, 0, 0, 0, 0, 0, 0 };

BOOL Send_SCSI_Cmd(HANDLE hDEV, SCSI_CMD_BLOCK * cmd)
{
    BOOL status = 0;
    HANDLE fileHandle = hDEV;
    PUCHAR dataBuffer = NULL;
    SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER sptdwb;
    ULONG length = 0, errorCode = 0, returned = 0, sectorSize = 512;
    int i, j;

    if (cmd->len != 0)
        dataBuffer = USBbuffer;
    ZeroMemory(&sptdwb, sizeof(SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER));

    sptdwb.sptd.Length = sizeof(SCSI_PASS_THROUGH_DIRECT);
    sptdwb.sptd.PathId = 0;
    sptdwb.sptd.TargetId = 1;
    sptdwb.sptd.Lun = 0;
    sptdwb.sptd.SenseInfoLength = 24;
    sptdwb.sptd.DataTransferLength = cmd->len;
    sptdwb.sptd.TimeOutValue = 2;

    sptdwb.sptd.CdbLength = 16; //CDB10GENERIC_LENGTH; tommy fix this, as we use 16 bytes.
    sptdwb.sptd.DataIn = ((cmd->dir == 0) ? SCSI_IOCTL_DATA_OUT : SCSI_IOCTL_DATA_IN); //
    sptdwb.sptd.DataBuffer = dataBuffer;
    sptdwb.sptd.SenseInfoOffset = offsetof(SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER, ucSenseBuf);
    memcpy(sptdwb.sptd.Cdb, cmd->CDB, 16);

    length = sizeof(SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER);
    status = DeviceIoControl(fileHandle,
                             IOCTL_SCSI_PASS_THROUGH_DIRECT,
                             &sptdwb, length, &sptdwb, length, &returned, FALSE);

    if (gDebugLevel && cmd->dir == 1)
    {
        PrintDataBuffer((PUCHAR) sptdwb.sptd.Cdb, 16);

        //printf("DeviceIoControl send scsi cmd %d bytes, return status %d \n", length, status);
        //PrintDataBuffer((PUCHAR) psptdwb->sptd.DataBuffer, psptdwb->sptd.DataTransferLength);
        //PrintStatusResults_Direct(status, returned, &sptdwb, length);

        printf("Scsi status: %02Xh, Bytes returned: %Xh, ", sptdwb.sptd.ScsiStatus, returned);
        printf("Data buffer length: %Xh\n", sptdwb.sptd.DataTransferLength);
        //PrintDataBuffer((PUCHAR) psptdwb, length);
        //if (sptdwb.sptd.DataTransferLength)
        PrintDataBuffer((PUCHAR) sptdwb.sptd.DataBuffer, 16*4);
    }

    if (!status)
    {
        printf("Send_SCSI_Cmd Error: %d  ", errorCode = GetLastError());
        PrintError(errorCode);
        return FALSE;
    }
    if (sptdwb.sptd.ScsiStatus)
    {
        //PrintSenseInfo(&sptdwb);
        return FALSE;
    }
    return TRUE;

}


BOOL Send_USB_Cmd(HANDLE hDEV, SCSI_CMD_BLOCK * cmd)
{
    BOOL status = 0;
    HANDLE fileHandle = hDEV;
    ULONG length = 0, errorCode = 0, returned = 0, sectorSize = 512;
	SCSI_PASS_THROUGH_DIRECT_WITH_BUFFER sptdwb;
    int i, j;

    status = DeviceIoControl(fileHandle,
                             IOCTL_INTERNAL_USB_RESET_PORT,
                             &sptdwb, 0, &sptdwb, 0, NULL, (LPOVERLAPPED)NULL);

    if (!status)
    {
        printf("resetdevice Error: %d  ", errorCode = GetLastError());
        PrintError(errorCode);
        return FALSE;
    }

    return TRUE;

}

void process_zsp_cmd(int argc, char *argv[])
{
    PCBW pcbw = (PCBW) (scsicmd.CDB);

    if (strstr(argv[2], "reset"))
    {
        hDEV = Open_MyZdev();
        scsicmd.dir = 0;
        scsicmd.len = 0;
        pcbw->_CBWCB._MYZ_CMD2ZSP.OperationCode = MYZ_CMD_ZSP;
        pcbw->_CBWCB._MYZ_CMD2ZSP.cmd = MYZ_ZSPCMD_RESET;
        pcbw->_CBWCB._MYZ_CMD2ZSP.para1 = (UCHAR) atoi(argv[3]);
        Send_SCSI_Cmd(hDEV, &scsicmd);
    }
}


void process_lcd_cmd(int argc, char *argv[])
{
    PCBW pcbw = (PCBW) (scsicmd.CDB);

    if (strstr(argv[2], "refresh"))
    {
        hDEV = Open_MyZdev();
        scsicmd.dir = 0;
        scsicmd.len = 0;
        pcbw->_CBWCB._MYZ_CMD2LCD.OperationCode = MYZ_CMD_LCD;
        if (strstr(argv[3], "rgb"))
            pcbw->_CBWCB._MYZ_CMD2LCD.cmd = MYZ_LCDCMD_REFRESH_RGB;
        else if (strstr(argv[3], "yuv"))
            pcbw->_CBWCB._MYZ_CMD2LCD.cmd = MYZ_LCDCMD_REFRESH_YUV;
        else if (strstr(argv[3], "yuv422"))
            pcbw->_CBWCB._MYZ_CMD2LCD.cmd = MYZ_LCDCMD_REFRESH_YUV422;
        //pcbw->_CBWCB._MYZ_CMD2LCD.para1 = (UCHAR) atoi(argv[3]);
        Send_SCSI_Cmd(hDEV, &scsicmd);
    }
}

void process_listdev(int argc, char *argv[])
{
	char DeviceName[256] = "";
	
    HANDLE hDEV = OpenUsbDevice((LPGUID) & GUID_CLASS_I82930_BULK,
                                DeviceName);
    if (hDEV == INVALID_HANDLE_VALUE)
    {
        printf("Failed to found MyZ device !\n");
    }
    else
    {
        printf("Found MyZ device !\n");
    }
}

void process_resetdevice(int argc, char *argv[])
{
	char DeviceName[256] = "";
	HANDLE hDEV;
	
	if (argv[2] == NULL)
		return;

	devname_string[0] = 0;
	strcpy(devname_string, argv[2]);			
	
    hDEV = OpenUsbDevice((LPGUID) & GUID_CLASS_I82930_BULK,
                                DeviceName);
    if (hDEV == INVALID_HANDLE_VALUE)
    {
        printf("Failed to found MyZ device !\n");
    }
    else
    {
        printf("Found MyZ device !\n");
    }
	printf(" Ready to reset it !\n");
	Send_USB_Cmd(hDEV, 0);
	printf(" Reset done !\n");
}




/*
        printf("-rwmem (read/write) (dmem/imem/sdram/z51) (addr) (len) (file)\n");

*/
#define USB_EP_MAXLEN           (0x10000) //64K BYTES, limited by USB EP interface.

void process_rwmem(int argc, char *argv[])
{
    PCBW pcbw = (PCBW) (scsicmd.CDB);
    FILE *fp = 0;
    ULONG length, len, blocks, addr;

    pcbw->_CBWCB._MYZ_RWMEM.OperationCode = MYZ_CMD_RWMEM;

    if (strstr(argv[3], "dmem"))
        pcbw->_CBWCB._MYZ_RWMEM.target = MYZ_ZSPDMEM;
    else if (strstr(argv[3], "imem"))
        pcbw->_CBWCB._MYZ_RWMEM.target = MYZ_ZSPIMEM;
    else if (strstr(argv[3], "sdram"))
        pcbw->_CBWCB._MYZ_RWMEM.target = MYZ_SDRAM;
    else if (strstr(argv[3], "z51"))
        pcbw->_CBWCB._MYZ_RWMEM.target = MYZ_Z8051;

    if (strstr(argv[4], "0x") || strstr(argv[4], "0X"))
    {
        sscanf(&argv[4][2], "%lx", &addr);
    }
    else
    {
        addr = atoi(argv[4]);
    }
    pcbw->_CBWCB._MYZ_RWMEM.StartAddress = addr;

    if (strstr(argv[5], "0x") || strstr(argv[5], "0X"))
    {
        sscanf(&argv[5][2], "%lx", &length);
    }
    else
    {
        length = atoi(argv[5]) * 512;
    }

    if (strstr(argv[2], "r"))
    {
        pcbw->_CBWCB._MYZ_RWMEM.mode = MYZ_READ;
        scsicmd.dir = 1;
        fp = fopen(argv[6], "wb");
        if (fp == 0)
        {
            printf(" open file failed \n");
            return;
        }
        if (length == 0)
        {
            printf("Error: read to file, with len == 0\n");
        }
        length = ((length + 511) / 512) * 512;
    }
    else if (strstr(argv[2], "w"))
    {
        pcbw->_CBWCB._MYZ_RWMEM.mode = MYZ_WRITE;
        scsicmd.dir = 0;
        fp = fopen(argv[6], "rb");
        if (fp == 0)
        {
            printf(" open file failed \n");
            return;
        }
        if (length == 0)
        {
            fseek(fp, 0, SEEK_END);
            length = ftell(fp);
            length = ((length + 511) / 512) * 512;
            fseek(fp, 0, SEEK_SET);
        }
    }

    hDEV = Open_MyZdev();

    if (strstr(argv[2], "r"))
    {
        len = length;
        while (len > 0)
        {
            blocks = len > USB_EP_MAXLEN ? USB_EP_MAXLEN : len;
            pcbw->_CBWCB._MYZ_RWMEM.Length = (ULONG) blocks;
            scsicmd.len = blocks;
            printf(" block is %d bytes \n", blocks);
            Send_SCSI_Cmd(hDEV, &scsicmd);
            fwrite(USBbuffer, blocks, 1, fp);
            len -= blocks;
            pcbw->_CBWCB._MYZ_RWMEM.StartAddress += blocks;
        }
    }
    else if (strstr(argv[2], "w"))
    {
        len = length;
        while (len > 0)
        {
            blocks = len > USB_EP_MAXLEN ? USB_EP_MAXLEN : len;
            pcbw->_CBWCB._MYZ_RWMEM.Length = (ULONG) blocks;
            scsicmd.len = blocks;
            fread(USBbuffer, 1, blocks, fp);
            Send_SCSI_Cmd(hDEV, &scsicmd);
            len -= blocks;
            pcbw->_CBWCB._MYZ_RWMEM.StartAddress += blocks;
        }

#if 1		//update yuv fb.
        scsicmd.dir = 0;
        scsicmd.len = 0;
        pcbw->_CBWCB._MYZ_CMD2LCD.OperationCode = MYZ_CMD_LCD;
        pcbw->_CBWCB._MYZ_CMD2LCD.cmd = MYZ_LCDCMD_REFRESH_YUV;
        Send_SCSI_Cmd(hDEV, &scsicmd);
#endif
        
    }

    fclose(fp);

}


static void WriteBuff_Mem(unsigned char target, unsigned long addr, unsigned char *buff, unsigned long len)
{
    PCBW pcbw = (PCBW) (scsicmd.CDB);
    ULONG length, blocks;

    pcbw->_CBWCB._MYZ_RWMEM.OperationCode = MYZ_CMD_RWMEM;
    pcbw->_CBWCB._MYZ_RWMEM.target = target;
    pcbw->_CBWCB._MYZ_RWMEM.StartAddress = addr;

    length = len;
    length = ((length + 511) / 512) * 512;

    pcbw->_CBWCB._MYZ_RWMEM.mode = MYZ_WRITE;
    scsicmd.dir = 0;

    if (hDEV == 0)
    hDEV = Open_MyZdev();

    len = length;
    while (len > 0)
    {
        blocks = len > USB_EP_MAXLEN ? USB_EP_MAXLEN : len;
        pcbw->_CBWCB._MYZ_RWMEM.Length = (ULONG) blocks;
        scsicmd.len = blocks;
        //fread(USBbuffer, blocks, 1, fp);
        memcpy(USBbuffer, buff, blocks);
        Send_SCSI_Cmd(hDEV, &scsicmd);
        len -= blocks;
        buff += blocks;
        pcbw->_CBWCB._MYZ_RWMEM.StartAddress += blocks;
    }
}

static void ReadBuff_Mem(unsigned char target, unsigned long addr, unsigned char *buff, unsigned long len)
{
    PCBW pcbw = (PCBW) (scsicmd.CDB);
    ULONG length, blocks;

    pcbw->_CBWCB._MYZ_RWMEM.OperationCode = MYZ_CMD_RWMEM;
    pcbw->_CBWCB._MYZ_RWMEM.target = target;
    pcbw->_CBWCB._MYZ_RWMEM.StartAddress = addr;

    length = len;
    length = ((length + 511) / 512) * 512;

    pcbw->_CBWCB._MYZ_RWMEM.mode = MYZ_READ;
    scsicmd.dir = 1;

    if (hDEV == 0)
    hDEV = Open_MyZdev();

    len = length;
    while (len > 0)
    {
        blocks = len > USB_EP_MAXLEN ? USB_EP_MAXLEN : len;
        pcbw->_CBWCB._MYZ_RWMEM.Length = (ULONG) blocks;
        scsicmd.len = blocks;
        Send_SCSI_Cmd(hDEV, &scsicmd);
        memcpy(buff, USBbuffer, blocks);
        len -= blocks;
        buff += blocks;
        pcbw->_CBWCB._MYZ_RWMEM.StartAddress += blocks;
    }
}

// start from SDRAM_MEM_BASE,
#define SDRAM_IN_START      (0x00000)
#define SDRAM_IN_SIZE       (0x100000)  //Tommy: 不知为何, 每次传输大小超过1m字节就会出错.
#define SDRAM_OUT_SIZE      (0x100000)  //Tommy: 不知为何, 每次传输大小超过1m字节就会出错.    
#define FILE_OPRSIZE         (0x10000)

//#define DEBUG_FILEIO

void process_fileio(int argc, char *argv[])
{
    PCBW pcbw = (PCBW) (scsicmd.CDB);
    FILE *fpin = 0, *fpout = 0;
    char msgc_shadow[512*2];
    volatile PMSGXCHG pmsgc = (volatile PMSGXCHG) msgc_shadow;
    char *fbuff;
    unsigned long fin_len, lenin, readlen;
    unsigned long fout_len, lenout, writelen;
    unsigned long i, j;
    static short status_in_bak = 0, status_out_bak = 0;
    char bExit = 0;
    int bDataRead = 0;
    long wlen = 0;
    clock_t start;

    start= clock();
    
    hDEV = Open_MyZdev();
    gDebugLevel = 0;

    // Init MSGC
    ReadBuff_Mem(MYZ_Z8051, MSGC_XDATA_BASE, msgc_shadow, 512);

    while(pmsgc->magic_id != MKFCC('Z', 'S', 'P', 'X'))
        ReadBuff_Mem(MYZ_Z8051, MSGC_XDATA_BASE, msgc_shadow, 512);

    printf("Run loop %d times !\n", pmsgc->syslooptime);
    // 
    memset(pmsgc, 0, sizeof(MSGXCHG));
    pmsgc->magic_id = MKFCC('M', 'S', 'G', 'X');

    //config input buffer to ZSP.
    pmsgc->status_in = STATUS_INBUF_IDLE;
    pmsgc->bufin_addr = SDRAM_IN_START;   
    pmsgc->bufin_size = SDRAM_IN_SIZE;
    printf("Inbuff,  addr:%08lxH, size:%08lxH.\n", pmsgc->bufin_addr, pmsgc->bufin_size);

    //config output buffer from ZSP.
    pmsgc->status_out = STATUS_OUTBUF_IDLE;
    pmsgc->bufout_addr = SDRAM_IN_START+ SDRAM_IN_SIZE;
    pmsgc->bufout_size = SDRAM_OUT_SIZE;
    printf("Outbuff, addr:%08lxH, size:%08lxH.\n", pmsgc->bufout_addr, pmsgc->bufout_size);

    pmsgc->status = STATUS_PC_READY;        // only valid to zsp, after WriteBuff_Mem(MYZ_Z8051)
    WriteBuff_Mem(MYZ_Z8051, MSGC_XDATA_BASE, msgc_shadow, 512);

    //open fiels.
    fpin = fopen(argv[2], "rb");
    if (fpin == 0)
    {
        printf(" open file failed \n");
        return;
    }
    fseek(fpin, 0, SEEK_END);
    fin_len = ftell(fpin);
    fseek(fpin, 0, SEEK_SET);
    printf("Open file %s, file size is %d.\n", argv[2], fin_len);

    fpout = fopen(argv[3], "wb");
    if (fpout == 0)
    {
        printf(" open file failed \n");
        return;
    }

    fbuff = malloc(FILE_OPRSIZE + 10);
    lenin = 0;

    printf(" ZSP ready ? .... ");
    //wait for zsp ready to go.
    while(pmsgc->status != STATUS_ZSP_READY)
        ReadBuff_Mem(MYZ_Z8051, MSGC_XDATA_BASE, msgc_shadow, 512);

    printf(" OK, Go !\n");
    //go......
    while (1)
    {
        //printf("wait key ");
        //getchar();
        //printf(", got !\n");
        
        ReadBuff_Mem(MYZ_Z8051, MSGC_XDATA_BASE, msgc_shadow, 512);
#ifdef DEBUG_FILEIO
        if (status_in_bak != pmsgc->status_in)
        {
            status_in_bak = pmsgc->status_in;
            printf(" status_in:0x%x.\n ", status_in_bak);
        }
        if (status_out_bak != pmsgc->status_out)
        {
            status_out_bak = pmsgc->status_out;
            printf(" status_out:0x%x.\n ", status_out_bak);
        }        
#endif
        // Input data to ZSP.
        if ( (lenin < fin_len)
            && (pmsgc->status_in == STATUS_INBUF_ZSP_READ_FINISHED))
        {
            i = 0;
            gDebugLevel = 0;
            printf("w");
            while (i < SDRAM_IN_SIZE)
            {
                readlen = fread(fbuff, 1, FILE_OPRSIZE, fpin);
                if (readlen == 0)
                    break;
                if (gDebugLevel)
                    printf(" (w%xh), \n", readlen);
                WriteBuff_Mem(MYZ_SDRAM, pmsgc->bufin_addr + i, fbuff, readlen);
                i += readlen;
            }
            //i = ((i + 1)/2) *2;     // align to words.
            pmsgc->bufin_len = (i)/2; //in words.
            if (readlen != 0) // || bDataRead == 0)
            {
                pmsgc->status_in = STATUS_INBUF_PC_FILLED;
            }
            else
            {
                //if (gDebugLevel)
                printf("\n Sent STATUS_INBUF_PC_FILLED_LASTONE.\n");
                if (bExit == 0)
                    bExit = 1;
                pmsgc->status_in = STATUS_INBUF_PC_FILLED_LASTONE;
            }

            //printf(" new status_in:0x%x..... ", pmsgc->status_in);
            WriteBuff_Mem(MYZ_Z8051, MSGC_XDATA_BASE, msgc_shadow, 512);

            //ReadBuff_Mem(MYZ_Z8051, MSGC_XDATA_BASE, msgc_shadow, 512);
            //printf(" 0x%x.\n ", pmsgc->status_in);
            
            lenin += pmsgc->bufin_len*2;
            gDebugLevel = 0;

        //getchar();
            
        }

        // Output data from ZSP.
        if (pmsgc->status_out == STATUS_OUTBUF_ZSP_FILLED
            || pmsgc->status_out == STATUS_OUTBUF_ZSP_FILLED_LASTONE)
        {
            i = 0;
            bDataRead = 1;
            printf("r");
            gDebugLevel = 0;
            if (pmsgc->status_out == STATUS_OUTBUF_ZSP_FILLED_LASTONE)
            {
                printf("\n Got STATUS_OUTBUF_ZSP_FILLED_LASTONE.\n");
                bExit = 2;
            }
            while (i < pmsgc->bufout_len*2)
            {
                //printf(" %d, %d \n", pmsgc->bufout_len*2 , i);
                j = ((pmsgc->bufout_len*2 - i) > FILE_OPRSIZE)? FILE_OPRSIZE : (pmsgc->bufout_len*2 - i);
                ReadBuff_Mem(MYZ_SDRAM, pmsgc->bufout_addr + i, fbuff, j);
                if (gDebugLevel)
                    printf(" (r%xh), ", j);
                fwrite(fbuff, 1, j, fpout);
                wlen += j;
                i += j;
            }
            //tommy: add a ReadBuff_Mem() here maybe more stable.
            pmsgc->status_out = STATUS_OUTBUF_PC_READ_FINISHED;
            WriteBuff_Mem(MYZ_Z8051, MSGC_XDATA_BASE, msgc_shadow, 512);
            gDebugLevel = 0;
        }

        if (bExit == 2)     // && pmsgc->status_out == STATUS_OUTBUF_ZSP_FILLED)
            break;

        //if (lenin >= fin_len && bDataRead == 0) // send out all data, but no data in, means big Error.
        //    break;

        //if (pmsgc->magic_id == MKFCC('E', 'X', 'I', 'T'))
        //    break;
		Sleep(10);

        //printf(" %d >= %d , %d\n", lenin, fin_len, bExit);

    }

    start = clock() -start;
    printf("\n** Entire time: %.2f sec, Speed is %.2f M/s\n",  
                (float) start / (float) CLOCKS_PER_SEC,
                (wlen/1000000)/((float) start / (float) CLOCKS_PER_SEC));
    
    //memset(pmsgc, 0, sizeof(MSGXCHG));
    //WriteBuff_Mem(MYZ_Z8051, MSGC_XDATA_BASE, msgc_shadow, 512);

    printf(" process_fileio exit. \n");
    free(fbuff);
    fclose(fpin);
    fclose(fpout);

}


/*++
Routine Description:

    Entry point to rwbulk.exe
    Parses cmdline, performs user-requested tests

Arguments:

    argc, argv  standard console  'c' app arguments

Return Value:

    Zero

--*/
int _cdecl main(int argc, char *argv[])
{
    ULONG i, j;
    //clock_t start, finish;

    ZeroMemory(&scsicmd, sizeof(SCSI_CMD_BLOCK));
    ZeroMemory(USBbuffer, USBBUF_SIZE);
    //parse(argc, argv);

    if (argc < 2)               // give usage if invoked with no parms
    {
        usage();
        return 1;
    }

	devname_string[0] = 0;
	strcpy(devname_string, DEVNAME_MATCH);
	
    if (argv[1][0] == '-' || argv[1][0] == '/')
    {
        if (strstr(argv[1], "zspcmd"))
        {
            process_zsp_cmd(argc, argv);
        }
        if (strstr(argv[1], "rwmem"))
        {
            process_rwmem(argc, argv);
        }
        if (strstr(argv[1], "fileio"))
        {
            process_fileio(argc, argv);
        }
        if (strstr(argv[1], "lcdcmd"))
        {
            process_lcd_cmd(argc, argv);
        }
        if (strstr(argv[1], "list"))
        {
            process_listdev(argc, argv);
        }
        if (strstr(argv[1], "resetdevice"))
        {
			process_resetdevice(argc, argv);
		}

    }

    CloseHandle(hDEV);
    return 0;
}
