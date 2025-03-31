# SPDX-FileCopyrightText: 2023-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
import logging
import os
import shutil
from collections.abc import AsyncGenerator
from collections.abc import Generator
from pathlib import Path
from typing import Union

import httpx
import pytest

from gotenberg_client import AsyncGotenbergClient
from gotenberg_client import SingleFileResponse
from gotenberg_client import SyncGotenbergClient
from gotenberg_client import ZipFileResponse
from gotenberg_client._chromium.routes import AsyncHtmlToPdfRoute
from gotenberg_client._chromium.routes import AsyncMarkdownToPdfRoute
from gotenberg_client._chromium.routes import AsyncScreenshotFromHtmlRoute
from gotenberg_client._chromium.routes import AsyncScreenshotFromMarkdownRoute
from gotenberg_client._chromium.routes import AsyncScreenshotFromUrlRoute
from gotenberg_client._chromium.routes import AsyncUrlToPdfRoute
from gotenberg_client._chromium.routes import SyncHtmlToPdfRoute
from gotenberg_client._chromium.routes import SyncMarkdownToPdfRoute
from gotenberg_client._chromium.routes import SyncScreenshotFromHtmlRoute
from gotenberg_client._chromium.routes import SyncScreenshotFromMarkdownRoute
from gotenberg_client._chromium.routes import SyncScreenshotFromUrlRoute
from gotenberg_client._chromium.routes import SyncUrlToPdfRoute
from gotenberg_client._health import AsyncHealthCheckApi
from gotenberg_client._health import SyncHealthCheckApi
from gotenberg_client._libreoffice.routes import AsyncOfficeDocumentToPdfRoute
from gotenberg_client._libreoffice.routes import SyncOfficeDocumentToPdfRoute
from gotenberg_client._merge.routes import AsyncMergePdfsRoute
from gotenberg_client._merge.routes import SyncMergePdfsRoute
from gotenberg_client._others.routes import AsyncFlattenRoute
from gotenberg_client._others.routes import AsyncSplitRoute
from gotenberg_client._others.routes import SyncFlattenRoute
from gotenberg_client._others.routes import SyncSplitRoute
from gotenberg_client._pdfa_ua.routes import AsyncConvertToArchiveFormatRoute
from gotenberg_client._pdfa_ua.routes import SyncConvertToArchiveFormatRoute
from gotenberg_client._pdfmetadata.routes import AsyncReadPdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import AsyncWritePdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import SyncReadPdfMetadataRoute
from gotenberg_client._pdfmetadata.routes import SyncWritePdfMetadataRoute

logger = logging.getLogger("gotenberg-client.tests")


def is_responsive(url):
    try:
        response = httpx.get(url)
    except httpx.HTTPError:
        logger.exception("Error connecting to service")
        return False
    else:
        return response.status_code == httpx.codes.OK


@pytest.fixture(scope="session")
def docker_compose_file() -> Path:
    if "GOTENBERG_CLIENT_EDGE_TEST" in os.environ:
        return Path(__file__).parent / "docker" / "docker-compose.ci-test-edge.yml"
    else:
        return Path(__file__).parent / "docker" / "docker-compose.ci-test.yml"


@pytest.fixture(scope="session")
def gotenberg_service_name() -> str:
    if "GOTENBERG_CLIENT_EDGE_TEST" in os.environ:
        return "gotenberg-client-test-edge-server"
    else:
        return "gotenberg-client-test-server"


@pytest.fixture(scope="session")
def webserver_service_name() -> str:
    if "GOTENBERG_CLIENT_EDGE_TEST" in os.environ:
        return "nginx-webserver-edge"
    else:
        return "nginx-webserver"


@pytest.fixture(scope="session")
def webserver_docker_internal_url(webserver_service_name: str) -> str:
    """
    The URL by which Gotenberg can access the webserver
    """
    return f"http://{webserver_service_name}"


