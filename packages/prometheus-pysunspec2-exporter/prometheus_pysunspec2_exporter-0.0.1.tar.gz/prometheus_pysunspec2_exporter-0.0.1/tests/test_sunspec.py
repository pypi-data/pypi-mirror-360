import pytest

from unittest.mock import Mock
from pathlib import Path
from collections import Counter

from sunspec2.file.client import (  # type: ignore
    FileClientDevice,
    FileClientModel,
)

from prometheus_pysunspec2_exporter.sunspec import (
    normalise_label,
    PointValue,
    iter_group_values,
    ReconnectingSunspecReader,
)

from example_device import get_example_device


@pytest.mark.parametrize(
    "text, exp",
    [
        # Empty
        ("", ""),
        # Passthrough permtted chars
        ("Foo123", "Foo123"),
        ("Foo_123", "Foo_123"),
        # Convert disallowed to underscores
        ("oh no", "oh_no"),
        ("oh!no", "oh_no"),
        # Collapse runs of underscores
        ("oh___no", "oh_no"),
        ("oh - no", "oh_no"),
        # Strip underscores at ends
        ("_foo_", "foo"),
        ("[foo]", "foo"),
        # Translate % and / into words
        ("meters/sec", "meters_per_sec"),
        ("charge_%", "charge_Percent"),
    ],
)
def test_normalise_label(text: str, exp: str) -> None:
    assert normalise_label(text) == exp


ValuesDict = dict[str, tuple[str, PointValue]]


class TestIterGroupValues:

    @pytest.fixture
    def values(self) -> ValuesDict:
        device = get_example_device()
        device.scan()
        values = [
            (name, desc, value)
            for model in device.model_list
            for name, desc, value in iter_group_values(model)
        ]
        assert len(set(name for name, _, _ in values)) == len(values)
        return {name: (desc, value) for name, desc, value in values}

    def test_names_without_units(self, values: ValuesDict) -> None:
        #       +------------------- model
        #       |      +------ point
        #       |      |
        assert "common_Vr" in values

    def test_units_in_names(self, values: ValuesDict) -> None:
        #       +------------------- model
        #       |            +------ point
        #       |            |   +-- unit
        #       |            |   |
        assert "DERMeasureAC_LLV_V" in values

    def test_nested_unnumbered_groups(self, values: ValuesDict) -> None:
        #       +------------------ model
        #       |        +--------- group
        #       |        |      +-- point
        #       |        |      |
        assert "DERCtlAC_PFWInj_PF" in values

    def test_nested_numbered_groups(self, values: ValuesDict) -> None:
        #       +------------------------------- model
        #       |          +-------------------- outer group
        #       |          |   +---------------- outer group index
        #       |          |   | +-------------- inner group
        #       |          |   | |  +----------- inner group index
        #       |          |   | |  | +--------- point
        #       |          |   | |  | | +------- unit
        #       |          |   | |  | | |
        assert "DERVoltVar_Crv_2_Pt_3_V_VNomPct" in values

    def test_values(self, values: ValuesDict) -> None:
        assert values["common_Vr"][1] == "1.2.3"

    def test_values_with_scale_factor(self, values: ValuesDict) -> None:
        assert values["DERMeasureAC_A_A"][1] == 41.1

    def test_description(self, values: ValuesDict) -> None:
        assert values["DERVoltVar_Crv_2_Pt_3_V_VNomPct"][0] == (
            # Show model number, name, label and description
            "Model 705, DERVoltVar (DER Volt-Var): DER Volt-Var model.\n"
            # Show enumerated groups (with name, label and description)
            "Crv[2] (Stored Curves): Stored curve sets.\n"
            "Pt[3] (Stored Curve Points): Stored curve points.\n"
            # Show points (with name, label and description)
            "V (Voltage Point): Curve voltage point as percentage."
        )

    def test_description_enumerated(self, values: ValuesDict) -> None:
        assert values["DERCtlAC_AntiIslEna"][0] == (
            "Model 704, DERCtlAC (DER AC Controls): DER AC controls model.\n"
            # Example of non-enumerated group
            "AntiIslEna (Anti-Islanding Enable): Anti-islanding enable.\n"
            # Enumerated values
            "DISABLED = 0, ENABLED = 1"
        )

    def test_description_bitfield(self, values: ValuesDict) -> None:
        assert values["DERMeasureAC_DERMode"][0] == (
            "Model 701, DERMeasureAC (DER AC Measurement): DER AC measurement model.\n"
            "DERMode (DER Operational Characteristics): Current operational characteristics of the DER.\n"
            # Bitfield bits
            "GRID_FOLLOWING = Bit 0, GRID_FORMING = Bit 1, PV_CLIPPED = Bit 2"
        )


