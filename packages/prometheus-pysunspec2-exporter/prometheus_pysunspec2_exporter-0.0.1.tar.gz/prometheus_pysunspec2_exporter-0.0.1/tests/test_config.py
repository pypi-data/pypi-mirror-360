import pytest

import yaml

from prometheus_pysunspec2_exporter.config import (
    ConfigError,
    parse_config,
)

from example_device import example_device_file


def test_empty() -> None:
    assert parse_config({"devices": []}) == []


def test_valid() -> None:
    config = yaml.safe_load(
        f"""
            devices:
              # Minimal
              - file:
                  filename: {str(example_device_file)!r}
              # All the bells-and-whistles
              - file:
                  filename: {str(example_device_file)!r}
                excluded_models:
                  - 1
                  - common
                labels:
                  filename: example
                  foo: bar
        """
    )

    device_configs = parse_config(config)

    assert len(device_configs) == 2

    # Check labels combine both the device parameters and specified labels (if
    # any)
    assert device_configs[0].labels == {
        "device_type": "file",
        "filename": str(example_device_file),
    }
    assert device_configs[1].labels == {
        "device_type": "file",
        "filename": "example",  # Overridden
        "foo": "bar",  # Extra
    }

    # Check exclusions
    assert device_configs[0].reader._excluded_models == set()
    assert device_configs[1].reader._excluded_models == {1, "common"}

    # Check working readers
    for device_config in device_configs:
        assert list(device_config.reader.read_all_values())


@pytest.mark.parametrize(
    "config, exp_error_text",
    [
        # Not a top-level dict
        ("", "Configuration must be a dictionary."),
        # Top-level doesn't have 'devices'
        ("foo: bar", "Configuration must contain a 'devices' list"),
        # Top-level has other stuff too
        ("devices: []\nfoo: bar", "Unexpected config key: foo"),
        # Devices not a list
        ("devices: bar", "'devices' must be a list."),
        # Device not a dict
        ("devices: [foo]", "Device defitions must be dictionaries."),
        # Device doesn't contain a device type
        ("devices: [{}]", "Device must specify one of file, tcp, rtu"),
        (
            "devices: [{excluded_models: [1]}]",
            "Device must specify one of file, tcp, rtu",
        ),
        # Multiple devices types specified
        (
            """
                devices:
                  - file:
                      filename: foo
                    tcp:
                      ipaddr: bar
            """,
            "Unexpected device key: tcp",
        ),
        # Device type isn't a dict
        ("devices: [{file: foo}]", "Device file value must be a dictionary."),
        # Unknown argument to device
        (
            "devices: [{file: {ipaddr: foo}}]",
            "Unknown file option: ipaddr (available options: filename, addr)",
        ),
        # Exclusions isn't a list
        (
            "devices: [{file: {filename: foo}, excluded_models: xxx}]",
            "Device 'excluded_models' must be a list.",
        ),
        # Exclusions contains a non-string-or-integer value
        (
            "devices: [{file: {filename: foo}, excluded_models: [null]}]",
            "Device 'excluded_models' entries must integers or strings.",
        ),
        # Labels must be a dict
        (
            "devices: [{file: {filename: foo}, labels: []}]",
            "Device 'labels' must be a dictionary.",
        ),
        # Extra key in device
        (
            "devices: [{file: {filename: foo}, foo: []}]",
            "Unexpected device key: foo",
        ),
    ],
)
def test_invalid(config: str, exp_error_text: str) -> None:
    with pytest.raises(ConfigError) as exc_info:
        parse_config(yaml.safe_load(config))

    assert str(exc_info.value) == exp_error_text
