from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from gotenberg_client import GotenbergClient
from gotenberg_client._others.routes import AsyncSplitRoute
from tests.utils import verify_stream_contains


@pytest.mark.live
@pytest.mark.async_route
class TestSplitApi:
    async def test_split_pdf(self, async_split_route: AsyncSplitRoute, pdf_sample_one_file: Path):
        await (
            async_split_route.split_files([pdf_sample_one_file]).split_mode("pages").split_span("1,3").run_with_retry()
        )


class TestSplitMocked:
    def test_split_user_password(
        self,
        mock_sync_client: GotenbergClient,
        sample_directory: Path,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(method="POST")
        with mock_sync_client.split.split() as route:
            route.split(sample_directory / "sample1.pdf").split_mode("pages").split_span("1").user_password("pw").run()
        verify_stream_contains(httpx_mock.get_request(), "userPassword", "pw")
