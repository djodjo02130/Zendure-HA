import logging
from collections.abc import Callable
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from stringcase import snakecase

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(_hass, _config_entry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Zendure button entities."""
    ZendureButton.add = async_add_entities


class ZendureButton(ButtonEntity):
    add: AddEntitiesCallback

    def __init__(
        self,
        deviceinfo: DeviceInfo,
        uniqueid: str,
        onpress: Callable[['ZendureButton'], None],
    ) -> None:
        """Initialize a button entity."""
        self._onpress = onpress

        self._attr_device_info = deviceinfo
        self._attr_unique_id = f"{deviceinfo.get('name')}-{uniqueid}"
        self.entity_id = f"button.{deviceinfo.get('name')}-{snakecase(uniqueid)}"

        self._attr_has_entity_name = True
        self._attr_should_poll = False
        self._attr_translation_key = snakecase(uniqueid)
        self._attr_available = True

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info(f"Press button: {self._attr_unique_id}")
        self._onpress(self)
