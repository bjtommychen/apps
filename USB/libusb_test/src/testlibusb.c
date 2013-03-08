/*
 * testlibusb.c
 *
 *  Test suite program
 */

#include <stdio.h>
#include <string.h>
#include "lusb0_usb.h"

int verbose = 0;


// Device vendor and product id.
#define MY_VID 0x0666
#define MY_PID 0x0001

// Device configuration and interface id.
#define MY_CONFIG 1
#define MY_INTF 0

// Device endpoint(s)
#define EP_IN 0x81
#define EP_OUT 0x01

// Device of bytes to transfer.
#define BUF_SIZE 64


void print_endpoint(struct usb_endpoint_descriptor *endpoint)
{
    printf("      bEndpointAddress: %02xh\n", endpoint->bEndpointAddress);
    printf("      bmAttributes:     %02xh\n", endpoint->bmAttributes);
    printf("      wMaxPacketSize:   %d\n", endpoint->wMaxPacketSize);
    printf("      bInterval:        %d\n", endpoint->bInterval);
    printf("      bRefresh:         %d\n", endpoint->bRefresh);
    printf("      bSynchAddress:    %d\n", endpoint->bSynchAddress);
}

void print_altsetting(struct usb_interface_descriptor *interface)
{
    int i;

    printf("    bInterfaceNumber:   %d\n", interface->bInterfaceNumber);
    printf("    bAlternateSetting:  %d\n", interface->bAlternateSetting);
    printf("    bNumEndpoints:      %d\n", interface->bNumEndpoints);
    printf("    bInterfaceClass:    %d\n", interface->bInterfaceClass);
    printf("    bInterfaceSubClass: %d\n", interface->bInterfaceSubClass);
    printf("    bInterfaceProtocol: %d\n", interface->bInterfaceProtocol);
    printf("    iInterface:         %d\n", interface->iInterface);

    for (i = 0; i < interface->bNumEndpoints; i++)
        print_endpoint(&interface->endpoint[i]);
}

void print_interface(struct usb_interface *interface)
{
    int i;

    for (i = 0; i < interface->num_altsetting; i++)
        print_altsetting(&interface->altsetting[i]);
}

void print_configuration(struct usb_config_descriptor *config)
{
    int i;

    printf("  wTotalLength:         %d\n", config->wTotalLength);
    printf("  bNumInterfaces:       %d\n", config->bNumInterfaces);
    printf("  bConfigurationValue:  %d\n", config->bConfigurationValue);
    printf("  iConfiguration:       %d\n", config->iConfiguration);
    printf("  bmAttributes:         %02xh\n", config->bmAttributes);
    printf("  MaxPower:             %d\n", config->MaxPower);

    for (i = 0; i < config->bNumInterfaces; i++)
        print_interface(&config->interface[i]);
}

void print_device_descriptor(struct usb_device_descriptor *desc, int indent)
{
	printf("%.*sbLength:             %u\n",    indent, "                    ", desc->bLength);
	printf("%.*sbDescriptorType:     %02Xh\n", indent, "                    ", desc->bDescriptorType);
	printf("%.*sbcdUSB:              %04Xh\n", indent, "                    ", desc->bcdUSB);
	printf("%.*sbDeviceClass:        %02Xh\n", indent, "                    ", desc->bDeviceClass);
	printf("%.*sbDeviceSubClass:     %02Xh\n", indent, "                    ", desc->bDeviceSubClass);
	printf("%.*sbDeviceProtocol:     %02Xh\n", indent, "                    ", desc->bDeviceProtocol);
	printf("%.*sbMaxPacketSize0:     %02Xh\n", indent, "                    ", desc->bMaxPacketSize0);
	printf("%.*sidVendor:            %04Xh\n", indent, "                    ", desc->idVendor);
	printf("%.*sidProduct:           %04Xh\n", indent, "                    ", desc->idProduct);
	printf("%.*sbcdDevice:           %04Xh\n", indent, "                    ", desc->bcdDevice);
	printf("%.*siManufacturer:       %u\n",    indent, "                    ", desc->iManufacturer);
	printf("%.*siProduct:            %u\n",    indent, "                    ", desc->iProduct);
	printf("%.*siSerialNumber:       %u\n",    indent, "                    ", desc->iSerialNumber);
	printf("%.*sbNumConfigurations:  %u\n",    indent, "                    ", desc->bNumConfigurations);
}

