# Gotenberg API Client

A modern, fully-typed Python client for the [Gotenberg](https://gotenberg.dev/) PDF generation API, with sync and async support.

[![PyPI - Version](https://img.shields.io/pypi/v/gotenberg-client.svg)](https://pypi.org/project/gotenberg-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gotenberg-client.svg)](https://pypi.org/project/gotenberg-client)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/gotenberg-client)](https://pypi.org/project/gotenberg-client)
[![codecov](https://codecov.io/gh/stumpylog/gotenberg-client/graph/badge.svg?token=PH25G91Q6J)](https://codecov.io/gh/stumpylog/gotenberg-client)

---

## Quick Start

```console
pip install gotenberg-client
```

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        response = route.index(Path("my-index.html")).run()
        response.to_file(Path("my-index.pdf"))
```

Four lines (excluding imports) to convert HTML to PDF.

## Why gotenberg-client?

[Gotenberg](https://gotenberg.dev/) is a powerful, Docker-based API for PDF generation and manipulation using
Chromium and LibreOffice under the hood. This client gives you a clean, Pythonic interface to all of its
capabilities, so you can skip the multipart form-data boilerplate and focus on your documents.

### Features

- **Fully typed** with concrete return types and full `py.typed` support
- **Sync and async** APIs with identical interfaces
- **Pluggable HTTP backends** -- [httpx](https://github.com/encode/httpx) (default, with HTTP/2), [niquests](https://github.com/jawah/niquests), or [requests](https://github.com/psf/requests)
- **Pathlib-native** -- pass `Path` objects directly, no manual file handling
- **Thoroughly tested** against a real Gotenberg server across multiple Python versions
- **Broad route coverage** including Chromium, LibreOffice, PDF merge/convert/split, health checks, and more
    - If there's a route you need, just [ask](https://github.com/stumpylog/gotenberg-client/discussions/categories/ideas)!

## Installation

The default installation uses httpx:

```console
pip install gotenberg-client
```

To use an alternative HTTP backend:

```console
pip install "gotenberg-client[niquests]"
pip install "gotenberg-client[requests]"  # sync-only
```

## Examples

### HTML to PDF

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        response = route.index(Path("my-index.html")).run()
        response.to_file(Path("my-index.pdf"))
```

### Async support

```python
from gotenberg_client import AsyncGotenbergClient
from pathlib import Path

async with AsyncGotenbergClient("http://localhost:3000") as client:
    async with client.chromium.html_to_pdf() as route:
        response = await route.index(Path("my-index.html")).run()
        response.to_file(Path("my-index.pdf"))
```

### HTML with additional resources

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        response = (
            route.index(Path("my-index.html"))
            .resource("image.png")
            .resource("style.css")
            .run()
        )
        response.to_file(Path("my-index.pdf"))
```

### URL to PDF in landscape

```python
from gotenberg_client import GotenbergClient
from gotenberg_client.options import PageOrientation

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.url_to_pdf() as route:
        response = route.url("https://hello.world").orient(PageOrientation.Landscape).run()
        response.to_file(Path("my-world.pdf"))
```

### PDF/A output format

```python
from gotenberg_client import GotenbergClient
from gotenberg_client.options import PdfAFormat
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        response = (
            route.index(Path("my-index.html"))
            .resources(["image.png", "style.css"])
            .pdf_format(PdfAFormat.A2b)
            .run()
        )
        response.to_file(Path("my-index.pdf"))
```

### PDF metadata

```python
from gotenberg_client import GotenbergClient
from datetime import datetime

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        response = (
            route.index("my-index.html")
            .metadata(
                title="My Document",
                author="John Doe",
                subject="Example PDF",
                keywords=["sample", "document", "test"],
                creation_date=datetime.now(),
            )
            .run()
        )
        response.to_file(Path("my-index.pdf"))
```

### Choosing an HTTP backend

```python
from gotenberg_client import GotenbergClient

# httpx (default, includes HTTP/2)
with GotenbergClient("http://localhost:3000") as client:
    ...

# niquests
with GotenbergClient("http://localhost:3000", backend="niquests") as client:
    ...

# requests (sync-only)
with GotenbergClient("http://localhost:3000", backend="requests") as client:
    ...
```

### Basic authentication

```python
from gotenberg_client import GotenbergClient

with GotenbergClient("http://localhost:3000", auth=("user", "secret")) as client:
    with client.chromium.html_to_pdf() as route:
        response = route.index(Path("my-index.html")).run()
        response.to_file(Path("my-index.pdf"))
```

## How It Works

All routes follow the same pattern:

1. Add the file(s) you want to process
2. Configure options the route supports
3. Call `.run()` and receive your result

Responses are either a `SingleFileResponse` or `ZipFileResponse`, each providing:

- `to_file(path)` -- write the result to disk
- `extract_to(directory)` -- extract a ZIP result into a directory (ZipFileResponse only)
- Access to `headers`, `status_code`, and `content` from the underlying response

### Resource cleanup

Both the client and routes should be used as context managers for proper cleanup.
If that isn't possible, call `.close()` explicitly:

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

client = GotenbergClient("http://localhost:3000")
try:
    route = client.merge.merge()
    try:
        response = route.merge([Path("myfile.pdf"), Path("otherfile.pdf")]).run()
        response.to_file(Path("merged.pdf"))
    finally:
        route.close()
finally:
    client.close()
```

## Documentation

For the full API reference and more examples, see the [documentation](https://stumpylog.github.io/gotenberg-client/latest/).

## License

`gotenberg-client` is distributed under the terms of the [MPL 2.0](https://spdx.org/licenses/MPL-2.0.html) license.
