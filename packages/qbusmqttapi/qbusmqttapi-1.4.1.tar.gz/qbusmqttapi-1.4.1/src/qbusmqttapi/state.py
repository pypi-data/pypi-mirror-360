"""Qbus state models."""

from enum import StrEnum
from typing import Any

from .const import (
    KEY_OUTPUT_ACTION,
    KEY_OUTPUT_ID,
    KEY_OUTPUT_PROPERTIES,
    KEY_OUTPUT_TYPE,
    KEY_PROPERTIES_CO2,
    KEY_PROPERTIES_CURRENT_TEMPERATURE,
    KEY_PROPERTIES_REGIME,
    KEY_PROPERTIES_SHUTTER_POSITION,
    KEY_PROPERTIES_SLAT_POSITION,
    KEY_PROPERTIES_STATE,
    KEY_PROPERTIES_SET_TEMPERATURE,
    KEY_PROPERTIES_VALUE,
)

KEY_DEVICE_CONNECTABLE = "connectable"
KEY_DEVICE_CONNECTED = "connected"
KEY_DEVICE_ID = "id"
KEY_DEVICE_STATE_PROPERTIES = "properties"

KEY_GATEWAY_ID = "id"
KEY_GATEWAY_ONLINE = "online"
KEY_GATEWAY_REASON = "reason"


class StateType(StrEnum):
    """Values to be used as state type."""

    ACTION = "action"
    EVENT = "event"
    STATE = "state"


class StateAction(StrEnum):
    """Values to be used as state action."""

    ACTIVATE = "activate"
    ACTIVE = "active"


class GaugeKey(StrEnum):
    """Keys to read gauge state."""

    CURRENT_VALUE = "currentValue"
    CONSUMPTION_VALUE = "consumptionValue"


class QbusMqttGatewayState:
    """MQTT representation of a Qbus gateway state."""

    def __init__(self, data: dict) -> None:
        """Initialize based on a json loaded dictionary."""
        self.id: str | None = data.get(KEY_GATEWAY_ID)
        self.online: bool | None = data.get(KEY_GATEWAY_ONLINE)
        self.reason: str | None = data.get(KEY_GATEWAY_REASON)


class QbusMqttDeviceStateProperties:
    """MQTT representation of a Qbus device its state properties."""

    def __init__(self, data: dict) -> None:
        """Initialize based on a json loaded dictionary."""
        self.connectable: bool | None = data.get(KEY_DEVICE_CONNECTABLE)
        self.connected: bool | None = data.get(KEY_DEVICE_CONNECTED)


class QbusMqttDeviceState:
    """MQTT representation of a Qbus device state."""

    def __init__(self, data: dict) -> None:
        """Initialize based on a json loaded dictionary."""
        self.id: str | None = data.get(KEY_DEVICE_ID)

        properties = data.get(KEY_DEVICE_STATE_PROPERTIES)
        self.properties: QbusMqttDeviceStateProperties | None = (
            QbusMqttDeviceStateProperties(properties) if properties is not None else None
        )


class QbusMqttState:
    """MQTT representation of a Qbus state."""

    def __init__(
        self,
        data: dict | None = None,
        *,
        id: str | None = None,
        type: str | None = None,
        action: str | None = None,
    ) -> None:
        """Initialize state."""
        self.id: str = ""
        self.type: str = ""
        self.action: str | None = None
        self.properties: dict | None = None

        if data is not None:
            self.id = data.get(KEY_OUTPUT_ID, "")
            self.type = data.get(KEY_OUTPUT_TYPE, "")
            self.action = data.get(KEY_OUTPUT_ACTION)
            self.properties = data.get(KEY_OUTPUT_PROPERTIES)

        if id is not None:
            self.id = id

        if type is not None:
            self.type = type

        if action is not None:
            self.action = action

    def read_property(self, key: str, default: Any) -> Any:
        """Read a property."""
        return self.properties.get(key, default) if self.properties else default

    def write_property(self, key: str, value: Any) -> None:
        """Add or update a property."""
        if self.properties is None:
            self.properties = {}

        self.properties[key] = value


