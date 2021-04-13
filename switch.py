"""Allows to configure a switch using RPi GPIO."""
from nanopi import duo, neocore2
from orangepi import (
    lite,
    lite2,
    one,
    oneplus,
    pc,
    pc2,
    pcplus,
    pi3,
    plus2e,
    prime,
    r1,
    winplus,
    zero,
    zeroplus,
    zeroplus2,
)
import voluptuous as vol

from homeassistant.components import orangepi_gpio
from . import DOMAIN, PLATFORMS, setup_mode, setup_output, write_output
from .const import CONF_INVERT_LOGIC, CONF_PIN_MODE, CONF_PORTS
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import DEVICE_DEFAULT_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.reload import setup_reload_service

PIN_MODES = {
    "lite": lite.BOARD,
    "lite2": lite2.BOARD,
    "one": one.BOARD,
    "oneplus": oneplus.BOARD,
    "pc": pc.BOARD,
    "pc2": pc2.BOARD,
    "pcplus": pcplus.BOARD,
    "pi3": pi3.BOARD,
    "plus2e": plus2e.BOARD,
    "prime": prime.BOARD,
    "r1": r1.BOARD,
    "winplus": winplus.BOARD,
    "zero": zero.BOARD,
    "zeroplus": zeroplus.BOARD,
    "zeroplus2": zeroplus2.BOARD,
    "duo": duo.BOARD,
    "neocore2": neocore2.BOARD,
}

DEFAULT_INVERT_LOGIC = False

_SWITCHES_SCHEMA = vol.Schema({cv.positive_int: cv.string})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PORTS): _SWITCHES_SCHEMA,
        vol.Required(CONF_PIN_MODE): vol.In(PIN_MODES.keys()),
        vol.Optional(CONF_INVERT_LOGIC, default=DEFAULT_INVERT_LOGIC): cv.boolean,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Orange PI GPIO devices."""
    setup_reload_service(hass, DOMAIN, PLATFORMS)

    invert_logic = config.get(CONF_INVERT_LOGIC)
    pin_mode = config[CONF_PIN_MODE]

    switches = []
    ports = config.get(CONF_PORTS)
    setup_mode(pin_mode)
    for port, name in ports.items():
        switches.append(OPiGPIOSwitch(name, port, invert_logic))
    add_entities(switches)


class OPiGPIOSwitch(ToggleEntity):
    """Representation of a  Orange Pi GPIO."""

    def __init__(self, name, port, invert_logic):
        """Initialize the pin."""
        self._name = name or DEVICE_DEFAULT_NAME
        self._port = port
        self._invert_logic = invert_logic
        self._state = False
        orangepi_gpio.setup_output(self._port)
        orangepi_gpio.write_output(self._port, 1 if self._invert_logic else 0)

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the device on."""
        orangepi_gpio.write_output(self._port, 0 if self._invert_logic else 1)
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        orangepi_gpio.write_output(self._port, 1 if self._invert_logic else 0)
        self._state = False
        self.schedule_update_ha_state()
