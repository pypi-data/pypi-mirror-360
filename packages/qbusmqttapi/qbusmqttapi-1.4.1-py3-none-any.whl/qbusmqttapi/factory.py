"""Qbus MQTT factory."""

import json
import logging
from dataclasses import dataclass
from typing import Any, TypeVar

from .const import (
    KEY_PROPERTIES_AUTHKEY,
    TOPIC_PREFIX,
)
from .discovery import QbusDiscovery, QbusMqttDevice
from .state import (
    QbusMqttDeviceState,
    QbusMqttGatewayState,
    QbusMqttState,
    StateAction,
    StateType,
)

_LOGGER = logging.getLogger(__name__)

type PublishPayloadType = str | bytes | int | float | None
type ReceivePayloadType = str | bytes | bytearray


@dataclass
class QbusMqttRequestMessage:
    """Qbus MQTT request data class."""

    topic: str
    payload: PublishPayloadType


class QbusMqttMessageFactory:
    """Factory methods for Qbus MQTT messages."""

    T = TypeVar("T", bound="QbusMqttState")

    def __init__(self) -> None:
        self._topic_factory = QbusMqttTopicFactory()

    def parse_gateway_state(self, payload: ReceivePayloadType) -> QbusMqttGatewayState | None:
        """Parse an MQTT message and return an instance
        of QbusMqttGatewayState if successful, otherwise None."""

        return self.deserialize(QbusMqttGatewayState, payload)

    def parse_discovery(self, payload: ReceivePayloadType) -> QbusDiscovery | None:
        """Parse an MQTT message and return an instance
        of QbusDiscovery if successful, otherwise None."""

        discovery: QbusDiscovery | None = self.deserialize(QbusDiscovery, payload)

        # Discovery data must include the Qbus device type and name.
        if discovery is not None and len(discovery.devices) == 0:
            _LOGGER.error("Incomplete discovery payload: %s", payload)
            return None

        return discovery

    def parse_device_state(self, payload: ReceivePayloadType) -> QbusMqttDeviceState | None:
        """Parse an MQTT message and return an instance
        of QbusMqttDeviceState if successful, otherwise None."""

        return self.deserialize(QbusMqttDeviceState, payload)

    def parse_output_state(self, cls: type[T], payload: ReceivePayloadType) -> T | None:
        """Parse an MQTT message and return an instance
        of T if successful, otherwise None."""

        return self.deserialize(cls, payload)

    def create_device_activate_request(self, device: QbusMqttDevice, prefix: str = TOPIC_PREFIX) -> QbusMqttRequestMessage:
        """Create a message to request device activation."""
        state = QbusMqttState(id=device.id, type=StateType.ACTION, action=StateAction.ACTIVATE)
        state.write_property(KEY_PROPERTIES_AUTHKEY, "ubielite")

        return QbusMqttRequestMessage(
            self._topic_factory.get_device_command_topic(device.id, prefix),
            self.serialize(state),
        )

    def create_device_state_request(self, device: QbusMqttDevice, prefix: str = TOPIC_PREFIX) -> QbusMqttRequestMessage:
        """Create a message to request a device state."""
        return QbusMqttRequestMessage(self._topic_factory.get_get_state_topic(prefix), json.dumps([device.id]))

    def create_state_request(self, ids: list[str], prefix: str = TOPIC_PREFIX) -> QbusMqttRequestMessage:
        """Create a message to request states."""
        return QbusMqttRequestMessage(self._topic_factory.get_get_state_topic(prefix), json.dumps(ids))

    def create_set_output_state_request(
        self, device: QbusMqttDevice, state: QbusMqttState, prefix: str = TOPIC_PREFIX
    ) -> QbusMqttRequestMessage:
        """Create a message to update the output state."""
        return QbusMqttRequestMessage(
            self._topic_factory.get_output_command_topic(device.id, state.id, prefix),
            self.serialize(state),
        )

    def serialize(self, obj: Any) -> str:
        """Convert an object to json payload."""
        return json.dumps(obj, cls=IgnoreNoneJsonEncoder)

    def deserialize(self, state_cls: type[Any], payload: ReceivePayloadType) -> Any | None:
        """Parse an MQTT message and return the requested type if successful, otherwise None."""

        if not payload:
            _LOGGER.warning("Empty state payload for %s", state_cls.__name__)
            return None

        try:
            data = json.loads(payload)
        except ValueError:
            _LOGGER.error("Invalid state payload for %s: %s", state_cls.__name__, payload)
            return None

        return state_cls(data)


class QbusMqttTopicFactory:
    """Factory methods for topics of the Qbus MQTT API."""

    def get_gateway_state_topic(self, prefix: str = TOPIC_PREFIX) -> str:
        """Return the gateway state topic."""
        return f"{prefix}/state"

    def get_get_config_topic(self, prefix: str = TOPIC_PREFIX) -> str:
        """Return the getConfig topic."""
        return f"{prefix}/getConfig"

    def get_config_topic(self, prefix: str = TOPIC_PREFIX) -> str:
        """Return the config topic."""
        return f"{prefix}/config"

    def get_get_state_topic(self, prefix: str = TOPIC_PREFIX) -> str:
        """Return the getState topic."""
        return f"{prefix}/getState"

    def get_device_state_topic(self, device_id: str, prefix: str = TOPIC_PREFIX) -> str:
        """Return the state topic."""
        return f"{prefix}/{device_id}/state"

    def get_device_command_topic(self, device_id: str, prefix: str = TOPIC_PREFIX) -> str:
        """Return the 'set state' topic."""
        return f"{prefix}/{device_id}/setState"

    def get_output_command_topic(self, device_id: str, entity_id: str, prefix: str = TOPIC_PREFIX) -> str:
        """Return the 'set state' topic of an output."""
        return f"{prefix}/{device_id}/{entity_id}/setState"

    def get_output_state_topic(self, device_id: str, entity_id: str, prefix: str = TOPIC_PREFIX) -> str:
        """Return the state topic of an output."""
        return f"{prefix}/{device_id}/{entity_id}/state"


class IgnoreNoneJsonEncoder(json.JSONEncoder):
    """A json encoder to ignore None values when serializing."""

    def default(self, o: Any) -> Any:
        if hasattr(o, "__dict__"):
            # Filter out None values
            return {k: v for k, v in o.__dict__.items() if v is not None}
        return super().default(o)
