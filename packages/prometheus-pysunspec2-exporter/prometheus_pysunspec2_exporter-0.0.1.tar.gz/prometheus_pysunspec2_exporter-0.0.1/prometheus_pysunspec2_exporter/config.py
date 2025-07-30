"""
Config file parser.

See expected format in readme.
"""

from typing import Any

from functools import partial
from inspect import signature

from sunspec2.file.client import FileClientDevice  # type: ignore
from sunspec2.modbus.client import (  # type: ignore
    SunSpecModbusClientDeviceTCP,
    SunSpecModbusClientDeviceRTU,
)

from prometheus_pysunspec2_exporter.sunspec import ReconnectingSunspecReader
from prometheus_pysunspec2_exporter.collector import DeviceConfig


device_classes = {
    "file": FileClientDevice,
    "tcp": SunSpecModbusClientDeviceTCP,
    "rtu": SunSpecModbusClientDeviceRTU,
}


class ConfigError(Exception):
    """Base class for all configuration errors."""


def parse_config(config: Any) -> list[DeviceConfig]:
    """
    Top level config parser. Takes a parsed YAML config file and returns the
    device configuration encoded within it, or throws a ConfigError if invalid.
    """
    if not isinstance(config, dict):
        raise ConfigError("Configuration must be a dictionary.")

    if "devices" not in config:
        raise ConfigError("Configuration must contain a 'devices' list")
    clients = parse_config_devices(config.pop("devices"))

    if config:
        raise ConfigError(f"Unexpected config key: {', '.join(config)}")

    return clients


def parse_config_devices(devices: Any) -> list[DeviceConfig]:
    if not isinstance(devices, list):
        raise ConfigError("'devices' must be a list.")

    return [parse_config_device(device) for device in devices]


def parse_config_device(device: Any) -> DeviceConfig:
    if not isinstance(device, dict):
        raise ConfigError("Device defitions must be dictionaries.")

    # Find device type
    for device_type, device_class in device_classes.items():
        if device_type in device:
            device_kwargs = device.pop(device_type)
            break
    else:
        raise ConfigError(
            f"Device must specify one of {', '.join(device_classes)}",
        )

    # Verify device arguments
    if not isinstance(device_kwargs, dict):
        raise ConfigError(f"Device {device_type} value must be a dictionary.")
    device_class_params = list(signature(device_class).parameters)
    try:
        device_class_params.remove("model_class")
    except ValueError:
        pass
    for kwarg in device_kwargs:
        if kwarg not in device_class_params:
            raise ConfigError(
                f"Unknown {device_type} option: {kwarg} "
                f"(available options: {', '.join(device_class_params)})"
            )

    # Gather exclusions
    excluded_models = device.pop("excluded_models", list())
    if not isinstance(excluded_models, list):
        raise ConfigError("Device 'excluded_models' must be a list.")
    for entry in excluded_models:
        if not isinstance(entry, (int, str)):
            raise ConfigError(
                "Device 'excluded_models' entries must integers or strings."
            )

    # Assemble labels
    extra_labels = device.pop("labels", {})
    if not isinstance(extra_labels, dict):
        raise ConfigError("Device 'labels' must be a dictionary.")
    labels = (
        {"device_type": device_type}
        | {str(k): str(v) for k, v in device_kwargs.items()}
        | {str(k): str(v) for k, v in extra_labels.items()}
    )

    if device:
        raise ConfigError(f"Unexpected device key: {', '.join(device)}")

    return DeviceConfig(
        labels,
        ReconnectingSunspecReader(
            partial(device_class, **device_kwargs),
            set(excluded_models),
        ),
    )
