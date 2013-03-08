//
// Copyright (C) 2006-2008, HTCCS
//
// File Name:
//      udisk_process_CBW.c
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
#include "ht3001.h"
#include "drivers.h"
#include "rbc.h"


bool_t udisk_process_CBW(void)
{
    if (__udisk_CBW_valid)
    {
        __udisk_IN_stall = FALSE;
        __udisk_OUT_stall = FALSE;

        if (CBW.bCBWLUN > MAX_LUN)
        {
            __udisk_stall_usb();
            __udisk_process_CSW(0UL, CSW_PHASE_ERROR);
            __udisk_build_sense(0x05, 0x25, 0x00);
        }
        else
        {
			//printf("\n CBW.OperationCode is 0x%bx on LUN:%bd\n", (u8_t)CBW.OperationCode, (u8_t)CBW.bCBWLUN);
            switch (CBW.OperationCode)
            {
            case RBC_CMD_READ10:
                __RBC_Read10();
                break;

            case RBC_CMD_WRITE10:
                __RBC_Write10();
                break;

            case RBC_CMD_VERIFY10:
                __RBC_Verify10();
                break;

            case RBC_CMD_READCAPACITY:
                __RBC_ReadCapacity();
                break;

            case RBC_CMD_STARTSTOPUNIT:
                __RBC_StartStopUnit();
                break;

            case SPC_CMD_INQUIRY:
                __SPC_Inquiry();
                break;

            case SPC_CMD_TESTUNITREADY:
                __SPC_TestUnitReady();
                break;

            case SPC_CMD_READFORMATCAPACITY:
                __SPC_ReadFormatCapacity();
                break;

            case SPC_CMD_MODESENSE6:
                __SPC_ModeSense6();
                break;

            case SPC_CMD_MODESELECT6:
                __SPC_ModeSelect6();
                break;

            case SPC_CMD_PREVENTALLOWMEDIAREMOVAL:
                __SPC_PreventAllowMediaRemoval();
                break;

            case SPC_CMD_REQUESTSENSE:
                __SPC_RequestSense();
                break;

            /////////// MYZ /////////
            case MYZ_CMD_RWMEM:
                __MYZ_ProcCmd_rwmem();
                break;

            case MYZ_CMD_ZSP:
                __MYZ_ProcCmd_zsp();
                break;

            case MYZ_CMD_LCD:
                __MYZ_ProcCmd_lcd();
                break;

            //case MYZ_CMD_FILEIO:
            //    __MYZ_ProcCmd_fileio();
            //    break;                

            default:
                __udisk_stall_usb();
                __udisk_process_CSW(0, CSW_FAILED);
                __udisk_build_sense(0x05, 0x20, 0x00);
                break;
            }
        }
        if (__udisk_IN_stall)
        {
            EA = 0;
            write_mreg16(EP1_IRQ_STAT, (1<<9));
            write_mreg16(EP1_RSP_SC, read_mreg16(EP1_RSP_SC)|(1<<4));
            while (!(read_mreg16(EP1_IRQ_STAT) & (1<<9)));
            EA = 1;
            while (read_mreg16(EP1_RSP_SC) & (1<<4));
        }
        else if (__udisk_OUT_stall)
        {
            EA = 0;
            write_mreg16(EP2_IRQ_STAT, (1<<9));
            write_mreg16(EP2_RSP_SC, read_mreg16(EP2_RSP_SC)|(1<<4)|(1<<0));
            while (!(read_mreg16(EP2_IRQ_STAT) & (1<<9)));
            EA = 1;
            while (read_mreg16(EP2_RSP_SC) & (1<<4));
            _usbd_rx_done = FALSE;
        }
        __udisk_write_usb((u8_t*)&CSW, 13);
        return TRUE;
    }

    return FALSE;
}
