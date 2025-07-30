from typing import NamedTuple, Iterable

import logging

from prometheus_client.registry import Collector
from prometheus_client.core import Metric

from prometheus_pysunspec2_exporter.prometheus_metrics import (
    MetricType,
    MetricValue,
    create_metric_families,
)
from prometheus_pysunspec2_exporter.sunspec import ReconnectingSunspecReader


logger = logging.getLogger(__name__)


class DeviceConfig(NamedTuple):
    """
    Configuration for a single device to collect sunspec metrics for.
    """

    labels: dict[str, str]
    reader: ReconnectingSunspecReader


class SunSpecCollector(Collector):
    """
    Prometheus collector for one or more Sunspec devices.
    """

    _devices: list[DeviceConfig]

    def __init__(self, devices: list[DeviceConfig]) -> None:
        self._devices = devices

    def collect(self) -> Iterable[Metric]:
        metric_values = []

        for labels, reader in self._devices:
            try:
                # NB: Extended using a list so we atomically add all values, or
                # none if an exception is thrown
                metric_values.extend(
                    [
                        MetricValue(
                            name=f"sunspec_{name}",
                            help=desc,
                            value=value,
                            labels=labels,
                            type=MetricType.gauge,
                        )
                        for (name, desc, value) in reader.read_all_values()
                        if isinstance(value, (int, float))
                    ]
                )
                this_device_up = 1
            except Exception:
                logger.exception(f"Collection for device {labels} failed")
                this_device_up = 0

            metric_values.append(
                MetricValue(
                    name="sunspec_up",
                    help="Was SunSpec data scrape successful?",
                    value=this_device_up,
                    labels=labels,
                    type=MetricType.gauge,
                )
            )

        yield from create_metric_families(metric_values)
