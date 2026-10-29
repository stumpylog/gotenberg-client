# Usage

## Installation

An HTTP backend is required. Pick the one that suits your project:

```console
pip install "gotenberg-client[httpx]"      # recommended — HTTP/2 and async support
pip install "gotenberg-client[httpx2]"     # alternative — HTTP/2 and async support
pip install "gotenberg-client[niquests]"   # alternative — HTTP/2 and async support
pip install "gotenberg-client[requests]"   # sync-only
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
        user_agent: str = "gotenberg-client/<version>",
        auth: AuthType = None,
        *,
        timeout: float = 30.0,
        log_level: int = logging.ERROR,
        http2: bool = True,
        backend: BackendType = "auto",
    ):
        ....
```

The `backend` parameter selects the HTTP library used to communicate with Gotenberg:

| Value              | Behaviour                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `"auto"` (default) | Use httpx if installed, then niquests, then httpx2                                       |
| `"httpx"`          | Always use httpx (install with `pip install "gotenberg-client[httpx]"`)                  |
| `"httpx2"`         | Always use httpx2 (install with `pip install "gotenberg-client[httpx2]"`)                |
| `"niquests"`       | Always use niquests (install with `pip install "gotenberg-client[niquests]"`)            |
| `"requests"`       | Always use requests (sync-only; install with `pip install "gotenberg-client[requests]"`) |

## Authentication

The `auth` parameter accepts a `(username, password)` tuple for HTTP Basic Authentication
with every backend. Omit it or pass `None` to use the backend's default authentication
behavior:

```python
with GotenbergClient("http://localhost:3000", auth=("user", "secret")) as client:
    ...
```

You can also pass an instance of your selected backend's native authentication base
class. The client validates its type before constructing the backend client and passes
matching authentication through unchanged:

| Backend                           | Native authentication                                                                           | Client support                                            |
| --------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `"httpx"`                         | `httpx.Auth`, including `BasicAuth`, `DigestAuth`, and custom subclasses                        | Sync and async; custom flows must support the chosen mode |
| `"httpx2"`                        | `httpx2.Auth` and subclasses                                                                    | Sync and async; custom flows must support the chosen mode |
| `"requests"`                      | `requests.auth.AuthBase` and subclasses                                                         | Sync only                                                 |
| `"niquests"`                      | `niquests.auth.AuthBase` and subclasses                                                         | Sync and async                                            |
| `"niquests"` with an async client | `niquests.auth.AsyncAuthBase` and subclasses, where supported by the installed Niquests version | Async only                                                |

Always set `backend=` explicitly when using native authentication. Native auth objects
belong to their backend; they are not interchangeable between backends. A mismatched
object raises a `TypeError` identifying the backend and expected authentication types.
Malformed username/password tuples and other unsupported values also raise `TypeError`.
`backend="auto"` selects an installed backend without considering your authentication object.

For custom authentication, subclass the selected backend's auth base class. Bare callables
are not accepted. See the [Niquests authentication API](https://niquests.readthedocs.io/en/latest/api.html#authentication)
and [Requests custom authentication guide](https://requests.readthedocs.io/en/latest/user/advanced/#custom-authentication).

```python
import httpx

from gotenberg_client import AsyncGotenbergClient, SyncGotenbergClient

auth = httpx.DigestAuth("user", "secret")  # Or your own httpx.Auth subclass

with SyncGotenbergClient("https://gotenberg.example", backend="httpx", auth=auth) as client:
    ...

async with AsyncGotenbergClient("https://gotenberg.example", backend="httpx", auth=auth) as client:
    ...
```

For multipart request signing with a custom `httpx.Auth`, set
`requires_request_body = True` on the auth class. HTTPX then buffers the complete encoded
multipart body before calling `auth_flow()`, making it available as `request.content` in
both sync and async clients. This includes form fields, uploaded files, and multipart
boundaries. The body is sent intact after authentication. For custom `sync_auth_flow()`
or `async_auth_flow()` overrides, manage body reads with `request.read()` or
`await request.aread()` as needed. See [HTTPX custom authentication](https://www.python-httpx.org/advanced/authentication/#custom-authentication-schemes).
Body buffering uses memory proportional to the encoded upload size. Requests and Niquests
prepare multipart uploads before invoking authentication, exposing the encoded body as
`PreparedRequest.body`.

The public `AuthType` alias is a union of `(username, password)` tuples, `None`, and
the native auth base classes listed above. Forward references and type-checking-only
imports keep optional backends out of runtime imports. Runtime validation rejects
foreign-backend auth and Niquests async auth used with a synchronous client.

## Client lifetime

The client should live as long as you will be communicating with Gotenberg as this
allows the connection to remain open, saving some time to re-negotiate a connection.

To ensure proper cleanup of connection, it is suggested to use the client as a context
manager. If not using as a context manager, the user should call `.close()`, preferably
inside a `finally` block.

## Routes

The library supports all the [routes](https://gotenberg.dev/docs/routes) defined
by the Gotenberg API, with the exception of the Prometheus metrics endpoint.

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

## Webhooks

Gotenberg supports [webhooks](https://gotenberg.dev/docs/webhook) — instead of waiting for the response, Gotenberg
POSTs the result to a URL you provide. Configure webhooks on the client before making requests:

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    client.add_webhook_url("https://my-service.example.com/webhook/result")
    client.add_error_webhook_url("https://my-service.example.com/webhook/error")
    client.set_webhook_http_method("POST")  # "POST", "PATCH", or "PUT"
    client.set_webhook_extra_headers({"Authorization": "Bearer my-token"})

    with client.chromium.html_to_pdf() as route:
        route.index(Path("index.html")).run()
        # Gotenberg processes the request asynchronously and POSTs to the webhook URL
```

Webhook configuration methods on the client:

| Method                                  | Description                                                          |
| --------------------------------------- | -------------------------------------------------------------------- |
| `add_webhook_url(url)`                  | URL Gotenberg will POST the result to                                |
| `add_error_webhook_url(url)`            | URL Gotenberg will POST errors to                                    |
| `set_webhook_http_method(method)`       | HTTP method for the result webhook (`"POST"`, `"PATCH"`, or `"PUT"`) |
| `set_error_webhook_http_method(method)` | HTTP method for the error webhook                                    |
| `set_webhook_extra_headers(headers)`    | Additional headers to include in webhook requests (e.g. auth)        |

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
which raises `MaxRetriesExceededError` after all attempts are exhausted:

```python
from gotenberg_client import GotenbergClient, MaxRetriesExceededError

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        try:
            resp = route.index(Path("index.html")).run_with_retry(
                max_retry_count=5,  # number of attempts (default: 5)
                initial_retry_wait=5.0,  # seconds before first retry (default: 5.0)
                retry_scale=2.0,  # multiplier applied after each attempt (default: 2.0)
            )
        except MaxRetriesExceededError as e:
            print(f"Gave up after retries, last status: {e.response.status_code}")
```

The default retry pattern waits 5 s, 10 s, 20 s, 40 s, then 80 s between attempts.
Only 5xx server errors trigger retries; 4xx client errors raise `HttpStatusError` immediately.
