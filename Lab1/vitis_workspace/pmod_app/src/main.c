
#include "xparameters.h"
#include "xil_printf.h"
#include "xgpio.h"
#include "xstatus.h"
#include "xil_types.h"

#define BTN_ID XPAR_AXI_GPIO_BUTTONS_DEVICE_ID
#define LED_ID XPAR_AXI_GPIO_LED_DEVICE_ID

#define BTN_CHANNEL 1
#define LED_CHANNEL 1
#define BTN_MASK 0xF

int LEDOutput()
{
    XGpio led_device;
    XGpio btn_device;
    u32 data;
    int status;

    xil_printf("Entered function main\r\n");

    // Initialize LED Device
    status = XGpio_Initialize(&led_device, LED_ID);
    if (status != XST_SUCCESS)
        return XST_FAILURE;

    // Initialize Button Device
    status = XGpio_Initialize(&btn_device, BTN_ID);
    if (status != XST_SUCCESS)
        return XST_FAILURE;

    // Set Button Tristate: input = 1
    XGpio_SetDataDirection(&btn_device, BTN_CHANNEL, 0xF);

    // Set LED Tristate: output = 0
    XGpio_SetDataDirection(&led_device, LED_CHANNEL, 0x0);

    while (1)
    {
        // Read four buttons
        data = XGpio_DiscreteRead(&btn_device, BTN_CHANNEL);

        // Set corresponding LEDs
        XGpio_DiscreteWrite(
            &led_device,
            LED_CHANNEL,
            data & BTN_MASK
        );
    }

    return XST_SUCCESS;
}

int main()
{
    int Status = LEDOutput();

    if (Status != XST_SUCCESS)
    {
        xil_printf("GPIO output to the LEDs failed!\r\n");
    }

    return 0;
}
