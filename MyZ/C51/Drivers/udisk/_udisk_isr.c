//
// Copyright (C) 2006-2008, HTCCS
//
// File Name:
//      usbd_isr.c
// Author:
//      luzl
// Date:
//      02/28/2008
// Description:
//      USB MASS STORAGE
// History:
//      Date        Author      Modification
//      02/28/2008  luzl        Created.
//
#include "ht3001.h"
#include "drivers.h"
#include "stdio.h"

//
// Endpoint packet size
//
#define CTRL_PSIZE          64
//
// Descriptor Type
//
#define DT_DEVICE           1
#define DT_CONFIG           2
#define DT_STRING           3
#define DT_INTERFACE        4
#define DT_ENDPOINT         5
#define DT_QUALIFIER        6
#define DT_OTHER            7
//
// Request Type
//
#define RT_DEVICE           0
#define RT_INTERFACE        1
#define RT_ENDPOINT         2
//
// Request Command
//
#define GET_STATUS          0
#define CLEAR_FEATURE       1
#define RESERVED0           2
#define SET_FEATURE         3
#define RESERVED1           4
#define SET_ADDRESS         5
#define GET_DESCRIPTOR      6
#define SET_DESCRIPTOR      7
#define GET_CONFIGURATION   8
#define SET_CONFIGURATION   9
#define GET_INTERFACE       10
#define SET_INTERFACE       11
#define SYNCH_FRAME         12
#define GET_MAX_LUN         254
#define MASS_STORAGE_RESET  255


//
// Device Descriptor
//
static ALIGN CODE u8_t DeviceDescriptor[] =
{
    0x12,                   // Size of this descriptor in bytes.
    DT_DEVICE,              // DEVICE Descriptor Type.
    0x00, 0x02,             // USB specification release number in BCD.
    0x00,                   // Class is specified in the interface descriptor.
    0x00,                   // Subclass is specified in the interface descriptor.
    0x00,                   // Protocol is specified in the interface descriptor.
    CTRL_PSIZE,             // Maximum packet size for endpoint zero. (only 8, 16, 32, or 64
                            // are valid (08h, 10h, 20h, 40h)).
    0x73, 0x19,             // Vendor ID (assigned by the USB-IF).
    0x05, 0x12,             // Product ID (assigned by the manufacturer).
    0x00, 0x01,             // Device release number in BCD.
    0x01,                   // Index of string descriptor describing the manufacturer.
    0x02,                   // Index of string descriptor describing this product.
    0x03,                   // Index of string descriptor describing the device's serial number.
    0x01                    // Number of possible configurations.
};

static ALIGN CODE u8_t QualifierDescriptor[] =
{
    0x0a,                   // Size of this descriptor in bytes.
    DT_QUALIFIER,           // DT_QUALIFIER Descriptor Type.
    0x00, 0x02,             // USB specification release number in BCD.
    0x00,                   // Class is specified in the interface descriptor.
    0x00,                   // Subclass is specified in the interface descriptor.
    0x00,                   // Protocol is specified in the interface descriptor.
    CTRL_PSIZE,             // Maximum packet size for endpoint zero. (only 8, 16, 32, or 64
                            // are valid (08h, 10h, 20h, 40h)).
    0x01,                   // Number of possible configurations.
    0x00                    // Reserved
};

