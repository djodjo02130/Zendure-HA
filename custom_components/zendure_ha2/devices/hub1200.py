"""Module for the Hyper2000 device integration in Home Assistant."""

import logging
from typing import Any

from homeassistant.components.number import NumberMode
from homeassistant.core import HomeAssistant

from custom_components.zendure_ha2.binary_sensor import ZendureBinarySensor
from custom_components.zendure_ha2.number import ZendureNumber
from custom_components.zendure_ha2.select import ZendureSelect
from custom_components.zendure_ha2.sensor import ZendureSensor
from custom_components.zendure_ha2.zendurebase import ZendureBase
from custom_components.zendure_ha2.zendurebattery import ZendureBattery
from custom_components.zendure_ha2.zenduredevice import ZendureDevice

_LOGGER = logging.getLogger(__name__)


class Hub1200(ZendureDevice):
    def __init__(self, hass: HomeAssistant, deviceId: str, prodName: str, definition: Any) -> None:
        """Initialise Hub1200."""
        super().__init__(hass, deviceId, prodName, definition)
        self.powerMin = -800
        self.powerMax = 800
        self.numbers: list[ZendureNumber] = []

    def entitiesCreate(self) -> None:
        super().entitiesCreate()

        binaries = [
            self.binary("masterSwitch"),
            self.binary("buzzerSwitch"),
            self.binary("wifiState"),
            self.binary("heatState"),
            self.binary("reverseState"),
            self.binary("pass"),
        ]
        ZendureBinarySensor.add(binaries)

        self.numbers = [
            self.number("inputLimit", None, "W", "power", 0, 800, NumberMode.SLIDER),
            self.number("outputLimit", None, "W", "power", 0, 200, NumberMode.SLIDER),
            self.number("socSet", "{{ value | int / 10 }}", "%", None, 5, 100, NumberMode.SLIDER),
            self.number("minSoc", "{{ value | int / 10 }}", "%", None, 5, 100, NumberMode.SLIDER),
        ]
        ZendureNumber.add(self.numbers)

        sensors = [
            self.sensor("hubState"),
            self.sensor("solarInputPower", None, "W", "power", "measurement"),
            self.sensor("packInputPower", None, "W", "power", "measurement"),
            self.sensor("outputPackPower", None, "W", "power", "measurement"),
            self.sensor("outputHomePower", None, "W", "power", "measurement"),
            self.calculate("remainOutTime", self.remainingOutput, "h", "duration"),
            self.calculate("remainInputTime", self.remainingInput, "h", "duration"),
            self.sensor("packNum", None),
            self.sensor("electricLevel", None, "%", "battery"),
            self.sensor("energyPower", None, "W"),
            self.sensor("gridPower", None, "W", "power", "measurement"),
            self.sensor("inverseMaxPower", None, "W"),
            self.sensor("solarPower1", None, "W", "power", "measurement"),
            self.sensor("solarPower2", None, "W", "power", "measurement"),
        ]
        ZendureSensor.add(sensors)

        selects = [
            self.select("acMode", {1: "input", 2: "output"}, self.update_ac_mode),
            self.select("passMode", {0: "auto", 2: "on", 1: "off"}),
            self.select("autoRecover", {0: "off", 1: "on"}),
        ]
        ZendureSelect.add(selects)

    def entitiesBattery(self, battery: ZendureBattery, sensors: list[ZendureSensor]) -> None:
        sensors.append(battery.sensor("soh", "{{ (value / 10) }}", "%", None))
        if battery.kwh > 1:
            self.powerMin = -1200
            self.numbers[0].update_range(0, abs(self.powerMin))

    def entityUpdate(self, key: Any, value: Any) -> bool:
        # Call the base class entityUpdate method
        if not super().entityUpdate(key, value):
            return False
        match key:
            case "inverseMaxPower":
                self.powerMax = value
                self.numbers[1].update_range(0, value)
        return True

    def writePower(self, power: int, inprogram: bool) -> None:
        delta = abs(power - self.powerAct)
        if delta <= 1 and inprogram:
            _LOGGER.info(f"Update power {self.name} => no action [power {power} capacity {self.capacity}]")
            return

        _LOGGER.info(f"Update power {self.name} => {power} capacity {self.capacity}")
        self.mqttInvoke({
            "arguments": [
                {
                    "autoModelProgram": 2 if inprogram else 0,
                    "autoModelValue": power,
                    "msgType": 1,
                    "autoModel": 8 if inprogram else 0,
                }
            ],
            "function": "deviceAutomation",
        })
