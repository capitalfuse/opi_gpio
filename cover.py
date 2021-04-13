"""Support for controlling a Orange Pi cover."""
from time import sleep
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
from homeassistant.components.cover import PLATFORM_SCHEMA, CoverEntity
from homeassistant.const import CONF_COVERS, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.reload import setup_reload_service

from . import DOMAIN, PLATFORMS, setup_mode, setup_input, read_input, setup_output, write_output

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

CONF_RELAY_PIN = "relay_pin"
CONF_RELAY_TIME = "relay_time"
CONF_STATE_PIN = "state_pin"

CONF_INVERT_STATE = "invert_state"
CONF_INVERT_RELAY = "invert_relay"

DEFAULT_RELAY_TIME = 0.2

DEFAULT_INVERT_STATE = False
DEFAULT_INVERT_RELAY = False
_COVERS_SCHEMA = vol.All(
    cv.ensure_list,
    [
        vol.Schema(
            {
                CONF_NAME: cv.string,
                CONF_RELAY_PIN: cv.positive_int,
                CONF_STATE_PIN: cv.positive_int,
            }
        )
    ],
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COVERS): _COVERS_SCHEMA,
        vol.Required(CONF_PIN_MODE): vol.In(PIN_MODES.keys()),
        vol.Optional(CONF_RELAY_TIME, default=DEFAULT_RELAY_TIME): cv.positive_int,
        vol.Optional(CONF_INVERT_STATE, default=DEFAULT_INVERT_STATE): cv.boolean,
        vol.Optional(CONF_INVERT_RELAY, default=DEFAULT_INVERT_RELAY): cv.boolean,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the OPi cover platform."""
    setup_reload_service(hass, DOMAIN, PLATFORMS)

    relay_time = config.get(CONF_RELAY_TIME)

    setup_mode(pin_mode)
    invert_state = config.get(CONF_INVERT_STATE)
    invert_relay = config.get(CONF_INVERT_RELAY)
    covers = []
    covers_conf = config.get(CONF_COVERS)

    for cover in covers_conf:
        covers.append(
            OPiGPIOCover(
                cover[CONF_NAME],
                cover[CONF_RELAY_PIN],
                cover[CONF_STATE_PIN],
                relay_time,
                invert_state,
                invert_relay,
            )
        )
    add_entities(covers)


class OPiGPIOCover(CoverEntity):
    """Representation of a Raspberry GPIO cover."""

    def __init__(
        self,
        name,
        relay_pin,
        state_pin,
        relay_time,
        invert_state,
        invert_relay,
    ):
        """Initialize the cover."""
        self._name = name
        self._state = False
        self._relay_pin = relay_pin
        self._state_pin = state_pin
        self._relay_time = relay_time
        self._invert_state = invert_state
        self._invert_relay = invert_relay
        orangepi_gpio.setup_output(self._relay_pin)
        orangepi_gpio.setup_input(self._state_pin)
        orangepi_gpio.write_output(self._relay_pin, 0 if self._invert_relay else 1)

    @property
    def name(self):
        """Return the name of the cover if any."""
        return self._name

    def update(self):
        """Update the state of the cover."""
        self._state = orangepi_gpio.read_input(self._state_pin)

    @property
    def is_closed(self):
        """Return true if cover is closed."""
        return self._state != self._invert_state

    def _trigger(self):
        """Trigger the cover."""
        orangepi_gpio.write_output(self._relay_pin, 1 if self._invert_relay else 0)
        sleep(self._relay_time)
        orangepi_gpio.write_output(self._relay_pin, 0 if self._invert_relay else 1)

    def close_cover(self, **kwargs):
        """Close the cover."""
        if not self.is_closed:
            self._trigger()

    def open_cover(self, **kwargs):
        """Open the cover."""
        if self.is_closed:
            self._trigger()
