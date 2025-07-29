"""CCL device mapping."""

from __future__ import annotations

import logging
import time
from typing import Callable, TypedDict

from .exception import CCLDataUpdateException
from .sensor import CCLSensor

_LOGGER = logging.getLogger(__name__)

CCL_DEVICE_INFO_TYPES = ("serial_no", "mac_address", "model", "fw_ver")


class CCLDevice:
    """Mapping for a CCL device."""

    def __init__(self, passkey: str):
        """Initialize a CCL device."""

        class Info(TypedDict):
            """Store device information."""
            fw_ver: str | None
            last_update_time: float | None
            mac_address: str | None
            model: str | None
            passkey: str
            serial_no: str | None


        self._info: Info = {
            "fw_ver": None,
            "last_update_time": None,
            "mac_address": None,
            "model": None,
            "passkey": passkey,
            "serial_no": None,
        }

        self._sensors: dict[str, CCLSensor] = {}
        self._update_callback: Callable[[], None] | None = None

        self._new_sensors: list[CCLSensor] | None = []
        self._new_sensor_callback: Callable[[], None] | None = None

    @property
    def passkey(self) -> str:
        """Return the passkey."""
        return self._info["passkey"]

    @property
    def device_id(self) -> str | None:
        """Return the device ID."""
        if self.mac_address is None:
            return None
        return self.mac_address.replace(":", "").lower()[-6:]

    @property
    def last_update_time(self) -> str | None:
        """Return the last update time."""
        return self._info["last_update_time"]

    @property
    def name(self) -> str | None:
        """Return the display name."""
        if self.device_id is not None:
            return self.model + " - " + self.device_id
        return self._info["model"]

    @property
    def mac_address(self) -> str | None:
        """Return the MAC address."""
        return self._info["mac_address"]

    @property
    def model(self) -> str | None:
        """Return the model."""
        return self._info["model"]

    @property
    def fw_ver(self) -> str | None:
        """Return the firmware version."""
        return self._info["fw_ver"]

    def get_sensors(self) -> dict[str, CCLSensor]:
        """Get all types of sensor data under this device."""
        if self._info["last_update_time"] is None:
            raise CCLDataUpdateException("Device is offline or not ready")
        if len(self._sensors) == 0 or time.monotonic() - self._info["last_update_time"] > 600:
            raise CCLDataUpdateException("Device is offline or not ready")
        return self._sensors
    
    def set_update_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback function to update sensor data."""
        self._update_callback = callback
        
    def set_new_sensor_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback function to add a new sensor."""
        self._new_sensor_callback = callback


    def update_info(self, new_info: dict[str, None | str]) -> None:
        """Add or update device info."""
        for key, value in new_info.items():
            if key in self._info:
                self._info[key] = str(value)
        self._info["last_update_time"] = time.monotonic()

    def push_updates(self) -> None:
        """Push sensor updates."""
        add_count = self._publish_new_sensors()
        if add_count > 0:
            _LOGGER.debug(
                "Added %s new sensors for device %s at %s.",
                add_count,
                self.device_id,
                self.last_update_time,
            )

        self._publish_updates()
        _LOGGER.debug(
            "Updating sensor data for device %s at %s.",
            self.device_id,
            self.last_update_time,
        )
        
    def process_data(self, data: dict[str, None | str | int | float]) -> None:
        """Add or update all sensor values."""
        for key, value in data.items():
            if key not in self._sensors:
                self._sensors[key] = CCLSensor(key)
                self._new_sensors.append(self._sensors[key])
            self._sensors[key].last_update_time = time.monotonic()
            self._sensors[key].value = value
        self.push_updates()

    def _publish_updates(self) -> None:
        """Call the function to update sensor data."""
        try:
            self._update_callback(self._sensors)
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOGGER.warning(
                "Error while updating sensors for device %s: %s",
                self.device_id,
                err,
            )

    def _publish_new_sensors(self) -> int:
        """Schedule all registered callbacks to add new sensors."""
        success_count = 0
        error_count = 0
        for sensor in self._new_sensors[:]:
            try:
                assert self._new_sensor_callback is not None
                if self._new_sensor_callback(sensor) is not True:
                    raise CCLDataUpdateException("Failed to publish new sensor")
                self._new_sensors.remove(sensor)
                success_count += 1
            except Exception:  # pylint: disable=broad-exception-caught
                error_count += 1
        if error_count > 0:
            _LOGGER.warning(
                    "Failed to add %s sensors for device %s",
                    error_count,
                    self.device_id,
                )
        return success_count