@pytest.fixture(scope="session")
def gotenberg_host(docker_services, docker_ip: str, gotenberg_service_name: str) -> str:
    """
    Fixture to set up and return the URL for the Gotenberg service running in a Docker container.

    Args:
        docker_services: Docker services management object
        docker_ip (str): IP address of the Docker host
        gotenberg_service_name (str): Name of the Gotenberg service in Docker

    Returns:
        str: Full URL of the Gotenberg service, including host and port
    """
    url = f"http://{docker_ip}:{docker_services.port_for(gotenberg_service_name, 3000)}"
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=1,
        check=lambda: is_responsive(f"{url}/version"),
    )
    return url


@pytest.fixture(scope="session")
def web_server_host(docker_services, docker_ip: str, webserver_service_name: str) -> str:
    """
    Fixture to set up and return the URL for the web server running in a Docker container.

    Args:
        docker_services: Docker services management object
        docker_ip (str): IP address of the Docker host
        webserver_service_name (str): Name of the web server service in Docker

    Returns:
        str: Full URL of the web server, including host and port
    """
    url = f"http://{docker_ip}:{docker_services.port_for(webserver_service_name, 80)}"
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=1,
        check=lambda: is_responsive(url),
    )
    return url


@pytest.fixture(scope="session")
def sample_directory() -> Path:
    """
    Fixture to provide the directory path containing sample test files.

    Returns:
        Path: Path to the directory containing sample files for testing
    """
    return Path(__file__).parent.resolve() / "samples"


@pytest.fixture(scope="session")
def basic_html_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to a basic HTML sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the basic HTML sample file
    """
    return sample_directory / "basic.html"


@pytest.fixture(scope="session")
def footer_html_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to an HTML footer sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the footer HTML sample file
    """
    return sample_directory / "footer.html"


@pytest.fixture(scope="session")
def complex_html_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to a complex HTML sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the complex HTML sample file
    """
    return sample_directory / "complex.html"


@pytest.fixture(scope="session")
def header_html_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to an HTML header sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the header HTML sample file
    """
    return sample_directory / "header.html"


@pytest.fixture(scope="session")
def img_gif_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to a GIF image sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the GIF image sample file
    """
    return sample_directory / "img.gif"


@pytest.fixture(scope="session")
def font_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to a font sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the font (WOFF) sample file
    """
    return sample_directory / "font.woff"


@pytest.fixture(scope="session")
def css_style_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to a CSS style sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the CSS style sample file
    """
    return sample_directory / "style.css"


@pytest.fixture(scope="session")
def markdown_index_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to a Markdown index sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the Markdown index sample file
    """
    return sample_directory / "markdown_index.html"


@pytest.fixture(scope="session")
def markdown_sample_one_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to the first Markdown sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the first Markdown sample file
    """
    return sample_directory / "markdown1.md"


@pytest.fixture(scope="session")
def markdown_sample_two_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to the second Markdown sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the second Markdown sample file
    """
    return sample_directory / "markdown2.md"


@pytest.fixture(scope="session")
def docx_sample_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to a DOCX sample file.

    Returns:
        Path: Path to the DOCX sample file
    """
    return sample_directory / "sample.docx"


@pytest.fixture(scope="session")
def odt_sample_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to an ODT sample file.

    Returns:
        Path: Path to the ODT sample file
    """
    return sample_directory / "sample.odt"


