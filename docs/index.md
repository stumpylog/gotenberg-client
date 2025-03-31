# Gotenberg Python Client

This is a Python client for interfacing with [Gotenberg](https://gotenberg.dev/), which
in turn is a wrapper around powerful tools for PDF generation and creation in various
ways, using a stateless API. It's a very powerful tool to generate and manipulate PDFs.

## Features

- HTTP/2 enabled by default
- Abstract away the handling of multi-part/form-data and deal with `Path`s instead
- Based on the modern [httpx](https://github.com/encode/httpx) library
- Full support for type hinting and concrete return types as much as possible
- Nearly full test coverage run against an actual Gotenberg server for multiple Python
  and PyPy versions

## Examples

Converting a single HTML file into a PDF:

```python
from gotenberg_client import GotenbergClient

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
      response = route.index("my-index.html").run()
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
    with client.chromium.html_to_pdf() as route:
      response = route.url("https://hello.world").orient(PageOrientation.Landscape).run()
      response.to_file(Path("my-world.pdf"))
```

To ensure the proper clean up of all used resources, both the client and the route(s)
should be used as context manager. If for some reason you cannot, you should `.close`
the client and any routes:

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

## API Responses

The response from any `.run()` or `.run_with_retry()` will be either a
`SingleFileResponse` or `ZipFileResponse`. There provide a slimmed down set of fields
from an `httpx.Response`, including the headers, the status code and the response
content. They also provide two convenience methods:

- `to_file` - Accepts a path and writes the content of the response to it
- `extract_to` - Only on a `ZipFileResponse`, extracts the zip into the given directory
  (which must exist)

Determining which response is a little complicated, as Gotenberg can produce a single
PDF from multiple files or a zip file containing multiple PDFs, depending on how the
route is configured and how many files were provided.

For example, the LibreOffice convert route may:

- Produce a single PDF when a single office document is provided
- Produce a zipped response when multiple office documents are provided
- Produce a single PDF when multiple office documents are provided AND the route is
  asked to merge the result
