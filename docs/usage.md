# Usage

## Installation

```console
pip install gotenberg-client
```

To use the [niquests](https://niquests.readthedocs.io/) HTTP backend instead of the default httpx:

```console
pip install "gotenberg-client[niquests]"
```

## How

All the routes and options from the Gotenberg routes are implemented, with the exception
of the Prometheus metrics endpoint. All the routes use the same format and general idea.

1. First, you add the file or files you want to process
1. Then, configure the endpoint with its various options the route supports
1. Finally, run the route and receive your resulting file

- Files will be PDF or ZIP, depending on what endpoint and its configuration. Endpoints
  which handle multiple files, but don't merge them, return a ZIP archive of the
  resulting PDFs

## Client

First, you obtain a `GotenbergClient`. As seen below, the host where Gotenberg can be
found is required, with optional configuration of global timeouts, the log level (for
this library and the underlying HTTP library) as well as control over the HTTP backend
and HTTP/2 usage.

```python
class GotenbergClient:

    def __init__(
        self,
        host: str,
        *,
        timeout: float = 30.0,
        log_level: int = logging.ERROR,
        http2: bool = True,
        backend: BackendType = "auto",
    ):
        ....
```

The `backend` parameter selects the HTTP library used to communicate with Gotenberg:

| Value              | Behaviour                                                                     |
| ------------------ | ----------------------------------------------------------------------------- |
| `"auto"` (default) | Use httpx if installed, otherwise fall back to niquests                       |
| `"httpx"`          | Always use httpx (included by default)                                        |
| `"niquests"`       | Always use niquests (install with `pip install "gotenberg-client[niquests]"`) |

## Authentication

The `auth` parameter accepts either a `(username, password)` tuple or an `httpx.BasicAuth`
instance for HTTP Basic Authentication:

```python
# Tuple form — works with all backends
with GotenbergClient("http://localhost:3000", auth=("user", "secret")) as client:
    ...

# httpx.BasicAuth — works only with the httpx backend
import httpx
with GotenbergClient("http://localhost:3000", auth=httpx.BasicAuth("user", "secret")) as client:
    ...
```

!!! note
`httpx.BasicAuth` does not expose its credentials publicly, so it cannot be converted
for use with the niquests backend. If you use `backend="niquests"` (or `backend="auto"`
resolves to niquests), you must pass auth as a `(username, password)` tuple.
Passing `httpx.BasicAuth` with the niquests backend raises `ValueError` at client creation.

The client should live as long as you will be communicating with Gotenberg as this
allows the connection to remain open, saving some time to re-negotiate a connection.

To ensure proper cleanup of connection, it is suggested to use the client as a context
manager. If not using as a context manager, the user should call `.close()`, preferably
inside a `finally` block.

## Routes

The library supports almost all the [routes](https://gotenberg.dev/docs/routes) defined
by the Gotenberg API. Only the Prometheus metrics endpoint is not implemented.

To utilize a route, you first select the module which provides it, then the actual
operation to carry out. For example, using Chromium to convert HTML into a PDF would
look like this:

```python
with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        ....
```

The exact options of each route vary, according to the Gotenberg documentation. Many
routes share some common options, such as controlling page size or setting the PDF/A
format output.

Configuration of a route will always return the the route, allowing chaining of
configuration, as seen here:

```python
from gotenberg_client import GotenbergClient
from gotenberg_client.constants import A4

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

Once all configuration is completed, call `.run()`. This sends the request to Gotenberg
with all configured files and form data. It returns a `SingleFileResponse` (for a single
PDF or image) or a `ZipFileResponse` (when multiple output files are produced), depending
on the route and its configuration.

For more details, see the [routes](routes.md) page for a detailed breakdown of the
implemented routes, and the linkage to the Gotenberg route documentation.

## Error handling

HTTP errors (non-2xx responses) raise `HttpStatusError`, which is exported from
`gotenberg_client` and is independent of the selected HTTP backend:

```python
from gotenberg_client import GotenbergClient, HttpStatusError

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        try:
            resp = route.index("index.html").run()
        except HttpStatusError as e:
            print(f"Gotenberg returned {e.response.status_code}")
```

If you were previously catching `httpx.HTTPStatusError`, update to `HttpStatusError`
when upgrading to this version.

Transient server errors (5xx) can be retried automatically using `.run_with_retry()`,
which raises `MaxRetriesExceededError` after all attempts are exhausted.