//
// Configuration Descriptor
//
static ALIGN u8_t ConfigurationDescriptor[] =
{
    0x09,                   // Size of this descriptor in bytes.
    DT_CONFIG,              // CONFIGURATION Descriptor Type.
    0x20, 0x00,             // Total length of data returned for this configuration. Includes
                            // the combined length of all descriptors (configuration, interface,
                            // endpoint, and class- or vendor-specific) returned for this
                            // configuration.
    0x01,                   // Number of interfaces supported by this configuration.
    0x01,                   // Value to use as an argument to the SetConfiguration() request
                            // to select this configuration.
    0x00,                   // Index of string descriptor describing this configuration.
    0x80,                   // Configuration characteristics:
                            //     Bit   Description
                            //     7     Reserved (set to one)
                            //     6     Self-powered
                            //     5     Remote Wakeup
                            //     4..0  Reserved (reset to zero)
    0xfa,                   // Maximum power consumption of the USB device from the bus
                            // in this specific configuration when the device is fully
                            // operational. Expressed in 2mA units (i.e. 50 = 100mA)
//
// Interface Descriptor
//
    0x09,                   // Size of this descriptor in bytes.
    DT_INTERFACE,           // INTERFACE Descriptor Type.
    0x00,                   // Number of interface. Zero-based value identifying the index
                            // in the array of concurrent interfaces supported by this
                            // configuration.
    0x00,                   // Value used to select alternate setting for the interface
                            // identified in the prior field.
    0x02,                   // Number of endpoints used by this interface (excluding
                            // endpoint zero).
    0x08,                   // MASS STORAGE Class. 0x08
    0x06,                   // SCSI-2. 0x06
    0x50,                   // USB Mass Storage Class Bulk-Only Transport. 0x50
    0x00,                   // Index to string descriptor describing this interface.
//
// Endpoint Descriptor
//
    0x07,                   // Size of this descriptor in bytes.
    DT_ENDPOINT,            // ENDPOINT Descriptor Type.
    0x81,                   // The address of this endpoint on the USB device. The address is
                            // encoded as follows.
                            //     Bit  Description
                            //     3..0 The endpoint number
                            //     6..4 Reserved, set to 0
                            //     7    1 = In
    0x02,                   // This is a Bulk endpoint.
    0x40,                   // Maximum packet size. Shall be 8, 16, 32 or 64 bytes (08h,
    0x00,                   // 10h, 20h, 40h).
    0x00,                   // Does not apply to Bulk endpoints.
//
// Endpoint Descriptor
//
    0x07,                   // Size of this descriptor in bytes.
    DT_ENDPOINT,            // ENDPOINT Descriptor Type.
    0x02,                   // The address of this endpoint on the USB device. The address is
                            // encoded as follows.
                            //     Bit  Description
                            //     3..0 The endpoint number
                            //     6..4 Reserved, set to 0
                            //     7    1 = In
    0x02,                   // This is a Bulk endpoint.
    0x40,                   // Maximum packet size. Shall be 8, 16, 32 or 64 bytes (08h,
    0x00,                   // 10h, 20h, 40h).
    0x00                    // Does not apply to Bulk endpoints.
};

//
// LANGID String Descriptor
//
static ALIGN CODE u8_t StringDescriptor[] =
{
    0x04,                   // Size of this descriptor in bytes.
    DT_STRING,              // STRING Descriptor Type.
    0x09, 0x04              // LANGID code zero.
};

//
// Vendor String Descriptor
//
static ALIGN CODE u8_t VendorString[] =
{
    0x13,                   // Size of this descriptor in bytes.
    DT_STRING,              // STRING Descriptor Type.
    'M',  0x00,             // 'HTCCS   '
    'y',  0x00,
    'Z',  0x00,
    '@',  0x00,
    '2',  0x00,
    '0',  0x00,
    '1',  0x00,
    '0',  0x00,
    ' ',  0x00
};

//
// Product String Descriptor
//
static ALIGN CODE u8_t ProductString[] =
{
    0x1e,                   // Size of this descriptor in bytes.
    DT_STRING,              // STRING Descriptor Type.
    'U',  0x00,             // 'USB Flash Disk'
    'S',  0x00,
    'B',  0x00,
    '2',  0x00,
    'Z',  0x00,
    'S',  0x00,
    'P',  0x00,
    ' ',  0x00,
    'B',  0x00,
    'r',  0x00,
    'i',  0x00,
    'd',  0x00,
    'g',  0x00,
    'e',  0x00
};

//
// Serial String Descriptor
//
static ALIGN CODE u8_t SerialString[] =
{
    0x0a,                   // Size of this descriptor in bytes.
    DT_STRING,              // STRING Descriptor Type.
    '1',  0x00,             // '1.00'
    '.',  0x00,
    '0',  0x00,
    '0',  0x00
};

//
// get max lun
//
extern u8_t __udisk_get_lun(void);
//
// reset flag
//
extern bool_t _usbd_reset;
//
// suspended flag
//
extern bool_t _usbd_suspend;
//
// tx flag
//
extern bool_t _usbd_tx_done;
//
// rx flag
//
extern bool_t _usbd_rx_done;
//
// dma flag
//
extern bool_t _usbd_dma_done;
//
// packet size
//
extern u16_t  _usbd_pkt_size;
//
// Received setup data
//
static u8_t  bmRequestType;
static u8_t  bRequest;
static u16_t wValue;
static u16_t wIndex;
static u16_t wLength;
//
// Send descriptor helper
//
static u8_t* DescriptorType;
static u8_t  DescriptorLength;
static u8_t  DescriptorIndex;
//
// control ep clear nak
//
#define clear_nak() write_mreg16(CEP_CTRL_STAT, 0)
//
// control ep send the stall signal to host
//
#define send_stall() write_mreg16(CEP_CTRL_STAT, (1<<1))
//
// control ep send zero packet to host
//
#define send_zero() write_mreg16(CEP_CTRL_STAT, (1<<2))
//
// control ep send data packet to host
//
static void send_packet(u8_t *buffer, u16_t size)
{
    u16_t count = size;
    do
    {
        write_mreg(CEP_DATA_BUF, *buffer++);
    } while (--count > 0);
    write_mreg16(IN_TRNSFR_CNT, size);
    clear_nak();
}