int print_device(struct usb_device *dev, int level)
{
    usb_dev_handle *udev;
    char description[256];
    char string[256];
    int ret, i;

    udev = usb_open(dev);
    if (udev)
    {
        if (dev->descriptor.iManufacturer)
        {
            ret = usb_get_string_simple(udev, dev->descriptor.iManufacturer, string,
                                        sizeof(string));
            if (ret > 0)
                snprintf(description, sizeof(description), "%s - ", string);
            else
                snprintf(description, sizeof(description), "%04X - ",
                         dev->descriptor.idVendor);
        }
        else
            snprintf(description, sizeof(description), "%04X - ",
                     dev->descriptor.idVendor);

        if (dev->descriptor.iProduct)
        {
            ret = usb_get_string_simple(udev, dev->descriptor.iProduct, string,
                                        sizeof(string));
            if (ret > 0)
                snprintf(description + strlen(description), sizeof(description) -
                         strlen(description), "%s", string);
            else
                snprintf(description + strlen(description), sizeof(description) -
                         strlen(description), "%04X", dev->descriptor.idProduct);
        }
        else
            snprintf(description + strlen(description), sizeof(description) -
                     strlen(description), "%04X", dev->descriptor.idProduct);

    }
    else
        snprintf(description, sizeof(description), "%04X - %04X",
                 dev->descriptor.idVendor, dev->descriptor.idProduct);

/*

C/C++ code
// %.*s 其中的.*表示显示的精度 对字符串输出(s)类型来说就是宽度
// 这个*代表的值由后面的参数列表中的整数型(int)值给出

// 例如：
printf("%.*s\n", 1, "abc");        // 输出a
printf("%.*s\n", 2, "abc");        // 输出ab
printf("%.*s\n", 3, "abc");        // 输出abc >3是一样的效果 因为输出类型type = s，遇到'\0'会结束

*/


    printf("\n%.*sDev #%d: %s", level * 2, "                    ", dev->devnum,
           description);

    if (udev && verbose)
    {
        if (dev->descriptor.iSerialNumber)
        {
            ret = usb_get_string_simple(udev, dev->descriptor.iSerialNumber, string,
                                        sizeof(string));
            if (ret > 0)
                printf(" - Serial Number: %s\n", string);
        }
		else
			printf("\n");
    }
	else
		printf("\n");

	if (verbose)
		print_device_descriptor(&dev->descriptor, level * 2);

    if (udev)
        usb_close(udev);

    if (verbose)
    {
        if (!dev->config)
        {
            printf("  Couldn't retrieve descriptors\n");
            return 0;
        }

        for (i = 0; i < dev->descriptor.bNumConfigurations; i++)
            print_configuration(&dev->config[i]);
    }
    else
    {
        printf(" dev->num_children is %d.\n", dev->num_children);
        for (i = 0; i < dev->num_children; i++)
            print_device(dev->children[i], level + 1);
    }

    return 0;
}


int main(int argc, char *argv[])
{
    struct usb_bus *bus;
    usb_dev_handle *dev;
    char tmp[BUF_SIZE] = {1,2,3,4,5,6,7,8,};
    int ret;

    if (argc > 1 && !strcmp(argv[1], "-v"))
        verbose = 1;

    usb_init();
    usb_set_debug(255);

    usb_find_busses();
    usb_find_devices();

    for (bus = usb_get_busses(); bus; bus = bus->next)
    {
        if (bus->root_dev && !verbose)
            print_device(bus->root_dev, 0);
        else
        {
            struct usb_device *dev;

            for (dev = bus->devices; dev; dev = dev->next)
                print_device(dev, 0);
        }
    }

#if 1
    bus = usb_get_busses();
    dev = usb_open(bus->devices);

//    usb_reset(dev);

#if 1//def TEST_SET_CONFIGURATION
    if (usb_set_configuration(dev, MY_CONFIG) < 0)
    {
        printf("error setting config #%d: %s\n", MY_CONFIG, usb_strerror());
        usb_close(dev);
        return 0;
    }
    else
    {
        printf("success: set configuration #%d\n", MY_CONFIG);
    }
#endif

#if 1//def TEST_CLAIM_INTERFACE
    if (usb_claim_interface(dev, 0) < 0)
    {
        printf("error claiming interface #%d:\n%s\n", MY_INTF, usb_strerror());
        usb_close(dev);
        return 0;
    }
    else
    {
        printf("success: claim_interface #%d\n", MY_INTF);
    }
#endif


//    ret = transfer_bulk_async(dev, EP_OUT, tmp, sizeof(tmp), 5000);
    // Running a sync write test
    ret = usb_bulk_write(dev, EP_OUT, tmp, sizeof(tmp), 5000);
    if (ret < 0)
    {
        printf("error writing:\n%s\n", usb_strerror());
    }
    else
    {
        printf("success: bulk write %d bytes\n", ret);
    }
    
    usb_close(dev);
#endif

    return 0;
}

