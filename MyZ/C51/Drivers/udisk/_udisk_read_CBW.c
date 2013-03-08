//
// Copyright (C) 2006-2008, HTCCS
//
// File Name:
//      udisk_read_CBW.c
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
#include "utils.h"
#include "rbc.h"


bool_t udisk_read_CBW(void)
{
    u16_t length;
    u8_t count, *pCBW = (u8_t*)&CBW;

	//printf("<");

    __udisk_CBW_valid = FALSE;
    if (_usbd_reset)
    {
        // flush endpoint
        EA = 0;
        _usbd_reset = FALSE;
        EA = 1;
    }

    if (_usbd_rx_done)
    {
		//printf("!");
        EA = 0;
        _usbd_rx_done = FALSE;
        length = read_mreg16(EP2_AVAIL_CNT);
		//printf(" EP2: %d bytes \n", length);
        count  = 0;
        if (length >= 31)
        {
	        // only use the 30 bytes.	
            for (; count<31; count++)
			{
                *pCBW++ = read_mreg(EP2_DATA_BUF);
				//printf("0x%bx, ", *(pCBW-1));
			}
            length -= count;
        }
        // discard the remain bytes.
        for (; length>0; length--)
            read_mreg(EP2_DATA_BUF);
        EA = 1;

		//printf("\nCBW: 0x%lx, len:%bd, count:%bd.  \n", CBW.dCBWSignature, CBW.bCBWCBLength, count);
        if (CBW.dCBWSignature == CBW_SIGNATURE
              && CBW.bCBWCBLength <= 16 && count == 31)
        {
			//printf("@");
            CBW.dCBWDataTransferLength = _swap32(CBW.dCBWDataTransferLength);
            __udisk_CBW_valid = TRUE;
        }
		else
		{
			//_usbd_rx_done = TRUE;
			
			//printf(" not valid CBW \n");
		}
    }
    else
    {
		//printf("#");
        EA = 0;
        if (read_mreg(USB_IRQ_STAT) & (1<<3))
        {
            write_mreg16(USB_IRQ_STAT, (1<<3));
            _usbd_suspend = TRUE;
        }
        EA = 1;
    }

	//printf(">");

    return __udisk_CBW_valid;
}
