# Usage

## Installation

```console
pip install gotenberg-client
```

## How

All the routes and options from the Gotenberg routes are implemented, with the exception of the Prometheus metrics
endpoint. All the routes use the same format and general idea.

1. First, you add the file or files you want to process
1. Then, configure the endpoint with its various options the route supports
1. Finally, run the route and receive your resulting file

- Files will be PDF or ZIP, depending on what endpoint and its configuration. Endpoints which handle
  multiple files, but don't merge them, return a ZIP archive of the resulting PDFs

## Client

First, you obtain a `GotenbergClient`. As seen below, the host
where Gotenberg can be found is required, with optional configuration of
global timeouts, the log level (for this library and httpx/httpcore) as
well as control over the usage of HTTP/2.

```python
class GotenbergClient:

    def __init__(
        self,
        host: str,
        *,
        timeout: float = 30.0,
        log_level: int = logging.ERROR,
        http2: bool = True,
    ):
        ....
```

The client should live as long as you will be communicating with Gotenberg as
this allows the connection to remain open, saving some time to re-negotiate
a connection.

To ensure proper cleanup of connection, it is suggested to use the client as
a context manager. If not using as a context manager, the user should call
`.close()`, preferably inside a `finally` block.

## Routes

The library supports almost all the [routes](https://gotenberg.dev/docs/routes)
defined by the Gotenberg API. Only the Prometheus metrics endpoint is not
implemented.

To utilize a route, you first select the module which provides it, then the
actual operation to carry out. For example, using Chromium to convert
HTML into a PDF would look like this:

```python
with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        ....
```

The exact options of each route vary, according to the Gotenberg documentation. Many routes
share some common options, such as controlling page size or setting the PDF/A format output.

Configuration of a route will always return the the route, allowing chaining of configuration,
as seen here:

```python
from gotenberg_client import GotenbergClient
from gotenberg_client.options import A4

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.markdown_to_pdf() as route:
        response = (
            route.index("main.html")
            .markdown_file("readme.md")
            .size(A4)
            .resource("styles.css")
            .fail_on_exceptions()
            .run()
        )
```

Once all configuration is completed, call `.run()`. This actually sends the information to
Gotenberg with all form data as has been configured. At the moment, it returns the full
[`httpx.Response`](https://www.python-httpx.org/api/#response), with the content of the response
being the resulting PDF or zip file, depending on the route and configurations.
