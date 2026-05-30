# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import pytest

from gotenberg_client.options import CookieJar
from gotenberg_client.options import DownloadFromUrl
from gotenberg_client.options import Measurement
from gotenberg_client.options import MeasurementUnitType
from gotenberg_client.options import PageMarginsType
from gotenberg_client.options import PageOrientation
from gotenberg_client.options import PageSize
from gotenberg_client.options import PdfAFormat


class TestMeasurement:
    @pytest.mark.parametrize(
        ("value", "unit", "field", "expected"),
        [
            # Undefined unit: value is passed through as-is (no suffix)
            (10, MeasurementUnitType.Undefined, "paperWidth", {"paperWidth": "10"}),
            (8.5, MeasurementUnitType.Undefined, "paperWidth", {"paperWidth": "8.5"}),
            # Named units produce "<value><unit_suffix>" strings
            (8.5, MeasurementUnitType.Inches, "paperWidth", {"paperWidth": "8.5in"}),
            (210, MeasurementUnitType.Millimeters, "paperHeight", {"paperHeight": "210mm"}),
            (21.0, MeasurementUnitType.Centimeters, "marginTop", {"marginTop": "21.0cm"}),
            (1920, MeasurementUnitType.Pixels, "paperWidth", {"paperWidth": "1920px"}),
            (72, MeasurementUnitType.Points, "marginLeft", {"marginLeft": "72pt"}),
            (50, MeasurementUnitType.Percent, "marginBottom", {"marginBottom": "50pc"}),
            # Zero with a unit produces a truthy string ("0in"), so it IS included
            (0, MeasurementUnitType.Inches, "marginTop", {"marginTop": "0in"}),
        ],
    )
    def test_to_form(
        self,
        value: float | int,
        unit: MeasurementUnitType,
        field: str,
        expected: dict[str, str],
    ) -> None:
        assert Measurement(value, unit).to_form(field) == expected

    def test_zero_value_undefined_unit_is_included(self) -> None:
        # optional_to_form only excludes None, not 0; zero without a unit is still emitted
        assert Measurement(0).to_form("paperWidth") == {"paperWidth": "0"}

    def test_default_unit_is_undefined(self) -> None:
        assert Measurement(5).unit == MeasurementUnitType.Undefined

    def test_form_key_is_passed_through(self) -> None:
        result = Measurement(3, MeasurementUnitType.Inches).to_form("customKey")
        assert "customKey" in result
        assert result["customKey"] == "3in"


class TestPageSize:
    def test_both_dimensions_undefined_unit(self) -> None:
        result = PageSize(width=Measurement(8.5), height=Measurement(11)).to_form()
        assert result == {"paperWidth": "8.5", "paperHeight": "11"}

    def test_both_dimensions_with_unit(self) -> None:
        result = PageSize(
            width=Measurement(210, MeasurementUnitType.Millimeters),
            height=Measurement(297, MeasurementUnitType.Millimeters),
        ).to_form()
        assert result == {"paperWidth": "210mm", "paperHeight": "297mm"}

    @pytest.mark.parametrize(
        ("width", "height", "expected_keys"),
        [
            (Measurement(8.5, MeasurementUnitType.Inches), None, {"paperWidth"}),
            (None, Measurement(11, MeasurementUnitType.Inches), {"paperHeight"}),
            (None, None, set()),
        ],
    )
    def test_partial_and_empty(
        self,
        width: Measurement | None,
        height: Measurement | None,
        expected_keys: set[str],
    ) -> None:
        result = PageSize(width=width, height=height).to_form()
        assert set(result.keys()) == expected_keys

    def test_mixed_units(self) -> None:
        result = PageSize(
            width=Measurement(8.5, MeasurementUnitType.Inches),
            height=Measurement(279, MeasurementUnitType.Millimeters),
        ).to_form()
        assert result == {"paperWidth": "8.5in", "paperHeight": "279mm"}


class TestPageMarginsType:
    def test_all_margins(self) -> None:
        margins = PageMarginsType(
            top=Measurement(1, MeasurementUnitType.Inches),
            bottom=Measurement(1, MeasurementUnitType.Inches),
            left=Measurement(1, MeasurementUnitType.Inches),
            right=Measurement(1, MeasurementUnitType.Inches),
        )
        assert margins.to_form() == {
            "marginTop": "1in",
            "marginBottom": "1in",
            "marginLeft": "1in",
            "marginRight": "1in",
        }

    def test_no_margins(self) -> None:
        assert PageMarginsType().to_form() == {}

    @pytest.mark.parametrize(
        ("top", "bottom", "left", "right", "expected_keys"),
        [
            (Measurement(2, MeasurementUnitType.Centimeters), None, None, None, {"marginTop"}),
            (None, Measurement(2, MeasurementUnitType.Centimeters), None, None, {"marginBottom"}),
            (None, None, Measurement(2, MeasurementUnitType.Centimeters), None, {"marginLeft"}),
            (None, None, None, Measurement(2, MeasurementUnitType.Centimeters), {"marginRight"}),
            (
                Measurement(10, MeasurementUnitType.Millimeters),
                None,
                None,
                Measurement(5, MeasurementUnitType.Millimeters),
                {"marginTop", "marginRight"},
            ),
        ],
    )
    def test_single_and_partial_margins(
        self,
        top: Measurement | None,
        bottom: Measurement | None,
        left: Measurement | None,
        right: Measurement | None,
        expected_keys: set[str],
    ) -> None:
        result = PageMarginsType(top=top, bottom=bottom, left=left, right=right).to_form()
        assert set(result.keys()) == expected_keys

    def test_mixed_units(self) -> None:
        result = PageMarginsType(
            top=Measurement(1, MeasurementUnitType.Inches),
            bottom=Measurement(25, MeasurementUnitType.Millimeters),
            left=Measurement(72, MeasurementUnitType.Points),
            right=Measurement(10, MeasurementUnitType.Percent),
        ).to_form()
        assert result == {
            "marginTop": "1in",
            "marginBottom": "25mm",
            "marginLeft": "72pt",
            "marginRight": "10pc",
        }


