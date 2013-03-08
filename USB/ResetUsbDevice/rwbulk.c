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

#define DEBUG
#define DEVNAME_MATCH  "vid_0bb4"
//#define OPEN_DEVIE_FAST               //Open faster, using CreateFile.

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
    printf("devname:%s\ndevname_string:%s\n", devName, devname_string);
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
        printf("OpenOneDevice():Device handle is %XH\n", hOut);

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
        printf("Failed to found AndroidBootLoader device !\n");
    }
    else
    {
        printf("Found AndroidBootLoader device !\n");
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
        printf("\n*********** USB Reset v1.0 **********\n");
        printf("Usage for Reset Android Boot Loader:\n");
        printf("-list\n\tList all the devices until find the matched one.\n");
        printf("-reset devicestring\n\tSend ResetPort cmd to matched device.\n");
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


BOOL Send_USB_Cmd(HANDLE hDEV, SCSI_CMD_BLOCK * cmd)
{
    BOOL status = 0;
    HANDLE fileHandle = hDEV;
    ULONG length = 0, errorCode = 0, returned = 0, sectorSize = 512;
    int i, j;

    status = DeviceIoControl(fileHandle,
                             IOCTL_INTERNAL_USB_RESET_PORT,
                             0, 0, 0, 0, NULL, (LPOVERLAPPED)NULL);

    if (!status)
    {
        printf("reset Error: %d  ", errorCode = GetLastError());
        //PrintError(errorCode);
        return FALSE;
    }

    return TRUE;

}


void process_listdev(int argc, char *argv[])
{
    char DeviceName[256] = "";

    HANDLE hDEV = OpenUsbDevice((LPGUID) & GUID_CLASS_I82930_BULK,
                                DeviceName);
    if (hDEV == INVALID_HANDLE_VALUE)
    {
        printf("Failed to found AndroidBootLoader device !\n");
    }
    else
    {
        printf("Found AndroidBootLoader device !\n");
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
        printf("Failed to found AndroidBootLoader device !\n");
    }
    else
    {
        printf("Found AndroidBootLoader device !\n");
    }
    printf(" Ready to reset it !\n");
    Send_USB_Cmd(hDEV, 0);
    printf(" Reset done !\n");
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
        if (strstr(argv[1], "list"))
        {
            process_listdev(argc, argv);
        }
        if (strstr(argv[1], "reset"))
        {
            process_resetdevice(argc, argv);
        }

    }

    CloseHandle(hDEV);
    return 0;
}
