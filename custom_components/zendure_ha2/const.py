"""Constants for the Zendure Integration integration."""

from enum import NAMED_FLAGS, Enum, Flag, auto, verify

DOMAIN = "zendure_ha2"

CONF_P1METER = "p1meter"
CONF_MQTTLOG = "mqttlog"
CONF_MQTTLOCAL = "mqttlocal"
CONF_MQTTSERVER = "mqttserver"
CONF_MQTTPORT = "mqttport"
CONF_MQTTUSER = "mqttuser"
CONF_MQTTPSW = "mqttpsw"
CONF_WIFISSID = "wifissid"
CONF_WIFIPSW = "wifipsw"


class ManagerState(Enum):
    IDLE = 0
    CHARGING = 1
    DISCHARGING = 2


class AcMode:
    INPUT = 1
    OUTPUT = 2


@verify(NAMED_FLAGS)
class MqttState(Flag):
    UNKNOWN = 0
    BLE = 1
    LOCAL = 2
    CLOUD = 4
    APP = 8
    BLE_ERR = 16


class SmartMode:
    NONE = 0
    MANUAL = 1
    MATCHING = 2
    FAST_UPDATE = 100
    MIN_POWER = 50
    START_POWER = 100
    TIMEFAST = 3
    TIMEZERO = 5
    TIMEIDLE = 10
