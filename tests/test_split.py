from pathlib import Path

from gotenberg_client._others.routes import AsyncSplitRoute


class TestSplitApi:
    async def test_split_pdf(self, async_split_route: AsyncSplitRoute, pdf_sample_one_file: Path):
        await (
            async_split_route.split_files([pdf_sample_one_file]).split_mode("pages").split_span("1,3").run_with_retry()
        )