class TestCookieJar:
    def test_required_fields_only(self) -> None:
        result = CookieJar(name="session", value="abc123", domain="example.com").asdict()
        assert result == {"name": "session", "value": "abc123", "domain": "example.com"}

    def test_all_fields(self) -> None:
        result = CookieJar(
            name="auth",
            value="token_value",
            domain="example.com",
            path="/",
            secure=True,
            http_only=True,
            same_site="Strict",
        ).asdict()
        assert result == {
            "name": "auth",
            "value": "token_value",
            "domain": "example.com",
            "path": "/",
            "secure": True,
            "httpOnly": True,
            "sameSite": "Strict",
        }

    @pytest.mark.parametrize("same_site", ["Strict", "Lax", "None"])
    def test_same_site_values(self, same_site: str) -> None:
        result = CookieJar(name="s", value="v", domain="d", same_site=same_site).asdict()  # type: ignore[arg-type]
        assert result["sameSite"] == same_site

    @pytest.mark.parametrize(
        ("kwargs", "absent_keys"),
        [
            # False/None optional fields are excluded from the dict
            ({"secure": False}, ["secure"]),
            ({"http_only": False}, ["httpOnly"]),
            ({"path": None}, ["path"]),
            ({"same_site": None}, ["sameSite"]),
        ],
    )
    def test_optional_fields_excluded_when_falsy(self, kwargs: dict, absent_keys: list[str]) -> None:
        cookie = CookieJar(name="session", value="abc123", domain="example.com", **kwargs)
        result = cookie.asdict()
        for key in absent_keys:
            assert key not in result


class TestDownloadFromUrl:
    def test_url_only(self) -> None:
        result = DownloadFromUrl(url="https://example.com/file.pdf").asdict()
        assert result == {"url": "https://example.com/file.pdf", "embedded": False}

    def test_embedded_true(self) -> None:
        result = DownloadFromUrl(url="https://example.com/file.pdf", embedded=True).asdict()
        assert result["embedded"] is True

    def test_all_fields(self) -> None:
        headers = {"Authorization": "Bearer secret"}
        result = DownloadFromUrl(
            url="https://example.com/stamp.pdf",
            extra_http_headers=headers,
            embedded=True,
            field="stamp",
        ).asdict()
        assert result == {
            "url": "https://example.com/stamp.pdf",
            "embedded": True,
            "extraHttpHeaders": headers,
            "field": "stamp",
        }

    @pytest.mark.parametrize("field_value", ["watermark", "stamp", "embedded", ""])
    def test_field_included_when_not_none(self, field_value: str) -> None:
        result = DownloadFromUrl(url="https://example.com/f.pdf", field=field_value).asdict()
        assert "field" in result
        assert result["field"] == field_value

    def test_field_excluded_when_none(self) -> None:
        result = DownloadFromUrl(url="https://example.com/f.pdf", field=None).asdict()
        assert "field" not in result

    def test_extra_http_headers_excluded_when_none(self) -> None:
        result = DownloadFromUrl(url="https://example.com/f.pdf").asdict()
        assert "extraHttpHeaders" not in result

    def test_extra_http_headers_included_when_present(self) -> None:
        headers = {"X-Token": "abc", "X-Other": "val"}
        result = DownloadFromUrl(url="https://example.com/f.pdf", extra_http_headers=headers).asdict()
        assert result["extraHttpHeaders"] == headers


class TestPdfAFormat:
    @pytest.mark.parametrize(
        ("fmt", "expected"),
        [
            (PdfAFormat.A1b, {"pdfa": "PDF/A-1b"}),
            (PdfAFormat.A2b, {"pdfa": "PDF/A-2b"}),
            (PdfAFormat.A3b, {"pdfa": "PDF/A-3b"}),
        ],
    )
    def test_to_form(self, fmt: PdfAFormat, expected: dict[str, str]) -> None:
        assert fmt.to_form() == expected

    def test_a1a_returns_empty_dict(self) -> None:
        with pytest.warns(DeprecationWarning, match="PDF/A-1a is deprecated"):
            result = PdfAFormat.A1a.to_form()
        assert result == {}

    def test_a1a_emits_deprecation_warning_message(self) -> None:
        with pytest.warns(DeprecationWarning, match="PDF/A-1a is deprecated"):
            PdfAFormat.A1a.to_form()


class TestPageOrientation:
    @pytest.mark.parametrize(
        ("orientation", "expected"),
        [
            (PageOrientation.Landscape, {"landscape": "true"}),
            (PageOrientation.Portrait, {"landscape": "false"}),
        ],
    )
    def test_to_form(self, orientation: PageOrientation, expected: dict[str, str]) -> None:
        assert orientation.to_form() == expected