//
// set packet size of the configuration decsriptor
//
static void set_packet_size(u16_t size)
{
    ConfigurationDescriptor[22] = size&0xff;
    ConfigurationDescriptor[23] = size>>8;
    ConfigurationDescriptor[29] = size&0xff;
    ConfigurationDescriptor[30] = size>>8;
    _usbd_pkt_size = size;
}

//
// Function:
//      reserved()
// Description:
//      保留请求号, 不支持该类请求.
// Parameter:
//      void
// Return:
//      void
//
static void reserved(void)
{
    send_stall();
}

//
// Function:
//      clear_feature()
// Description:
//      响应 Get Clear Feature 请求, Clear Feature 后, 返回状态到主机.
// Parameter:
//      void
// Return:
//      void
//
static void clear_feature(void)
{
    if (wLength == 0)
    {
        switch (bmRequestType)
        {
        case RT_DEVICE:     // no effect on device
            break;

        case RT_INTERFACE:  // no effect on interface
            if (wIndex == 0)
            {
                // return interface status
                send_zero();
                return;
            }
            break;

        case RT_ENDPOINT:   // clear endpoint feature
            if (wValue == 0)
            {
                if ((wIndex&0x0f) == 1)
                {
                    // Enable endpoint 1
                    write_mreg16(EP1_RSP_SC, 0);
                    // return endpoint 1 status
                    send_zero();
                    return;
                }

                if ((wIndex&0x0f) == 2)
                {
                    // Enable endpoint 2
                    write_mreg16(EP2_RSP_SC, 0);
                    // return endpoint 2 status
                    send_zero();
                    return;
                }
            }
            break;
        }
    }

    // return stall
    send_stall();
}

//
// Function:
//      get_configuration()
// Description:
//      响应 Get Configuration 请求, 返回Configuration状态到主机.
// Parameter:
//      void
// Return:
//      void
//
static void get_configuration(void)
{
    u8_t configuration;

    if (wValue == 0 && wIndex == 0 && wLength == 1)
    {
        configuration = (u8_t)read_mreg16(EP1_CFG)&(1<<0);
        send_packet((u8_t*)&configuration, 1);
        return;
    }

    // return stall
    send_stall();
}

//
// Function:
//      get_descriptor()
// Description:
//      响应 Get Descriptor 请求, 返回请求的描述符到主机.
// Parameter:
//      void
// Return:
//      void
//
static void get_descriptor(void)
{
    DescriptorType   = 0;
    DescriptorLength = 0;
    DescriptorIndex  = 0;

    switch (wValue >> 8)
    {
    case DT_DEVICE: // Request device descriptor
        DescriptorType = DeviceDescriptor;
        DescriptorLength = sizeof(DeviceDescriptor);
        break;

    case DT_CONFIG: // Request configuration descriptor
        ConfigurationDescriptor[1] = DT_CONFIG;
        DescriptorType = ConfigurationDescriptor;
        DescriptorLength = sizeof(ConfigurationDescriptor);
        break;

    case DT_STRING: // Request string descriptor
        switch (wValue & 0xff)
        {
        case 0:     // Request language id
            DescriptorType = StringDescriptor;
            DescriptorLength = sizeof(StringDescriptor);
            break;

        case 1:     // Request vendor string
            DescriptorType = VendorString;
            DescriptorLength = sizeof(VendorString);
            break;

        case 2:     // Request product string
            DescriptorType = ProductString;
            DescriptorLength = sizeof(ProductString);
            break;

        case 3:     // Request serial string
            DescriptorType = SerialString;
            DescriptorLength = sizeof(SerialString);
            break;

        default:
            // return stall
            send_stall();
            return;
        }
        break;

    case DT_QUALIFIER:
        DescriptorType = QualifierDescriptor;
        DescriptorLength = sizeof(QualifierDescriptor);
        break;

    case DT_OTHER:
        ConfigurationDescriptor[1] = DT_OTHER;
        DescriptorType = ConfigurationDescriptor;
        DescriptorLength = sizeof(ConfigurationDescriptor);
        break;

    default:
        // return stall
        send_stall();
        return;
    }

    // Send first packet of descriptor
    if (wLength > DescriptorLength)
        wLength = DescriptorLength;
    else
        DescriptorLength = wLength;
    if (wLength > CTRL_PSIZE)
        wLength = CTRL_PSIZE;
    send_packet((u8_t*)DescriptorType, wLength);
}

