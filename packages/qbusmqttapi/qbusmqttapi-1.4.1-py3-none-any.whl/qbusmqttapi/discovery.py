"""Qbis discovery models."""

from __future__ import annotations

from .const import (
    KEY_OUTPUT_ACTIONS,
    KEY_OUTPUT_ID,
    KEY_OUTPUT_LOCATION,
    KEY_OUTPUT_LOCATION_ID,
    KEY_OUTPUT_NAME,
    KEY_OUTPUT_PROPERTIES,
    KEY_OUTPUT_REF_ID,
    KEY_OUTPUT_TYPE,
    KEY_OUTPUT_VARIANT,
)

KEY_DEVICES = "devices"

KEY_DEVICE_FUNCTIONBLOCKS = "functionBlocks"
KEY_DEVICE_ID = "id"
KEY_DEVICE_IP = "ip"
KEY_DEVICE_MAC = "mac"
KEY_DEVICE_NAME = "name"
KEY_DEVICE_SERIAL_NR = "serialNr"
KEY_DEVICE_TYPE = "type"
KEY_DEVICE_VERSION = "version"


class QbusMqttOutput:
    """MQTT representation of a Qbus output."""

    def __init__(self, data: dict, device: QbusMqttDevice) -> None:
        """Initialize based on a json loaded dictionary."""
        self._data = data
        self._device = device

    @property
    def id(self) -> str:
        """Return the id."""
        return self._data.get(KEY_OUTPUT_ID) or ""

    @property
    def type(self) -> str:
        """Return the type."""
        return self._data.get(KEY_OUTPUT_TYPE) or ""

    @property
    def name(self) -> str:
        """Return the name."""
        return self._data.get(KEY_OUTPUT_NAME) or ""

    @property
    def ref_id(self) -> str:
        """Return the ref id."""
        return self._data.get(KEY_OUTPUT_REF_ID) or ""

    @property
    def properties(self) -> dict:
        """Return the properties."""
        return self._data.get(KEY_OUTPUT_PROPERTIES) or {}

    @property
    def actions(self) -> dict:
        """Return the actions."""
        return self._data.get(KEY_OUTPUT_ACTIONS) or {}

    @property
    def location(self) -> str:
        """Return the location."""
        return self._data.get(KEY_OUTPUT_LOCATION) or ""

    @property
    def location_id(self) -> int:
        """Return the location id."""
        return self._data.get(KEY_OUTPUT_LOCATION_ID) or 0

    @property
    def variant(self) -> str | tuple | list:
        """Return the variant."""
        value = self._data.get(KEY_OUTPUT_VARIANT) or ""

        if isinstance(value, list | tuple):
            value = [x for x in value if x is not None]

        return value

    @property
    def device(self) -> QbusMqttDevice:
        """Return the device."""
        return self._device


class QbusMqttDevice:
    """MQTT representation of a Qbus device."""

    def __init__(self, data: dict) -> None:
        """Initialize based on a json loaded dictionary."""
        self._data = data

    @property
    def id(self) -> str:
        """Return the id."""
        return self._data.get(KEY_DEVICE_ID) or ""

    @property
    def ip(self) -> str:
        """Return the ip address."""
        return self._data.get(KEY_DEVICE_IP) or ""

    @property
    def mac(self) -> str:
        """Return the ip address."""
        return self._data.get(KEY_DEVICE_MAC) or ""

    @property
    def name(self) -> str:
        """Return the ip address."""
        return self._data.get(KEY_DEVICE_NAME) or ""

    @property
    def serial_number(self) -> str:
        """Return the serial number."""
        return self._data.get(KEY_DEVICE_SERIAL_NR) or ""

    @property
    def type(self) -> str:
        """Return the mac address."""
        return self._data.get(KEY_DEVICE_TYPE) or ""

    @property
    def version(self) -> str:
        """Return the version."""
        return self._data.get(KEY_DEVICE_VERSION) or ""

    @property
    def outputs(self) -> list[QbusMqttOutput]:
        """Return the outputs."""

        outputs: list[QbusMqttOutput] = []

        if self._data.get(KEY_DEVICE_FUNCTIONBLOCKS):
            outputs = [QbusMqttOutput(x, self) for x in self._data[KEY_DEVICE_FUNCTIONBLOCKS]]

        return outputs


class QbusDiscovery:
    """MQTT representation of a Qbus config."""

    def __init__(self, data: dict) -> None:
        """Initialize based on a json loaded dictionary."""
        if KEY_DEVICES in data:
            self._devices = [QbusMqttDevice(x) for x in data[KEY_DEVICES]]

        self._name: str = data["app"]

    def get_device_by_id(self, id: str) -> QbusMqttDevice | None:
        """Get the device by id."""
        return next((x for x in self.devices if x.id.casefold() == id.casefold()), None)

    def get_device_by_serial(self, serial: str) -> QbusMqttDevice | None:
        """Get the device by serial."""
        return next(
            (x for x in self.devices if x.serial_number.casefold() == serial.casefold()),
            None,
        )

    @property
    def devices(self) -> list[QbusMqttDevice]:
        """Return the devices."""
        return self._devices

    @property
    def name(self) -> str:
        """Return device name."""
        return self._name
