# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

`AGENTS.md` is a symlink to this file.

## Overview

`gotenberg-client` is a fully-typed Python client for the [Gotenberg](https://gotenberg.dev/)
PDF generation API. It provides identical **sync and async** interfaces over a **pluggable HTTP
backend** (httpx, niquests, or requests), exposing Gotenberg's Chromium, LibreOffice, and PDF
manipulation routes through a fluent builder API.

## Commands

The project uses [`hatch`](https://hatch.pypa.io/) for environment management, testing, and tooling.
[`uv`](https://astral.sh/uv/) is the configured installer.

- Run the full test suite: `hatch test`
- Run with coverage: `hatch test --cover`
- Run a single test file: `hatch test tests/test_merge.py`
- Run a single test: `hatch test tests/test_merge.py::test_name` (or `-k <pattern>`)
- Run against one Python version: `hatch test --python 3.12`
- Format & lint (autofix): `hatch fmt`
- Check formatting/lint only: `hatch fmt --check`
- Type check: `hatch run typing:run` (mypy in strict mode against `src/gotenberg_client`)
- All pre-commit hooks: `hatch run prek:check`
- Build docs: `hatch run docs:build` / serve: `hatch run docs:serve`

CI runs `hatch fmt --check`, `hatch run typing:run`, prek hooks, and the test matrix across
Python 3.10-3.14 (plus PyPy) before a merge is allowed.

### Testing structure

Tests fall into three tiers. **Pick the lightest tier that proves what you need** — do not reach for
the live Docker stack to verify something that is really just request construction.

1. **Pure unit tests** — no client, no network, no Docker. They exercise `options.py` dataclasses/enums
   and other pure logic directly (e.g. `Measurement(...).to_form(...)`). See `tests/test_options.py`.
   This is the right tier for anything that can be checked by calling a function and asserting its
   return value.
2. **Mocked request-construction tests** — verify that a route builds the correct multipart form data
   and headers, _without_ performing a real conversion. They intercept the outgoing POST with the
   `httpx_mock` fixture (from `pytest-httpx`), then assert on the captured request with
   `verify_stream_contains` (see `tests/utils.py`). Conventionally grouped in a `Test*Mocked` class with
   **no** `@pytest.mark.live`. Use this tier for new option-setting mixin methods: add the option, mock
   the response, assert the field/header is present. `pytest-httpx` only intercepts the **httpx**
   backend, so mocked tests run against httpx.
3. **Live integration tests** — marked `@pytest.mark.live`, they hit a real Gotenberg server and verify
   the produced PDF/image with `pikepdf`/`pypdf`. Use only when you genuinely need a real conversion
   (output correctness, PDF/A status, page counts, screenshots, server-side retry behavior).

**Pick the right client fixture — this controls whether Docker starts.** `pytest-docker` only spins up
the Gotenberg + nginx stack when a test (transitively) requests the `gotenberg_host` / `web_server_host`
fixtures. So fixture choice decides whether a test needs Docker:

- **No-server tests (tiers 1 and 2)** must use `mock_sync_client` / `mock_async_client` (in `conftest.py`).
  These build a client against a dummy host with the httpx backend and have **no** `gotenberg_host`
  dependency, so they never start Docker. Build the route inline from the client
  (`with mock_sync_client.chromium.html_to_pdf() as route: ...`).
- **Live tests (tier 3)** use `sync_client` / `async_client` (or the per-route fixtures built on them,
  e.g. `sync_merge_pdfs_route`). These resolve `gotenberg_host` and therefore require the Docker stack.

Do **not** give a mocked test `sync_client`/`async_client` or a `sync_*_route`/`async_*_route` fixture —
that drags the whole Docker stack into a test that never makes a real request. `webserver_docker_internal_url`
is just a hostname string (no Docker dependency) and is fine to use as a `.url()` argument in mocked tests.
Running `hatch test -m "not live"` exercises tiers 1 and 2 with zero Docker.

**Live tests require Docker.** The live tier spins up Gotenberg + an nginx webserver via `pytest-docker`
(compose files in `tests/docker/`). Docker must be available locally. Set `GOTENBERG_CLIENT_EDGE_TEST=1`
to test against the Gotenberg `:edge` image instead of the pinned release. `pytest-randomly` randomizes
test order and `pytest-xdist` runs in parallel by default.

Pytest markers (see `pyproject.toml`, `--strict-markers` is on): `live`, `chromium`, `libreoffice`,
`screenshot`, `httpx`, `niquests`, `requests`, `async_route`. `asyncio_mode = "auto"`, so `async def`
tests run without an explicit decorator. Sync and async variants are tested as separate classes/tests
(mirroring the `Sync*`/`Async*` code split), the async ones additionally marked `@pytest.mark.async_route`.

### Test-writing preferences

- **Parametrize over duplication.** Use `@pytest.mark.parametrize` to cover input/output variations
  rather than copy-pasting near-identical test functions (see `TestMeasurement` in `tests/test_options.py`).
- **`httpx_mock` (`pytest-httpx`)** is the preferred way to assert what request a route sends, and to
  simulate server responses/status codes (e.g. driving the 5xx retry loop). Pair it with
  `verify_stream_contains` for form-field assertions.
- **`mocker` (`pytest-mock`)** is the preferred way to patch/stub internals and assert on calls; prefer
  it over hand-rolled monkeypatching or `unittest.mock` directly.

## Architecture

### Sync/async duplication is the core pattern

Almost every class exists as a `Sync*` and `Async*` pair built on a shared generic base. The bases
are parameterized over `ClientT` (the HTTP client protocol). When adding or modifying functionality,
**you almost always change both the sync and async variant**, plus the shared base. Backend-agnostic
logic lives on the base; only the actual I/O (`_post_data`, context-manager enter/exit, `close`)
differs between sync and async.

- `client/base.py` — `BaseGotenbergClient` (abstract) plus `SyncGotenbergClient` / `AsyncGotenbergClient`.
  `GotenbergClient` is aliased to `SyncGotenbergClient`. The client holds the HTTP client + logger and
  exposes each route group as a property (`.chromium`, `.libre_office`, `.merge`, `.split`, `.metadata`,
  `.encrypt`, `.bookmarks`, etc.), each returning a fresh `*Api` instance. Webhook configuration lives
  here as `add_*_webhook_url` / `set_*_webhook_*` helpers that set `Gotenberg-Webhook-*` headers.
- `_base/api.py` — `BaseApi` / `SyncBaseApi` / `AsyncBaseApi`. An "Api" is a thin grouping that hands
  the client+logger to the routes it constructs.
- `_base/routes.py` — `BaseRoute` and `Sync`/`AsyncBaseRoute`. This is where the real request machinery
  lives: file maps, in-memory resources, embed files, form data, headers, `run()` / `run_with_retry()`,
  and the exponential-backoff retry loop that retries only on 5xx (4xx raise immediately).

### Route module layout

Each feature area is a package under `src/gotenberg_client/` with a consistent trio:

- `api.py` — the `*Api` class with factory methods that construct route objects (e.g.
  `chromium.html_to_pdf()` returns a `SyncHtmlToPdfRoute`).
- `routes.py` — concrete route classes. Each defines an `ENDPOINT_URL` and composes mixins to gain its
  option-setting methods; route-specific methods like `.index()`, `.url()`, `.resource()` add files.
- `mixins.py` (where present) — feature-area-specific option mixins.

Feature packages: `_chromium`, `_libreoffice`, `_merge`, `_pdfa_ua` (PDF/A & PDF/UA convert),
`_pdfmetadata` (read/write metadata), `_bookmarks` (read/write), and `_others` (embed, encrypt,
flatten, rotate, split, stamp, watermark). `_health.py` and `_version.py` are standalone read-only APIs.

### The mixin/builder pattern

Routes are assembled from many small mixins so that shared Gotenberg options (PDF/A format, metadata,
margins, page size, watermark, split mode, etc.) are defined once and mixed into every route that
supports them. Cross-route mixins live in `_common/mixins.py`; Chromium-only ones in
`_chromium/mixins.py`, etc. Every option method mutates `self._form_data` (or `self._headers` /
`self._file_map`) and returns `Self`, enabling the fluent chaining seen in the README. Mixins use
`# type: ignore[attr-defined]` because they reference `_form_data` etc. that only exist on the concrete
route — this is intentional, not a bug to "fix."

### HTTP backends

`_http_backends/` abstracts the three supported libraries behind `SyncClientProtocol` /
`AsyncClientProtocol` (`_protocols.py`). `make_sync_client` / `make_async_client` are factories
selected by `BackendType` (`"httpx" | "niquests" | "requests" | "auto"`). Backend modules are
imported **lazily** inside the factory so users only pay the import cost (and only need to install)
the backend they actually use. `"auto"` prefers httpx, then niquests. `requests` is sync-only and
raises if used for an async client. When touching request/response handling, keep all three backends
and the protocol in sync.

### Public API surface

`src/gotenberg_client/__init__.py` defines `__all__` — the supported public exports (clients, response
types, error types, `HealthStatus`, `BackendType`, `AuthType`, `BookmarkEntry`). Everything under a
`_`-prefixed package is internal. User-facing option enums/dataclasses (e.g. `PdfAFormat`,
`PageOrientation`, `CookieJar`, `WatermarkStampOptions`) live in `options.py` and are imported from
there. Responses (`SingleFileResponse`, `ZipFileResponse`, `PdfMetadata`) are in `responses.py`;
errors in `_errors.py`.

## Conventions

- Every source file starts with the SPDX MPL-2.0 header block.
- Ruff is configured with a large rule set (line length 120, single-line isort imports, relative imports
  banned). Run `hatch fmt` rather than hand-formatting.
- mypy runs in strict mode (`disallow_any_expr`, `disallow_untyped_defs`, etc.) over `src/` only; tests
  are excluded. New code must be fully typed.
- `Self` is imported from `_typing_compat` (not `typing`) for 3.10 compatibility.
- The version is single-sourced from `src/gotenberg_client/__about__.py`.
- Maintain `CHANGELOG.md` in keep-a-changelog format — CI validates it.
- Branch from and PR against `develop`, not `main`.