//
// Function:
//      get_interface()
// Description:
//      响应 Get Interface 请求, 返回接口索引到主机.
// Parameter:
//      void
// Return:
//      void
//
static void get_interface(void)
{
    u8_t interface;

    if (wValue == 0 && wLength == 1)
    {
        if (wIndex == 0)
        {
            interface = 0;
            send_packet((u8_t*)&interface, 1);
            return;
        }
    }

    // return stall
    send_stall();
}

//
// Function:
//      get_status()
// Description:
//      响应 Get Status 请求, 返回相应请求对象的状态到主机.
// Parameter:
//      void
// Return:
//      void
//
static void get_status(void)
{
    u8_t status[2];

    status[1] = 0;
    if (wValue == 0 && wLength == 2)
    {
        switch (bmRequestType)
        {
        case RT_DEVICE:
            // return device status
            status[0] = 1;
            send_packet((u8_t*)&status, 2);
            return;

        case RT_INTERFACE:
            if (wIndex == 0)
            {
                // return interface status
                status[0] = 0;
                send_packet((u8_t*)&status, 2);
                return;
            }
            break;

        case RT_ENDPOINT:
            if ((wIndex&0x0f) == 0)
            {
                // return endpoint 1 status
                status[0] = 0;
                send_packet((u8_t*)&status, 2);
                return;
            }

            if ((wIndex&0x0f) == 1)
            {
                // return endpoint 1 status
                if (read_mreg16(EP1_RSP_SC) & (1<<4))
                    status[0] = 1;
                else
                    status[0] = 0;
                send_packet((u8_t*)&status, 2);
                return;
            }

            if ((wIndex&0x0f) == 2)
            {
                // return endpoint 2 status
                if (read_mreg16(EP2_RSP_SC) & (1<<4))
                    status[0] = 1;
                else
                    status[0] = 0;
                send_packet((u8_t*)&status, 2);
                return;
            }
            break;
        }
    }

    // return stall
    send_stall();
}

//
// Function:
//      set_address()
// Description:
//      响应 Set Address 请求, 设置USB设备地址.
// Parameter:
//      void
// Return:
//      void
//
static void set_address(void)
{
    if (wValue < 0x80 && wIndex == 0 && wLength == 0)
    {
        write_mreg16(CEP_IRQ_STAT, (1<<10));
        send_zero();
        while (!(read_mreg16(CEP_IRQ_STAT) & (1<<10))) {}
         // setup USB address
        write_mreg16(USB_ADDR, wValue & 0x7f);
    }
}

//
// Function:
//      set_configuration()
// Description:
//      响应 Set Configuration 请求, 根据 Configuration 的值,
//    激活或阻止数据传输端点.
// Parameter:
//      void
// Return:
//      void
//
static void set_configuration(void)
{
    if (wIndex == 0 && wLength == 0)
    {
        send_zero();
        if (wValue)
        {
            // activate endpoint 1
            write_mreg16(EP1_CFG, (1<<0)|(1<<1)|(1<<3)|(1<<4));
            // activate endpoint 2
            write_mreg16(EP2_CFG, (1<<0)|(1<<1)|(0<<3)|(2<<4));
        }
        else
        {
            // inactivate endpoint 1 & 2
            write_mreg16(EP1_CFG, (0<<0)|(1<<1)|(1<<3)|(1<<4));
            write_mreg16(EP2_CFG, (0<<0)|(1<<1)|(0<<3)|(2<<4));
        }
        return;
    }

    // return stall
    send_stall();
}

//
// Function:
//      set_descriptor()
// Description:
//      响应 Set Decriptor 请求, 不支持该请求.
// Parameter:
//      void
// Return:
//      void
//
static void set_descriptor(void)
{
    // unsupported, return stall
    send_stall();
}

