# Gotenberg API Client

[![PyPI - Version](https://img.shields.io/pypi/v/gotenberg-client.svg)](https://pypi.org/project/gotenberg-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gotenberg-client.svg)](https://pypi.org/project/gotenberg-client)
[![codecov](https://codecov.io/gh/stumpylog/gotenberg-client/graph/badge.svg?token=PH25G91Q6J)](https://codecov.io/gh/stumpylog/gotenberg-client)

---

## Table of Contents

- [Installation](#installation)
- [What](#what)
- [Why](#why)
    - [Features](#features)
- [How](#how)
    - [Examples](#examples)
- [License](#license)

## Installation

```console
pip install gotenberg-client
```

## What

This is a Python client for interfacing with [Gotenberg](https://gotenberg.dev/), which in turn is a wrapper around
powerful tools for PDF generation and creation in various ways, using a stateless API. It's a very powerful tool
to generate and manipulate PDFs.

## Why

As far as I can tell, no active Python library exists to interface with the Gotenberg API.

### Features

- HTTP/2 enabled by default
- Abstract away the handling of `multi-part/form-data` requests and deal with `Path`s instead
- Based on the modern [httpx](https://github.com/encode/httpx) library
- Full support for type hinting and concrete return types as much as possible
- Nearly full test coverage run against an actual Gotenberg server for multiple Python and PyPy versions
- Asynchronous support

## How

All the routes and options from the Gotenberg routes are implemented, with the exception of the Prometheus metrics
endpoint. All the routes use the same format and general idea.

1. First, you add the file or files you want to process
1. Then, configure the endpoint with its various options the route supports
1. Finally, run the route and receive your resulting file

- Files will be PDF or ZIP, depending on what endpoint and its configuration. Endpoints which handle
  multiple files, but don't merge them, return a ZIP archive of the resulting PDFs

For more detailed examples, check the [documentation](https://stumpylog.github.io/gotenberg-client/latest/)

### Examples

Converting a single HTML file into a PDF:

```python
from gotenberg_client import GotenbergClient, AsyncGotenbergClient

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
      response = route.index("my-index.html").run()
      response.to_file(Path("my-index.pdf"))

async with AsyncGotenbergClient("http://localhost:3000") as client:
    async with client.chromium.html_to_pdf() as route:
      response = await route.index("my-index.html").run()
      response.to_file(Path("my-index.pdf"))
```

Converting an HTML file with additional resources into a PDF:

```python
from gotenberg_client import GotenbergClient

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
      response = route.index("my-index.html").resource("image.png").resource("style.css").run()
      response.to_file(Path("my-index.pdf"))
```

Converting an HTML file with additional resources into a PDF/A1a format:

```python
from gotenberg_client import GotenbergClient
from gotenberg_client.options import PdfAFormat

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
      response = route.index("my-index.html").resources(["image.png", "style.css"]).pdf_format(PdfAFormat.A2b).run()
      response.to_file(Path("my-index.pdf"))
```

Converting a URL into PDF, in landscape format

```python
from gotenberg_client import GotenbergClient
from gotenberg_client.options import PageOrientation

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.url_to_pdf() as route:
      response = route.url("https://hello.world").orient(PageOrientation.Landscape).run()
      response.to_file(Path("my-world.pdf"))
```

Adding metadata to a PDF:

This example shows how to add metadata to your generated PDF. All metadata fields are optional and include:

- Document info (title, author, subject, keywords)
- Dates (creation, modification)
- Technical details (pdf version, creator, producer)
- PDF standards (trapped status, marked status)

```python
from gotenberg_client import GotenbergClient
from datetime import datetime

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        response = (route
            .index("my-index.html")
            .metadata(
                title="My Document",
                author="John Doe",
                subject="Example PDF",
                keywords=["sample", "document", "test"],
                creation_date=datetime.now(),
                trapped="Unknown"
            )
            .run())
        response.to_file(Path("my-index.pdf"))
```

To ensure the proper clean up of all used resources, both the client and the route(s) should be
used as context manager. If for some reason you cannot, you should `.close` the client and any
routes:

```python
from gotenberg_client import GotenbergClient

try:
  client = GotenbergClient("http://localhost:3000")
  try:
    route = client.merge(["myfile.pdf", "otherfile.pdf"]).run()
  finally:
    route.close()
finally:
  client.close()
```

The response from any `.run()` or `.run_with_retry()` will be either a `SingleFileResponse` or `ZipFileResponse`.
There provide a slimmed down set of fields from an `httpx.Response`, including the headers, the status code and
the response content. They also provide two convenience methods:

- `to_file` - Accepts a path and writes the content of the response to it
- `extract_to` - Only on a `ZipFileResponse`, extracts the zip into the given directory (which must exist)

## License

`gotenberg-client` is distributed under the terms of the [MPL 2.0](https://spdx.org/licenses/MPL-2.0.html) license.
