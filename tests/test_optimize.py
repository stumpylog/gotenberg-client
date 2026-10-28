# SPDX-FileCopyrightText: 2025-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import random
import zlib
from pathlib import Path

import pikepdf
import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._common import ImageQualityMixin
from gotenberg_client._common import OptimizeImagesMixin
from gotenberg_client._others.routes import AsyncOptimizeRoute
from tests.utils import verify_basic_response_values_pdf
from tests.utils import verify_stream_contains


class _FormRecorder:
    def __init__(self) -> None:
        self._form_data: dict[str, str] = {}


class _ImageQuality(_FormRecorder, ImageQualityMixin):
    pass


class _OptimizeImages(_FormRecorder, OptimizeImagesMixin):
    pass


class TestOptimizeMixins:
    @pytest.mark.parametrize("quality", [0, -1, 101, 1000])
    def test_image_quality_out_of_range(self, quality: int):
        with pytest.raises(ValueError, match="between 1 and 100"):
            _ImageQuality().image_quality(quality)

    @pytest.mark.parametrize("quality", [1, 80, 100])
    def test_image_quality_in_range(self, quality: int):
        mixin = _ImageQuality()
        assert mixin.image_quality(quality) is mixin
        assert mixin._form_data == {"imageQuality": str(quality)}

    def test_optimize_images_defaults(self):
        mixin = _OptimizeImages()
        assert mixin.optimize_images() is mixin
        assert mixin._form_data == {"optimizeImages": "true"}

    def test_optimize_images_with_quality(self):
        mixin = _OptimizeImages()
        mixin.optimize_images(quality=40)
        assert mixin._form_data == {"optimizeImages": "true", "imageQuality": "40"}

    def test_optimize_images_invalid_quality_sets_nothing(self):
        mixin = _OptimizeImages()
        with pytest.raises(ValueError, match="between 1 and 100"):
            mixin.optimize_images(quality=0)
        assert mixin._form_data == {}


class TestOptimizeMocked:
    def test_optimize_route(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.optimize.optimize() as route:
            route.optimize(sample_directory / "sample1.pdf").image_quality(40).run()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/forms/pdfengines/optimize"
        verify_stream_contains(request, "imageQuality", "40")

    def test_optimize_route_files(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.optimize.optimize() as route:
            route.optimize_files([sample_directory / "sample1.pdf", sample_directory / "z_first_merge.pdf"]).run()
        request = httpx_mock.get_request()
        assert request is not None
        verify_stream_contains(request, "sample1.pdf", "sample1.pdf")
        verify_stream_contains(request, "z_first_merge.pdf", "z_first_merge.pdf")

    def test_html_to_pdf(self, mock_sync_client: GotenbergClient, sample_directory: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.html_to_pdf() as route:
            route.index(sample_directory / "basic.html").optimize_images(quality=60).run()
        request = httpx_mock.get_request()
        verify_stream_contains(request, "optimizeImages", "true")
        verify_stream_contains(request, "imageQuality", "60")

    def test_url_to_pdf(self, mock_sync_client: GotenbergClient, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.chromium.url_to_pdf() as route:
            route.url("https://example.com").optimize_images().run()
        request = httpx_mock.get_request()
        verify_stream_contains(request, "optimizeImages", "true")
        assert b'name="imageQuality"' not in request.content

    def test_libreoffice(self, mock_sync_client: GotenbergClient, docx_sample_file: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.libre_office.to_pdf() as route:
            route.convert(docx_sample_file).optimize_images(quality=70).run()
        request = httpx_mock.get_request()
        verify_stream_contains(request, "optimizeImages", "true")
        verify_stream_contains(request, "imageQuality", "70")

    def test_merge(self, mock_sync_client: GotenbergClient, sample_directory: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.merge.merge() as route:
            route.merge([sample_directory / "z_first_merge.pdf", sample_directory / "a_merge_second.pdf"])
            route.optimize_images(quality=50).run()
        request = httpx_mock.get_request()
        verify_stream_contains(request, "optimizeImages", "true")
        verify_stream_contains(request, "imageQuality", "50")

    def test_split(self, mock_sync_client: GotenbergClient, sample_directory: Path, httpx_mock: HTTPXMock):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.split.split() as route:
            route.split(sample_directory / "sample1.pdf").split_mode("pages").split_span("1").optimize_images(
                quality=30,
            ).run()
        request = httpx_mock.get_request()
        verify_stream_contains(request, "optimizeImages", "true")
        verify_stream_contains(request, "imageQuality", "30")


@pytest.fixture
def image_heavy_pdf(tmp_path: Path) -> Path:
    """
    A one page PDF with a single, losslessly (zlib) compressed image, which a JPEG re-encode shrinks a lot
    """
    rng = random.Random(1234)  # noqa: S311
    width = height = 400
    pdf = pikepdf.new()
    # The X1 name matches what Chromium emits, Gotenberg maps the extracted images back by that style of name
    # A gradient with noise on top: too noisy for zlib to shrink much, but easy for JPEG
    pixels = bytes((x + y + rng.randrange(16)) % 256 for y in range(height) for x in range(width) for _ in range(3))
    image = pikepdf.Stream(pdf, zlib.compress(pixels))
    image.Filter = pikepdf.Name.FlateDecode
    image.Type = pikepdf.Name.XObject
    image.Subtype = pikepdf.Name.Image
    image.Width = width
    image.Height = height
    image.ColorSpace = pikepdf.Name.DeviceRGB
    image.BitsPerComponent = 8
    page = pdf.add_blank_page(page_size=(width, height))
    page.Resources = pikepdf.Dictionary(XObject=pikepdf.Dictionary(X1=image))
    page.Contents = pdf.make_stream(f"q {width} 0 0 {height} 0 0 cm /X1 Do Q".encode())
    path = tmp_path / "image-heavy.pdf"
    pdf.save(path, compress_streams=True)
    return path


@pytest.mark.live
@pytest.mark.async_route
class TestOptimizeLive:
    async def test_optimize_shrinks_images(self, async_optimize_route: AsyncOptimizeRoute, image_heavy_pdf: Path):
        resp = await async_optimize_route.optimize(image_heavy_pdf).image_quality(40).run_with_retry()
        verify_basic_response_values_pdf(resp)
        assert len(resp.content) < image_heavy_pdf.stat().st_size / 2

    async def test_optimize_without_images(self, async_optimize_route: AsyncOptimizeRoute, pdf_sample_one_file: Path):
        verify_basic_response_values_pdf(await async_optimize_route.optimize(pdf_sample_one_file).run_with_retry())