//
// Function:
//      set_feature()
// Description:
//      响应 Set Feature 请求, Set Feature 后, 并返回其状态到主机.
// Parameter:
//      void
// Return:
//      void
//
static void set_feature(void)
{
    if (wLength == 0)
    {
        switch (bmRequestType)
        {
        case RT_DEVICE:         // no effect on device
            if (wValue == 0)
            {
                send_zero();
                return;
            }
            break;

        case RT_INTERFACE:      // no effect on interface
            if (wIndex == 0)
            {
                // return interface status
                send_zero();
                return;
            }
            break;

        case RT_ENDPOINT:
            if (wValue == 0)
            {
                if ((wIndex&0x0f) == 1)
                {
                    // Stop endpoint 1
                    write_mreg16(EP1_RSP_SC, read_mreg16(EP1_RSP_SC)|(1<<4));
                    while (!(read_mreg16(EP1_RSP_SC) & (1<<4)));
                    // return endpoint 1 status
                    send_zero();
                    return;
                }

                if ((wIndex&0x0f) == 2)
                {
                    // Stop endpoint 2
                    write_mreg16(EP2_RSP_SC, read_mreg16(EP2_RSP_SC)|(1<<4)|(1<<0));
                    while (!(read_mreg16(EP2_RSP_SC) & (1<<4)));
                    // return endpoint 2 status
                    send_zero();
                    return;
                }
            }
            break;
        }
    }

    // return stall
    send_stall();
}

//
// Function:
//      set_interface()
// Description:
//      响应 Set Interface 请求, 不支持该请求.
// Parameter:
//      void
// Return:
//      void
//
static void set_interface(void)
{
    if (wValue == 0 && wLength == 0)
    {
        if (wIndex == 0 )
        {
            send_zero();
            return;
        }
    }

    // unsupported, return stall
    send_stall();
}

//
// Function:
//      synch_frame()
// Description:
//      响应 Synch Frame 请求, 不支持该请求.
// Parameter:
//      void
// Return:
//      void
//
static void synch_frame(void)
{
    // unsupported, return stall
    send_stall();
}

//
// Function:
//      get_max_lun()
// Description:
//      响应 Get Max LUN 请求, 返回磁盘数.
// Parameter:
//      void
// Return:
//      void
//
static void get_max_lun(void)
{
    u8_t max_lun;

    if (wValue == 0 && wLength == 1)
    {
        if (wIndex == 0)
        {
            // Max LUN
            max_lun = __udisk_get_lun();
            send_packet(&max_lun, 1);
            return;
        }
    }

    // return stall
    send_stall();
}

//
// Function:
//      mass_storage_rest()
// Description:
//      响应 Mass Storage Reset 请求, 复位磁盘.
// Parameter:
//      void
// Return:
//      void
//
static void mass_storage_reset(void)
{
    if (wValue == 0 && wLength == 0)
    {
        if (wIndex == 0)
        {
            send_zero();
            return;
        }
    }

    // return stall
    send_stall();
}

//
// Request dispatch array
//
/*
static void (*Dispatch[])(void) =
{
    get_status,
    clear_feature,
    reserved,
    set_feature,
    reserved,
    set_address,
    get_descriptor,
    set_descriptor,
    get_configuration,
    set_configuration,
    get_interface,
    set_interface,
    synch_frame
};
*/

//
// Function:
//      ep0_isr()
// Description:
//      EP0 中断服务程序.
// Parameter:
//      void
// Return:
//      void
//
static void ep0_isr(void)
{
    u16_t status;

    status = read_mreg16(CEP_IRQ_STAT);
    if (status & (1<<1))
    {
        // SETUP packet interrupt
        write_mreg16(CEP_IRQ_STAT, (1<<1));
        // Receive SETUP packet
        status  = read_mreg16(SETUP1_0);
        wValue  = read_mreg16(SETUP3_2);
        wIndex  = read_mreg16(SETUP5_4);
        wLength = read_mreg16(SETUP7_6);
        bmRequestType = (u8_t)(status & 0xff);
        bRequest = (u8_t)(status >> 8);
        // Dispatch request
        switch (bRequest)
        {
        case GET_STATUS:
            get_status();
            break;
        case CLEAR_FEATURE:
            clear_feature();
            break;
        case SET_FEATURE:
            set_feature();
            break;
        case SET_ADDRESS:
            set_address();
            break;
        case GET_DESCRIPTOR:
            get_descriptor();
            break;
        case SET_DESCRIPTOR:
            set_descriptor();
            break;
        case GET_CONFIGURATION:
            get_configuration();
            break;
        case SET_CONFIGURATION:
            set_configuration();
            break;
        case GET_INTERFACE:
            get_interface();
            break;
        case SET_INTERFACE:
            set_interface();
            break;
        case SYNCH_FRAME:
            synch_frame();
            break;
        case GET_MAX_LUN:
            get_max_lun();
            break;
        case MASS_STORAGE_RESET:
            mass_storage_reset();
            break;
        default:
            reserved();
            break;
        }
    }
    else if (status & (1<<5))
    {
        // Data packet transmitted
        write_mreg16(CEP_IRQ_STAT, (1<<5));
        if (DescriptorType)
        {
            // Send descriptor completed
            DescriptorType   = 0;
            DescriptorLength = 0;
            DescriptorIndex  = 0;
        }
    }
    else if (status & (1<<6))
    {
        // rx done
        write_mreg16(CEP_IRQ_STAT, (1<<6));
        status = read_mreg16(OUT_TRNSFR_CNT);
        while (status > 0)
        {
            read_mreg16(CEP_DATA_BUF);
            status--;
        }
        send_zero();
    }
}

