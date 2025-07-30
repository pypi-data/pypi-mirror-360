"""
The :py:func:`create_metric_families` utility for creating Prometheus Metric
objects from a disorganised list of possibly repeated metrics.
"""

from typing import NamedTuple

from enum import Enum, auto
from collections import defaultdict

from prometheus_client.core import (
    Metric,
    GaugeMetricFamily,
    CounterMetricFamily,
)


class MetricType(Enum):
    """Types of Prometheus metrics."""

    counter = auto()
    gauge = auto()
    # ... not very complete!


class MetricValue(NamedTuple):
    """
    Represents a metric value to be exported (and its associated metadata).
    """

    name: str
    type: MetricType
    help: str
    labels: dict[str, str]
    value: int | float


def create_metric_families(metric_values: list[MetricValue]) -> list[Metric]:
    """
    Convert a series of metric observations with possible repeated metrics with
    different sets of labels and return a single coherent set of Prometheus
    metric family objects.
    """
    # Accumulate the complete set of labels used by each named metric.
    metric_labels: defaultdict[str, set[str]] = defaultdict(set)
    for value in metric_values:
        metric_labels[value.name].update(value.labels)

    # Create the metric objects
    metrics: dict[str, CounterMetricFamily | GaugeMetricFamily] = {}
    for value in metric_values:
        # Create metric family objects the first time we encounter each metric
        if value.name not in metrics:
            labels = list(metric_labels[value.name])
            match value.type:
                case MetricType.counter:
                    metrics[value.name] = CounterMetricFamily(
                        value.name, value.help, labels=labels
                    )
                case MetricType.gauge:
                    metrics[value.name] = GaugeMetricFamily(
                        value.name, value.help, labels=labels
                    )
                case _:
                    raise NotImplementedError(value.type)

        metrics[value.name].add_metric(
            [value.labels.get(label, "") for label in metric_labels[value.name]],
            value.value,
        )

    return list(metrics.values())
