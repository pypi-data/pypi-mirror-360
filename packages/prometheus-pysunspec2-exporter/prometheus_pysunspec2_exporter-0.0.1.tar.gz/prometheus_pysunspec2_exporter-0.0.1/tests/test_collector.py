import pytest
from unittest.mock import Mock

from pathlib import Path

from prometheus_pysunspec2_exporter.sunspec import (
    ReconnectingSunspecReader,
)

from prometheus_pysunspec2_exporter.collector import (
    DeviceConfig,
    SunSpecCollector,
)

from example_device import get_example_device


def test_empty() -> None:
    c = SunSpecCollector([])
    assert list(c.collect()) == []


def test_working() -> None:
    c = SunSpecCollector(
        [
            DeviceConfig(
                labels={"foo": "bar"},
                reader=ReconnectingSunspecReader(get_example_device),
            ),
            DeviceConfig(
                labels={"qux": "quo"},
                reader=ReconnectingSunspecReader(get_example_device),
            ),
        ]
    )

    metrics = {m.name: m for m in c.collect()}

    # Check we have metrics from both devices (checking both the 'sunspec_up'
    # metric and a point from both devices
    for metric_name in ["sunspec_up", "sunspec_common_ID"]:
        assert len(metrics[metric_name].samples) == 2
        assert {
            frozenset(sample.labels.items()) for sample in metrics[metric_name].samples
        } == {
            frozenset({("foo", "bar"), ("qux", "")}),
            frozenset({("foo", ""), ("qux", "quo")}),
        }

    # Check both devices up
    assert [sample.value for sample in metrics["sunspec_up"].samples] == [1, 1]


def test_not_working() -> None:
    c = SunSpecCollector(
        [
            DeviceConfig(
                labels={"foo": "bar"},
                reader=ReconnectingSunspecReader(Mock(side_effect=NotImplementedError)),
            ),
        ]
    )

    # Shouldn't crash...
    metrics = {m.name: m for m in c.collect()}

    # Should be down, though
    assert [sample.value for sample in metrics["sunspec_up"].samples] == [0]
