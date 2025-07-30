import pytest

from prometheus_pysunspec2_exporter.prometheus_metrics import (
    MetricType,
    MetricValue,
    create_metric_families,
)


def test_empty() -> None:
    assert create_metric_families([]) == []


def test_single_metric() -> None:
    out = create_metric_families(
        [
            MetricValue(
                name="foo",
                type=MetricType.gauge,
                help="Some help",
                labels={"qux": "quo"},
                value=123,
            ),
        ]
    )

    assert len(out) == 1
    assert out[0].name == "foo"
    assert out[0].documentation == "Some help"

    assert len(out[0].samples) == 1
    assert out[0].samples[0].value == 123
    assert out[0].samples[0].labels == {"qux": "quo"}


def test_multiple_different_labels_per_metric() -> None:
    out = create_metric_families(
        [
            MetricValue(
                name="foo",
                type=MetricType.gauge,
                help="Some help",
                labels={"qux": "quo"},
                value=123,
            ),
            MetricValue(
                name="foo",
                type=MetricType.gauge,
                help="Some help",
                labels={"bar": "baz"},
                value=321,
            ),
        ]
    )

    assert len(out) == 1
    assert out[0].name == "foo"
    assert out[0].documentation == "Some help"

    assert len(out[0].samples) == 2
    assert out[0].samples[0].value == 123
    assert out[0].samples[0].labels == {"qux": "quo", "bar": ""}
    assert out[0].samples[1].value == 321
    assert out[0].samples[1].labels == {"qux": "", "bar": "baz"}


def test_multiple_different_metrics() -> None:
    out = create_metric_families(
        [
            MetricValue(
                name="foo",
                type=MetricType.gauge,
                help="Some help",
                labels={"qux": "quo"},
                value=123,
            ),
            MetricValue(
                name="bar",
                type=MetricType.gauge,
                help="Some more help",
                labels={"bar": "baz"},
                value=321,
            ),
        ]
    )

    assert len(out) == 2
    assert out[0].name == "foo"
    assert out[0].documentation == "Some help"
    assert out[1].name == "bar"
    assert out[1].documentation == "Some more help"

    assert len(out[0].samples) == 1
    assert out[0].samples[0].value == 123
    assert out[0].samples[0].labels == {"qux": "quo"}

    assert len(out[1].samples) == 1
    assert out[1].samples[0].value == 321
    assert out[1].samples[0].labels == {"bar": "baz"}