class QbusMqttOnOffState(QbusMqttState):
    """MQTT representation of a Qbus on/off output."""

    def __init__(
        self,
        data: dict | None = None,
        *,
        id: str | None = None,
        type: str | None = None,
    ) -> None:
        super().__init__(data, id=id, type=type)

    def read_value(self) -> bool:
        """Read the value of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_VALUE, False)

    def write_value(self, on: bool) -> None:
        """Set the Qbus output on or off."""
        self.write_property(KEY_PROPERTIES_VALUE, on)


class QbusMqttAnalogState(QbusMqttState):
    """MQTT representation of a Qbus analog output."""

    def __init__(
        self,
        data: dict | None = None,
        *,
        id: str | None = None,
        type: str | None = None,
    ) -> None:
        super().__init__(data, id=id, type=type)

    def read_percentage(self) -> float:
        """Read the value of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_VALUE, 0)

    def write_percentage(self, percentage: float) -> None:
        """Set the value of the Qbus output."""
        self.write_property(KEY_PROPERTIES_VALUE, percentage)

    def write_on_off(self, on: bool) -> None:
        """Set the Qbus output on or off."""
        self.action = "on" if on else "off"


class QbusMqttShutterState(QbusMqttState):
    """MQTT representation of a Qbus shutter output."""

    def __init__(
        self,
        data: dict | None = None,
        *,
        id: str | None = None,
        type: str | None = None,
    ) -> None:
        super().__init__(data, id=id, type=type)

    def read_state(self) -> str | None:
        """Read the state of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_STATE, None)

    def write_state(self, state: str) -> None:
        """Set the state of the Qbus output."""
        self.write_property(KEY_PROPERTIES_STATE, state)

    def read_position(self) -> int | None:
        """Read the position of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_SHUTTER_POSITION, None)

    def write_position(self, percentage: int) -> None:
        """Set the position of the Qbus output."""
        self.write_property(KEY_PROPERTIES_SHUTTER_POSITION, percentage)

    def read_slat_position(self) -> int | None:
        """Read the slat position of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_SLAT_POSITION, None)

    def write_slat_position(self, percentage: int) -> None:
        """Set the slat position of the Qbus output."""
        self.write_property(KEY_PROPERTIES_SLAT_POSITION, percentage)


class QbusMqttThermoState(QbusMqttState):
    """MQTT representation of a Qbus thermo output."""

    def __init__(
        self,
        data: dict | None = None,
        *,
        id: str | None = None,
        type: str | None = None,
    ) -> None:
        super().__init__(data, id=id, type=type)
    
    def read_current_temperature(self) -> float | None:
        """Read the current temperature of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_CURRENT_TEMPERATURE, None)

    def read_set_temperature(self) -> float | None:
        """Read the set temperature of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_SET_TEMPERATURE, None)
    
    def write_set_temperature(self, temperature: float) -> None:
        """Set the set temperature of the Qbus output."""
        self.write_property(KEY_PROPERTIES_SET_TEMPERATURE, temperature)

    def read_regime(self) -> str | None:
        """Read the regime of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_REGIME, None)
    
    def write_regime(self, regime: str) -> None:
        """Set the regime of the Qbus output."""
        self.write_property(KEY_PROPERTIES_REGIME, regime)


class QbusMqttGaugeState(QbusMqttState):
    """MQTT representation of a Qbus gauge output."""

    def __init__(
        self,
        data: dict | None = None,
        *,
        id: str | None = None,
        type: str | None = None,
    ) -> None:
        super().__init__(data, id=id, type=type)

    def read_value(self, key: GaugeKey) -> float:
        """Read the value of the Qbus output."""
        return self.read_property(key, 0)


class QbusMqttVentilationState(QbusMqttState):
    """MQTT representation of a Qbus ventilation output."""

    def __init__(
        self,
        data: dict | None = None,
        *,
        id: str | None = None,
        type: str | None = None,
    ) -> None:
        super().__init__(data, id=id, type=type)

    def read_co2(self) -> float:
        """Read the co2 of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_CO2, 0)


class QbusMqttHumidityState(QbusMqttState):
    """MQTT representation of a Qbus humidity output."""

    def __init__(
        self,
        data: dict | None = None,
        *,
        id: str | None = None,
        type: str | None = None,
    ) -> None:
        super().__init__(data, id=id, type=type)

    def read_value(self) -> float:
        """Read the value of the Qbus output."""
        return self.read_property(KEY_PROPERTIES_VALUE, 0)