@pytest.fixture(scope="session")
def odt_sample_file_with_password(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to an ODT sample file.


    Returns:
        Path: Path to the ODT sample file with a password of password
    """
    return sample_directory / "sample-password.odt"


@pytest.fixture(scope="session")
def odt_sample_file_with_images(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to an ODT sample file.


    Returns:
        Path: Path to the ODT sample file with a password of password
    """
    return sample_directory / "sample-with-images.odt"


@pytest.fixture(scope="session")
def xlsx_sample_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to an XLSX sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the XLSX sample file
    """
    return sample_directory / "sample.xlsx"


@pytest.fixture(scope="session")
def ods_sample_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to an ODS sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the ODS sample file
    """
    return sample_directory / "sample.ods"


@pytest.fixture(scope="session")
def pdf_sample_one_file(sample_directory: Path) -> Path:
    """
    Fixture to provide the path to the first PDF sample file.

    Args:
        sample_directory (Path): Directory containing sample files

    Returns:
        Path: Path to the first PDF sample file
    """
    return sample_directory / "sample1.pdf"


@pytest.fixture(scope="session")
def output_file_save_directory() -> Path:
    """
    Fixture to provide the directory path for saving output files during testing.

    Returns:
        Path: Path to the directory where output files will be saved
    """
    return Path(__file__).parent.resolve() / "outputs"


@pytest.fixture(scope="session")
def save_output_files(output_file_save_directory: Path) -> bool:
    val = True
    if val:
        shutil.rmtree(output_file_save_directory, ignore_errors=True)
        output_file_save_directory.mkdir()
    return val


@pytest.fixture
def output_saver_factory(request, save_output_files: bool, output_file_save_directory: Path):  # noqa: FBT001
    def _save_the_item(response: Union[SingleFileResponse, ZipFileResponse], extra: str = ""):  # noqa: ARG001
        if save_output_files:
            extension_mapping = {
                "application/zip": ".zip",
                "application/pdf": ".pdf",
                "image/png": ".png",
            }
            extension = extension_mapping[response.headers["Content-Type"]]
            response.to_file(output_file_save_directory / f"{request.node.originalname}{extension}")

    return _save_the_item


# TODO: @pytest_asyncio.fixture(loop_scope="session", scope="session") so the client lives for the session
@pytest.fixture
def sync_client(gotenberg_host: str) -> Generator[SyncGotenbergClient, None, None]:
    with SyncGotenbergClient(host=gotenberg_host, log_level=logging.INFO) as client:
        yield client


@pytest.fixture
async def async_client(gotenberg_host: str) -> AsyncGenerator[AsyncGotenbergClient, None]:
    async with AsyncGotenbergClient(host=gotenberg_host, log_level=logging.INFO) as client:
        yield client


@pytest.fixture
def sync_html_to_pdf_route(sync_client: SyncGotenbergClient) -> Generator[SyncHtmlToPdfRoute, None, None]:
    with sync_client.chromium.html_to_pdf() as route:
        yield route


@pytest.fixture
async def async_html_to_pdf_route(async_client: AsyncGotenbergClient) -> AsyncGenerator[AsyncHtmlToPdfRoute, None]:
    async with async_client.chromium.html_to_pdf() as route:
        yield route


@pytest.fixture
def sync_url_to_pdf_route(sync_client: SyncGotenbergClient) -> Generator[SyncUrlToPdfRoute, None, None]:
    with sync_client.chromium.url_to_pdf() as route:
        yield route


@pytest.fixture
async def async_url_to_pdf_route(async_client: AsyncGotenbergClient) -> AsyncGenerator[AsyncUrlToPdfRoute, None]:
    async with async_client.chromium.url_to_pdf() as route:
        yield route


@pytest.fixture
def sync_markdown_to_pdf_route(sync_client: SyncGotenbergClient) -> Generator[SyncMarkdownToPdfRoute, None, None]:
    with sync_client.chromium.markdown_to_pdf() as route:
        yield route


@pytest.fixture
async def async_markdown_to_pdf_route(
    async_client: AsyncGotenbergClient,
) -> AsyncGenerator[AsyncMarkdownToPdfRoute, None]:
    async with async_client.chromium.markdown_to_pdf() as route:
        yield route


@pytest.fixture
def sync_office_to_pdf_route(sync_client: SyncGotenbergClient) -> Generator[SyncOfficeDocumentToPdfRoute, None, None]:
    with sync_client.libre_office.to_pdf() as route:
        yield route


@pytest.fixture
async def async_office_to_pdf_route(
    async_client: AsyncGotenbergClient,
) -> AsyncGenerator[AsyncOfficeDocumentToPdfRoute, None]:
    async with async_client.libre_office.to_pdf() as route:
        yield route


@pytest.fixture
def sync_merge_pdfs_route(sync_client: SyncGotenbergClient) -> Generator[SyncMergePdfsRoute, None, None]:
    with sync_client.merge.merge() as route:
        yield route


@pytest.fixture
async def async_merge_pdfs_route(async_client: AsyncGotenbergClient) -> AsyncGenerator[AsyncMergePdfsRoute, None]:
    async with async_client.merge.merge() as route:
        yield route


@pytest.fixture
def sync_convert_pdfs_route(sync_client: SyncGotenbergClient) -> Generator[SyncConvertToArchiveFormatRoute, None, None]:
    with sync_client.pdf_convert.to_pdfa() as route:
        yield route


@pytest.fixture
async def async_convert_pdfs_route(
    async_client: AsyncGotenbergClient,
) -> AsyncGenerator[AsyncConvertToArchiveFormatRoute, None]:
    async with async_client.pdf_convert.to_pdfa() as route:
        yield route


@pytest.fixture
def sync_health_api(sync_client: SyncGotenbergClient) -> Generator[SyncHealthCheckApi, None, None]:
    with sync_client.health as api:
        yield api


@pytest.fixture
async def async_health_api(async_client: AsyncGotenbergClient) -> AsyncGenerator[AsyncHealthCheckApi, None]:
    async with async_client.health as api:
        yield api


@pytest.fixture
def sync_screenshot_url_route(sync_client: SyncGotenbergClient) -> Generator[SyncScreenshotFromUrlRoute, None, None]:
    with sync_client.chromium.screenshot_url() as route:
        yield route


@pytest.fixture
async def async_screenshot_url_route(
    async_client: AsyncGotenbergClient,
) -> AsyncGenerator[AsyncScreenshotFromUrlRoute, None]:
    async with async_client.chromium.screenshot_url() as route:
        yield route


@pytest.fixture
def sync_screenshot_html_route(sync_client: SyncGotenbergClient) -> Generator[SyncScreenshotFromHtmlRoute, None, None]:
    with sync_client.chromium.screenshot_html() as route:
        yield route


@pytest.fixture
async def async_screenshot_html_route(
    async_client: AsyncGotenbergClient,
) -> AsyncGenerator[AsyncScreenshotFromHtmlRoute, None]:
    async with async_client.chromium.screenshot_html() as route:
        yield route


@pytest.fixture
def sync_screenshot_markdown_route(
    sync_client: SyncGotenbergClient,
) -> Generator[SyncScreenshotFromMarkdownRoute, None, None]:
    with sync_client.chromium.screenshot_markdown() as route:
        yield route


@pytest.fixture
async def async_screenshot_markdown_route(
    async_client: AsyncGotenbergClient,
) -> AsyncGenerator[AsyncScreenshotFromMarkdownRoute, None]:
    async with async_client.chromium.screenshot_markdown() as route:
        yield route


@pytest.fixture
def sync_read_pdf_metadata_route(sync_client: SyncGotenbergClient) -> Generator[SyncReadPdfMetadataRoute, None, None]:
    with sync_client.metadata.read() as route:
        yield route


@pytest.fixture
async def async_read_pdf_metadata_route(
    async_client: AsyncGotenbergClient,
) -> AsyncGenerator[AsyncReadPdfMetadataRoute, None]:
    async with async_client.metadata.read() as route:
        yield route


@pytest.fixture
def sync_write_pdf_metadata_route(sync_client: SyncGotenbergClient) -> Generator[SyncWritePdfMetadataRoute, None, None]:
    with sync_client.metadata.write() as route:
        yield route


@pytest.fixture
async def async_write_pdf_metadata_route(
    async_client: AsyncGotenbergClient,
) -> AsyncGenerator[AsyncWritePdfMetadataRoute, None]:
    async with async_client.metadata.write() as route:
        yield route


@pytest.fixture
def sync_flatten_route(sync_client: SyncGotenbergClient) -> Generator[SyncFlattenRoute, None, None]:
    with sync_client.flatten.flatten() as route:
        yield route


@pytest.fixture
async def async_flatten_route(async_client: AsyncGotenbergClient) -> AsyncGenerator[AsyncFlattenRoute, None]:
    async with async_client.flatten.flatten() as route:
        yield route


@pytest.fixture
def sync_split_route(sync_client: SyncGotenbergClient) -> Generator[SyncSplitRoute, None, None]:
    with sync_client.split.split() as route:
        yield route


@pytest.fixture
async def async_split_route(async_client: AsyncGotenbergClient) -> AsyncGenerator[AsyncSplitRoute, None]:
    async with async_client.split.split() as route:
        yield route
