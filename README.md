# opi_gpio
## Home Assistant Custom Component for Orangepi GPIO

To control switch, binary and cover devices on GPIO 

### OPi.GPIO
https://www.home-assistant.io/integrations/orangepi_gpio

### Homeassistant Core Component orangepi_gpio
Modified the following raspberry pi component.
https://github.com/home-assistant/core/tree/dev/homeassistant/components/rpi_gpio

And added the switch and the cover functions to the original orangepi_gpio component.
https://github.com/home-assistant/core/tree/dev/homeassistant/components/orangepi_gpio

### Other References
https://github.com/rm-hull/OPi.GPIO
https://pypi.org/project/OPi.GPIO/

**Physical Pin No:BCM and GPIO on Orangepi PC**
```
If you point out No.7, it shows GPIO6.
BCM to GPIO
    3: 12,    # I2C0_SDA/PA12 (TWI0_SDA/DI_RX/PA_EINT12)
    5: 11,    # I2C0_SCL/PA11 (TWI0_SCK/DI_TX/PA_EINT11)
    7: 6,     # PA6 (SIM_PWREN/PWM1/PA_EINT6)
    8: 13,    # PA13 (SPI1_CS/UART3_TX/PA_EINT13)
    10: 14,   # PA14 (SPI1_CLK/UART3_RX/PA_EINT14)
    11: 1,    # PA1 (UART2_RX/JTAG_CK/PA_EINT1)
    12: 110,  # PD14
    13: 0,    # PA0 (UART2_TX/JTAG_MS/PA_EINT0)
    15: 3,    # PA3 (UART2_CTS/JTAG_DI/PA_EINT3)
    16: 68,   # PC4
    18: 71,   # PC7
    19: 64,   # PC0 (SPI0_MOSI)
    21: 65,   # PC1 (SPI0_MISO)
    22: 2,    # PA2 (UART2_RTS/JTAG_DO/PA_EINT2)
    23: 66,   # PC2 (SPI0_CLK)
    24: 67,   # PC3 (SPI0_CS)
    26: 21,   # PA21 (PCM0_DIN/SIM_VPPPP/PA_EINT21)
    27: 19,   # PA19 (PCM0_CLK/TWI1_SDA/PA_EINT19)
    28: 18,   # PA18 (PCM0_SYNC/TWI1_SCK/PA_EINT18)
    29: 7,    # PA7 (SIM_CLK/PA_EINT7)
    31: 8,    # PA8 (SIM_DATA/PA_EINT8)
    32: 200,  # PG8 (UART1_RTS/PG_EINT8)
    33: 9,    # PA9 (SIM_RST/PA_EINT9)
    35: 10,   # PA10 (SIM_DET/PA_EINT10)
    36: 201,  # PG9 (UART1_CTS/PG_EINT9)
    37: 20,   # PA20 (PCM0_DOUT/SIM_VPPEN/PA_EINT20)
    38: 198,  # PG6 (UART1_TX/PG_EINT6)
    40: 199,  # PG7 (UART1_RX/PG_EINT7)
```   

Home Assistant not working by root user, so need to add group "gpio" and have the hass user belong to it.

```
$ sudo addgroup gpio
$ sudo usermod -aG gpio <current_user>
```

```
$ sudo nano /etc/udev/rules.d/99-gpio.rules
```

```
$ echo XX > /sys/class/gpio/export
```
Add an udev rule to have gpio group manage gpio pins like the following. 
```
$sudo pico /etc/udev/rules.d/99-gpio.rules

# /etc/udev/rules.d/99-gpio.rules
# need to add group "gpio" for reading and writing access GPIO dir
#
#Group gpio chown
SUBSYSTEM=="gpio", PROGRAM="/bin/sh -c '/bin/chown -R root:gpio /sys/class/gpio'"
#Group gpio chmod
SUBSYSTEM=="gpio", PROGRAM="/bin/sh -c '/bin/chmod -R ug+rw /sys/class/gpio'"
#Group chown
SUBSYSTEM=="gpio", PROGRAM="/bin/sh -c '/bin/chown -R root:gpio /sys/devices/platform/soc/1c20800.pinctrl/gpiochip0/gpio'"
#Group chmod
SUBSYSTEM=="gpio", PROGRAM="/bin/sh -c '/bin/chmod -R ug+rw /sys/devices/platform/soc/1c20800.pinctrl/gpiochip0/gpio'"
```
or make more simple 
```
$ sudo pico /etc/udev/rules.d/10-gpio.rules

SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c 'find -L /sys/class/gpio/ -maxdepth 2 -exec chown root:gpio {} \; -exec chmod 770 {} \; || true'"

```
**reload config**
```
$ sudo udevadm trigger --subsystem-match=gpio
```