//
// Function:
//      udisk_isr()
// Description:
//      USB 设备中断服务程序.
// Parameter:
//      void
// Return:
//      void
//
void udisk_isr(void)
{
    u16_t status;

    status = read_mreg16(IRQ_STAT_L);
    if (status & (1<<0))
    {
        // USB Interrupt
        status = read_mreg16(USB_IRQ_STAT);
        if (status & (1<<1))
        {
            // Reset interrupt
            write_mreg16(USB_IRQ_STAT, (1<<1));
            write_mreg16(USB_RESUME_SUSPEND, 0);

            write_mreg16(EP1_IRQ_STAT, 0xffff);
            write_mreg16(EP1_IRQ_ENB, (1<<3));
            write_mreg16(EP1_RSP_SC, (1<<0)|(1<<3));
            while (read_mreg16(EP1_RSP_SC)) {}
            write_mreg16(EP1_CFG, (1<<0)|(1<<1)|(1<<3)|(1<<4));
            write_mreg16(EP2_IRQ_STAT, 0xffff);
            write_mreg16(EP2_IRQ_ENB, (1<<4));
            write_mreg16(EP2_RSP_SC, (1<<0)|(1<<3));
            while (read_mreg16(EP2_RSP_SC)) {}
            write_mreg16(EP2_CFG, (1<<0)|(1<<1)|(0<<3)|(2<<4));

            // check high speed.
            if (read_mreg16(USB_OPER) & (1<<2))
            {
                printf("usb set pack size 512bytes\n");
                set_packet_size(0x0200);
            }
            else
            {
                printf("usb set pack size 64bytes\n");
                set_packet_size(0x0040);
            }
            write_mreg16(EP1_MPS, _usbd_pkt_size);
            write_mreg16(EP2_MPS, _usbd_pkt_size);
            _usbd_reset = TRUE;
            _usbd_suspend = FALSE;
            _usbd_rx_done = FALSE;
        }
        else if (status & (1<<2))
        {
            // Resume interrupt
            write_mreg16(USB_IRQ_STAT, (1<<2));
            write_mreg16(USB_RESUME_SUSPEND, 0);
        }
        else if (status & (1<<3))
        {
            // Suspend interrupt
            write_mreg16(USB_IRQ_STAT, (1<<3));
            _usbd_suspend = TRUE;
            return;
        }
        else if (status & (1<<5))
        {
            write_mreg16(USB_IRQ_STAT, (1<<5));
            _usbd_dma_done = TRUE;
            _usbd_rx_done = FALSE;
        }
    }
    else if (status & (1<<1))
    {
        // EP0 Control Interrupt
        ep0_isr();
    }
    else if (status & (1<<2))
    {
        // EP1 Interrupt
        write_mreg16(EP1_IRQ_STAT, read_mreg16(EP1_IRQ_STAT));
        _usbd_tx_done = TRUE;
		//printf("ISR: _usbd_tx_done is %bd\n", _usbd_tx_done?1:0);
    }
    else if (status & (1<<3))
    {
        // EP2 Interrupt
        write_mreg16(EP2_IRQ_STAT, read_mreg16(EP2_IRQ_STAT));
        _usbd_rx_done = TRUE;
		//printf("ISR: _usbd_rx_done is %bd\n", _usbd_rx_done?1:0);
    }
#ifdef PLATFORM_ZSP
    write_mreg16(IRQ_ENB_L, 0x00);
    write_mreg16(IRQ_ENB_L, 0x0f);
#endif
}