class TestReconnectingSunspecReader:

    @pytest.fixture
    def metric_read_log(self, monkeypatch) -> dict[str, int]:
        """
        Monitor (and count) calls to Model.read(), logged by model name.
        """
        log: dict[str, int] = Counter()

        orig_read = FileClientModel.read

        def read_wrapper(self, *args, **kwargs):
            log[self.gname] += 1
            return orig_read(self, *args, **kwargs)

        monkeypatch.setattr(FileClientModel, "read", read_wrapper)

        return log

    def test_no_exclusions(self, monkeypatch, metric_read_log: dict[str, int]) -> None:
        reader = ReconnectingSunspecReader(get_example_device)

        # Verify metrics look plausible
        metrics = {
            name: (desc, value) for name, desc, value in reader.read_all_values()
        }
        # Just a sanity check
        assert "common_ID" in metrics
        assert "DERWattVar_ID" in metrics
        assert "DERVoltWatt_ID" in metrics

        # First read should be accomplished via sync (so no read() calls)
        assert metric_read_log == {}

        # Subsequent reads should be accomplished via read
        list(reader.read_all_values())
        assert "common" in metric_read_log
        assert "DERWattVar" in metric_read_log
        assert "DERVoltVar" in metric_read_log
        assert all(cnt == 1 for cnt in metric_read_log.values())

        list(reader.read_all_values())
        assert all(cnt == 2 for cnt in metric_read_log.values())

    def test_exclusions(self, metric_read_log: dict[str, int]) -> None:
        reader = ReconnectingSunspecReader(
            get_example_device,
            {1, "DERWattVar"},
        )

        # Verify metrics look plausible
        metrics = {
            name: (desc, value) for name, desc, value in reader.read_all_values()
        }
        assert "common_ID" not in metrics
        assert "DERWattVar_ID" not in metrics
        assert "DERVoltWatt_ID" in metrics

        # First read should be accomplished via sync (so no read() calls)
        assert metric_read_log == {}

        # Subsequent reads should be accomplished via read, and only for
        # non-excluded metrics
        list(reader.read_all_values())
        assert "common" not in metric_read_log
        assert "DERWattVar" not in metric_read_log
        assert "DERVoltVar" in metric_read_log
        assert all(cnt == 1 for cnt in metric_read_log.values())

        list(reader.read_all_values())
        assert all(cnt == 2 for cnt in metric_read_log.values())

    def test_make_fails(self) -> None:
        reader = ReconnectingSunspecReader(Mock(side_effect=NotImplementedError))

        # Failure should pass upward
        with pytest.raises(NotImplementedError):
            list(reader.read_all_values())

        # Should keep on trying...
        with pytest.raises(NotImplementedError):
            list(reader.read_all_values())

    def test_read_fails(self, monkeypatch) -> None:
        def read_wrapper(self, *args, **kwargs):
            raise NotImplementedError()

        monkeypatch.setattr(FileClientModel, "read", read_wrapper)

        get_example_device_wrapper = Mock(side_effect=get_example_device)
        reader = ReconnectingSunspecReader(get_example_device_wrapper)
        assert len(get_example_device_wrapper.mock_calls) == 0

        # First values should come out OK
        list(reader.read_all_values())
        assert len(get_example_device_wrapper.mock_calls) == 1

        # But next attempt should fail because device read function fails
        with pytest.raises(NotImplementedError):
            list(reader.read_all_values())

        # Verify we reconnect when next read attempted
        assert len(get_example_device_wrapper.mock_calls) == 1
        list(reader.read_all_values())
        assert len(get_example_device_wrapper.mock_calls) == 2

    def test_close_ignore_errors(self, monkeypatch, caplog) -> None:
        def close_wrapper(self, *args, **kwargs):
            raise NotImplementedError()

        monkeypatch.setattr(FileClientDevice, "close", close_wrapper)

        reader = ReconnectingSunspecReader(get_example_device)

        # Close should do nothing if not already connected
        reader.close()

        # Values should come out OK
        list(reader.read_all_values())

        # No errors should have ocurred yet
        assert len(caplog.records) == 0

        # Close should be called and even if it fails should not crash
        reader.close()

        # But logs should be produced
        assert len(caplog.records) == 1
        assert "NotImplementedError" in caplog.text
