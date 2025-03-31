from pathlib import Path

from gotenberg_client._others.routes import AsyncFlattenRoute
from tests.utils import verify_basic_response_values_pdf


class TestFlattenApi:
    async def test_flatten_pdf(self, async_flatten_route: AsyncFlattenRoute, pdf_sample_one_file: Path):
        verify_basic_response_values_pdf(
            await async_flatten_route.flatten_files([pdf_sample_one_file]).run_with_retry(),
        )
