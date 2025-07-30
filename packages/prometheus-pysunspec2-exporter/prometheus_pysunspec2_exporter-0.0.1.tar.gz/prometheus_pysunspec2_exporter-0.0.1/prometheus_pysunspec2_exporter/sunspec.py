"""
The :py:func:`iter_group_values` function enumerates (data) points in a Sunspec
module complete with Prometheus-friendly names and help strings.
"""

from typing import Iterable, Callable

import re
import logging

from sunspec2.device import Group, Device  # type: ignore


logger = logging.getLogger(__name__)


def normalise_label(text: str) -> str:
    """
    Replace all non-prometheus-label-friendly characters with underscores.
    Expands "%" to "Percent" and "/" to " per " to make unit names continue to
    be readable.
    """
    text = text.replace("%", "Percent")
    text = text.replace("/", " per ")
    text = re.sub(r"[^a-zA-Z0-9_]", "_", text)
    text = re.sub(r"__+", "_", text)
    text = text.strip("_")
    return text


PointValue = int | float | str | None


def iter_group_values(
    group: Group,
) -> Iterable[tuple[str, str, PointValue]]:
    """
    Given a Sunspec Group (or Module) object, return an iterator of (name,
    description, value) triples where:

    * 'name' is a Prometheus metric name suitable for that point
    * 'description' is a combination of the point (and all parent group)'s full
      labels and their descrpitions.
    * 'value' is the computed value (cvalue) of the point.
    """
    # Assemble group name/description
    if group.index is None:
        group_name = group.gname
    else:
        group_name = f"{group.gname}[{group.index}]"

    if hasattr(group, "model_id"):
        model_id = f"Model {group.model_id}, "
    else:
        model_id = ""

    if group_label := group.gdef.get("label"):
        group_label = f"{model_id}{group_name} ({group_label})"
    else:
        group_label = model_id + group_name

    if group_desc := group.gdef.get("desc"):
        group_desc = f"{group_label}: {group_desc}"
    else:
        group_desc = group_label

    # Enumerate points
    for name, point in group.points.items():
        metric_name = normalise_label(
            f"{group_name}_{name}_{point.pdef.get('units', '')}"
        )

        if point_label := point.pdef.get("label"):
            point_label = f"{name} ({point_label})"
        else:
            point_label = name

        if point_desc := point.pdef.get("desc"):
            point_desc = f"{point_label}: {point_desc}"
        else:
            point_desc = point_label

        if symbols := point.pdef.get("symbols"):
            prefix = "Bit " if point.pdef["type"].startswith("bitfield") else ""
            symbol_desc = ", ".join(
                f"{s['name']} = {prefix}{s['value']}" for s in symbols
            )
            point_desc = f"{point_desc}\n{symbol_desc}"

        combined_desc = f"{group_desc}\n{point_desc}"

        yield (metric_name, combined_desc, point.cvalue)

    # Recurse into subgroups
    for name, subgroups in group.groups.items():
        if not isinstance(subgroups, list):
            subgroups = [subgroups]

        for subgroup in subgroups:
            for point_name, point_desc, point_value in iter_group_values(subgroup):
                combined_name = normalise_label(f"{group_name}_{point_name}")
                combined_desc = f"{group_desc}\n{point_desc}"
                yield (combined_name, combined_desc, point_value)


class ReconnectingSunspecReader:
    """
    Reads values from a Sunspec device, re-connecting whenever a prior
    request has failed.
    """

    _make_device: Callable[[], Device]
    _excluded_models: set[str | int]

    _device: Device | None

    def __init__(
        self,
        make_device: Callable[[], Device],
        excluded_models: set[str | int] = set(),
    ) -> None:
        """
        Parameters
        ==========
        make_device : fn() -> Device
            A zero-argument constructor which creates a fresh new Sunspec
            Device object.
        excluded_models : {str | int, ...}
            Model names (e.g. 'common') or numbers (e.g. 1) to exclude skip
            when reading from the device.
        """
        self._make_device = make_device
        self._excluded_models = excluded_models

        self._device = None

    def read_all_values(self) -> Iterable[tuple[str, str, PointValue]]:
        """
        Read all values from the sunspec device, along with Prometheus-friendly
        names and descriptions (see :py:func:`iter_group_values`). Values from
        models in :py:attr:`excluded_models` are skipped.

        If not already connected, will (re)connect to the Sunspec device first
        and enumerate all models and values. If already connected, will re-read
        all non-excluded models first.

        If a Sunspec/device error occurs, the relevant exception will be thrown
        and, internally, the device connection will be closed. A new one will
        be made on the next read attempt.
        """
        try:
            # (Re-)connect if required and refresh all models
            if self._device is None:
                self._device = self._make_device()
                self._device.scan()
            else:
                for model in self._device.model_list:
                    if (
                        model.model_id not in self._excluded_models
                        and model.gname not in self._excluded_models
                    ):
                        model.read()

            # Fetch metrics
            for model in self._device.model_list:
                if (
                    model.model_id not in self._excluded_models
                    and model.gname not in self._excluded_models
                ):
                    yield from iter_group_values(model)
        except Exception:
            # Disconnect on failures
            self.close()
            raise

    def close(self) -> None:
        """
        Close the connection to the sunspec device, or do nothing if not
        currently connected.
        """
        if self._device is not None:
            try:
                self._device.close()
            except Exception:
                logger.exception("Unable to close connection")
            self._device = None
