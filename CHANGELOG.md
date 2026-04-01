# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking Changes

- `httpx` is no longer installed by default. Install the backend you want explicitly:
    - `pip install "gotenberg-client[httpx]"` - recommended; HTTP/2 and async support
    - `pip install "gotenberg-client[niquests]"` - HTTP/2 and async support
    - `pip install "gotenberg-client[requests]"` - sync-only
- `auth` parameter type changed from `httpx.BasicAuth | tuple[str, str] | None` to
  `tuple[str, str] | None` - `httpx.BasicAuth` is no longer accepted

### Added

- Pluggable HTTP backend: users can choose between
  [`httpx`](https://www.python-httpx.org/), [`niquests`](https://niquests.readthedocs.io/),
  or [`requests`](https://requests.readthedocs.io/) via the new `backend` parameter on
  `SyncGotenbergClient` / `AsyncGotenbergClient`
    - `backend="auto"` (default) - uses httpx if installed, falls back to niquests
    - `backend="httpx"` - always use httpx (requires `pip install "gotenberg-client[httpx]"`)
    - `backend="niquests"` - always use niquests (requires `pip install "gotenberg-client[niquests]"`)
    - `backend="requests"` - sync-only (requires `pip install "gotenberg-client[requests]"`)
- `HttpStatusError` exception exported from `gotenberg_client` - a backend-agnostic
  replacement for `httpx.HTTPStatusError` that is raised by `run()` and `run_with_retry()`
- `BackendType` type alias exported from `gotenberg_client` for type-annotating the `backend` argument
- `AuthType` type alias (`tuple[str, str] | None`) exported from `gotenberg_client` for
  type-annotating the `auth` argument
- `requests` sync-only backend: users who already have `requests` installed can now use
  it via `backend="requests"` on `SyncGotenbergClient`
    - `AsyncGotenbergClient` raises `ValueError` if `backend="requests"` is passed, since
      `requests` has no async support
- Watermark support: apply a watermark behind page content on Chromium,
  LibreOffice, Merge, and Split routes via `watermark_source()`, `watermark_expression()`,
  `watermark_pages()`, `watermark_options()`, and `watermark_file()`
- Stamp support: apply a stamp on top of page content on Chromium,
  LibreOffice, Merge, and Split routes via `stamp_source()`, `stamp_expression()`,
  `stamp_pages()`, `stamp_options()`, and `stamp_file()`
- Rotate support: rotate PDF pages by 90°, 180°, or 270° on Chromium,
  LibreOffice, Merge, and Split routes via `rotate(angle, pages=None)`
- Encrypt support: password-protect output PDFs on Chromium,
  LibreOffice, Merge, and Split routes via `user_password()` and `owner_password()`
- Embed support: attach external files inside the PDF container on
  Chromium, LibreOffice, Merge, and Split routes via `embed()` and `embed_files()`
- Download-from support: instruct Gotenberg to fetch input files
  from URLs rather than requiring direct uploads on Chromium, LibreOffice, Merge, and
  Split routes via `download_from(urls)`
- Flatten options now also applied to all Chromium conversion routes
- New option types in `gotenberg_client.options`:
    - `WatermarkStampSource` enum (`Text`, `Image`, `Pdf`)
    - `RotateAngle` enum (`Clockwise90`, `Clockwise180`, `Clockwise270`)
    - `WatermarkStampOptions` dataclass (font, points, color, rotation, opacity, scale)
    - `DownloadFromUrl` dataclass (url, extra_http_headers, embedded, field)
- New Chromium route options (available on all PDF and screenshot routes):
    - `wait_for_selector(selector)` — wait for a CSS selector before rendering
    - `emulated_media_features(features)` — override CSS media features (e.g. `prefers-color-scheme`)
    - `fail_on_resource_status_codes(codes)` — fail if any loaded resource returns a listed HTTP status code
    - `ignore_resource_status_domains(domains)` — exclude specific domains from resource status code checks
    - `skip_network_almost_idle(*, skip)` — skip the network "almost idle" event for faster rendering
- New Chromium PDF-only options:
    - `generate_tagged_pdf(*, generate)` — generate a tagged (accessible) PDF structure
- New Chromium PDF route convenience methods on `HeaderFooterMixin`:
    - `string_header(html)` — set the header from an in-memory HTML string
    - `string_footer(html)` — set the footer from an in-memory HTML string
- New LibreOffice route options:
    - `export_placeholders(*, export_placeholders)` — export placeholder fields to PDF
    - Native watermark support via `LibreOfficeNativeWatermarkMixin`: `native_watermark_text()`,
      `native_watermark_color()`, `native_watermark_font_height()`, `native_watermark_rotate_angle()`,
      `native_watermark_font_name()`, `native_tiled_watermark_text()`
    - PDF viewer preferences via `LibreOfficeViewerPreferencesMixin`: `initial_view()`, `initial_page()`,
      `magnification()`, `zoom()`, `page_layout()`, `first_page_on_left()`,
      `resize_window_to_initial_page()`, `center_window()`, `open_in_full_screen_mode()`,
      `display_pdf_document_title()`, `hide_viewer_menubar()`, `hide_viewer_toolbar()`,
      `hide_viewer_window_controls()`, `use_transition_effects()`, `open_bookmark_levels()`
    - New enums `InitialView`, `MagnificationOption`, and `PageLayout` in `gotenberg_client.options`
      for use with viewer preference methods
- New Merge PDF route options:
    - `auto_index_bookmarks(*, enable)` — auto-extract bookmarks from input PDFs and re-index page numbers
    - `merge_bookmarks(bookmark_list)` — set custom bookmarks on the merged PDF

### Changed

- Internal `RequestFiles` type changed from `dict` to `list[tuple[str, FileEntry]]` to
  preserve file ordering when multiple files are submitted in a single request
- `run()` and `run_with_retry()` now raise `HttpStatusError` (from `gotenberg_client`)
  instead of `httpx.HTTPStatusError` for non-2xx responses
    - **Migration**: replace `except httpx.HTTPStatusError` with `except HttpStatusError`
      after adding `from gotenberg_client import HttpStatusError`
- `MaxRetriesExceededError.response` is now typed as `ResponseProtocol` instead of
  `httpx.Response` - the object still exposes `.status_code`, `.headers`, `.content`
- Response `headers` field is now typed as `Mapping[str, str]` instead of `httpx.Headers`
    - `httpx.Headers` satisfies this interface so existing call sites are unaffected
- CI testing now runs against Gotenberg 8.29.1

### Security

- All GitHub Actions pinned to full commit SHAs (with tag version comments) to prevent
  supply-chain attacks via mutable tags

### Fixed

Gotenberg 8.29 modified the read metadata route (see [this discussion](https://github.com/gotenberg/gotenberg/discussions/1506)), which is now taken into account in testing

## [0.14.0] - 2023-03-11

### Changed

- [BREAKING]: Drop support for Python 3.9
    - This modernizes typing annotations and allows adding `slots` to all dataclasses

### Fixed

- A bug in the retry logic which would have raised almost immediately
- Minor internal class names were spelled incorrectly
- PDF/A-1b was missing as a PDF output option

## [0.13.1] - 2025-12-04

### Fixed

- Allow for more than 10 Documents to be merged while keeping the sorting intact
- Loosen restrictions on hatchling for building

## [0.13.0] - 2025-11-18

### Changed

- Bumps astral-sh/setup-uv from 6.8.0 to 7.1.2
- Bumps actions/upload-artifact from 4.6.2 to 5.0.0
- Bumps actions/download-artifact from 5.0.0 to 6.0.0
- Bumps github/codeql-action from 3 to 4

### Fixed

- Replaces bad import from gotenberg_client.options to gotenberg_client.constants to align with the updated Gotenberg client API on usage docs
- Incorrect form field for Libreoffice maximum image resolution

## [0.12.0] - 2025-10-15

### Added

- Validates the changelog format is correct during CI linting job
- LibreOffice route can use in-memory buffer for conversions by @gunnar-rydberg ([#68](https://github.com/stumpylog/gotenberg-client/pull/68))

### Changed

- Bumps pypa/gh-action-pypi-publish from 1.12.4 to 1.13.0
- Bumps astral-sh/setup-uv from 6.6.0 to 6.8.0
- Bumps actions/setup-python from 5.6.0 to 6.0.0
- Bumps actions/cache from 4.2.4 to 4.3.0
- Bumps ncipollo/release-action from 1.18.0 to 1.20.0
- Transitions from pre-commit to prek

### Fixed

- Some note callouts were not properly formatted in the documentation

## [0.11.0] - 2025-08-28

### Added

- [zizmor](https://woodruffw.github.io/zizmor/) is now enabled to audit the workflows
- yamlfmt is now used to format all YAML files
- Fixes examples around route.index

### Changed

- Drops testing against pypy, as pikepdf no longer provides wheels for it
- Updates CI testing to use Gotenberg 8.22.0
- Updates development dependencies
- Updates GitHub Action versions

### Fixed

- Fixes an issue with the actions lockdown preventing documentation deployment

## [0.10.0] - 2025-04-21

### Changed

- Reworked Codecov integration ([#50](https://github.com/stumpylog/gotenberg-client/pull/50))
- Update CI to use astral-sh/setup-uv instead of pip ([#51](https://github.com/stumpylog/gotenberg-client/pull/51))
- Test in CI using Gotenberg 8.17.3 ([#52](https://github.com/stumpylog/gotenberg-client/pull/52))
- Bump pypa/gh-action-pypi-publish from 1.12.3 to 1.12.4 by @dependabot ([#49](https://github.com/stumpylog/gotenberg-client/pull/49))

### Added

- Asynchronous support for all implemented routes ([#53](https://github.com/stumpylog/gotenberg-client/pull/53))
    - Also implemented split and flatten routes
    - Also added support for cookies, and other new fields as of Gotenberg 8.19
    - Be sure to check the documentation for more!
- Add automatic API documentation as well ([#54](https://github.com/stumpylog/gotenberg-client/pull/54))

## [0.9.0] - 2025-01-09

### Breaking Change

- Drop testing on PyPy3.9 ([#45](https://github.com/stumpylog/gotenberg-client/pull/45))
    - The library should still work, but required wheels for testing are no longer built against pypy3.9. Flagging this as breaking just for an FYI

### Added

- Allow setting user agent string and provide a default ([#46](https://github.com/stumpylog/gotenberg-client/pull/46))
- Allow providing an instance of [httpx.BasicAuth](https://www.python-httpx.org/advanced/authentication/#basic-authentication) when creating the client ([#47](https://github.com/stumpylog/gotenberg-client/pull/47))
- Documentation and project management updates ([#48](https://github.com/stumpylog/gotenberg-client/pull/48))
    - Enabled discussions for Q&A and Feature Requests
    - Created a bug report template
    - Created a contributing guide

## [0.8.2] - 2024-12-17

### Fixed

- Bump pypa/gh-action-pypi-publish from 1.12.2 to 1.12.3, fixing core metadata publishing issue

## [0.8.1] - 2024-12-17

### Fixed

- Relaxed version restriction on `httpx`

### Changed

- Test in CI using Gotenberg 8.14.1

## [0.8.0] - 2024-12-11

### Breaking Change

- Dropped support for Python 3.8 ([#43](https://github.com/stumpylog/gotenberg-client/pull/43))

### Added

- Official support and testing for Python 3.13 ([#25](https://github.com/stumpylog/gotenberg-client/pull/25))
- Support for setting PDF metadata ([#42](https://github.com/stumpylog/gotenberg-client/pull/42))
    - Initial work by @spechtx in ([#40](https://github.com/stumpylog/gotenberg-client/pull/40))
- Integrated Codecov test analytics ([#44](https://github.com/stumpylog/gotenberg-client/pull/44))

### Changed

- Use `pytest-docker` to manage Docker image services ([#36](https://github.com/stumpylog/gotenberg-client/pull/36))
- Bump Bump pypa/gh-action-pypi-publish from 1.10.2 to 1.12.2 by @dependabot ([#41](https://github.com/stumpylog/gotenberg-client/pull/41))
- Bump codecov/codecov-action from 4 to 5 by @dependabot ([#41](https://github.com/stumpylog/gotenberg-client/pull/41))

## [0.7.0] - 2024-10-08

### Fixed

- `mike` deployment mis-ordered the version and alias, this has been corrected
- `mypy` wasn't running correctly in CI
- Wrong paper size preset for A4 by [@mannerydhe](https://github.com/mannerydhe) ([#24](https://github.com/stumpylog/gotenberg-client/pull/24))

### Added

- All routes now return a stronger typed response than just an `httpx.Response` ([#23](https://github.com/stumpylog/gotenberg-client/pull/23))
- All public methods now include docstrings ([#33](https://github.com/stumpylog/gotenberg-client/pull/33))
- The Chromium based HTML and Markdown to PDF routes can now accept accept a `str`, containing either HTML text, Markdown or other text based resources for conversion ([#30](https://github.com/stumpylog/gotenberg-client/pull/30))
    - See `string_index`, `string_resource` and `string_resources` for those routes

### Changed

- Bump pypa/gh-action-pypi-publish from 1.8.14 to 1.9.0 by @dependabot ([#25](https://github.com/stumpylog/gotenberg-client/pull/25))
- Bump pypa/gh-action-pypi-publish from 1.9.0 to 1.10.2 by @dependabot ([#31](https://github.com/stumpylog/gotenberg-client/pull/31))
- CI testing now runs against Gotenberg 8.11 ([#32](https://github.com/stumpylog/gotenberg-client/pull/32))
- Development tool updates in `pyproject.toml` and pre-commit hook updates
- Properly use `pytest` fixtures in all testing ([#34](https://github.com/stumpylog/gotenberg-client/pull/34))
- Upgrade `pre-commit` to 4.0.1 ([#35](https://github.com/stumpylog/gotenberg-client/pull/35))

## [0.6.0] - 2024-06-13

### Breaking Change

- Only Gotenberg 8 is now supported

### Fixed

- The documentation site's changelog was not updating with the changes

### Added

- `codespell` pre-commit hook
- Link to the full documentation from the README
- Documentation of all implemented routes ([#16](https://github.com/stumpylog/gotenberg-client/pull/16))
- Page margins may now specify the units of the margin ([#21](https://github.com/stumpylog/gotenberg-client/pull/21))

### Changed

- Bump codecov/codecov-action from 3 to 4 by @dependabot ([#11](https://github.com/stumpylog/gotenberg-client/pull/11))
- Bump release-flow/keep-a-changelog-action from 2 to 3 by @dependabot ([#12](https://github.com/stumpylog/gotenberg-client/pull/12))
- Bump pypa/gh-action-pypi-publish from 1.8.11 to 1.8.12 by @dependabot ([#13](https://github.com/stumpylog/gotenberg-client/pull/13))
- Bump pre-commit/action from 3.0.0 to 3.0.1 by @dependabot ([#14](https://github.com/stumpylog/gotenberg-client/pull/14))
- Bump pypa/gh-action-pypi-publish from 1.8.12 to 1.8.14 by @dependabot ([#15](https://github.com/stumpylog/gotenberg-client/pull/15))
- Use hatch commands for testing and linting ([#17](https://github.com/stumpylog/gotenberg-client/pull/17))
- Update testing Docker image to Gotenberg 8.5.0 ([#18](https://github.com/stumpylog/gotenberg-client/pull/18))
- chore: Formats JSON files with prettier ([#19](https://github.com/stumpylog/gotenberg-client/pull/19))
- chore: Updates Gotenberg test image to 8.5.1 ([#20](https://github.com/stumpylog/gotenberg-client/pull/20))
- chore: Updates mike to ~2.1.1 ([#22](https://github.com/stumpylog/gotenberg-client/pull/22))

## [0.5.0] - 2024-01-11

### Added

- Documentation site built with Github Pages and Material for MkDocs
- New method `.run_with_retry` for routes, which allows the route to be rerun as configured, with progressive backoff if the server returns a server error
- Support for Gotenberg [Webhooks](https://gotenberg.dev/docs/webhook)

### Deprecated

- Support for Gotenberg 7.x. This will likely be the last release to support 7.x, as the options for PDF/A have been changed

## [0.4.1] - 2023-12-11

### Fixed

- Implemented an internal workaround for older Gotenberg versions and their handling of non-latin filenames.
    - When detected, the files will be copied into a temporary directory and the filename cleaned
    - Gotenberg 8.0.0 will start implementing something similar once released
- The pulled Gotenberg image is now inspected, allowing local re-creation of failures against specific digests
- The `:edge` tag testing is now allowed to fail

## [0.4.0] - 2023-12-04

### Changed

- Removed some certain special cases from coverage
- Updated `pre-commit` hook versions
- Updated how pytest is configured, so it will apply to any invocation
- Updated test running image to log at warning or lower using text format
- Updated test running image from 7.9.2 to 7.10.1
- For the moment, send both `pdfa` and `pdfFormat` for compatibility with 7.9 and 7.10
    - See [here](https://github.com/stumpylog/gotenberg-client/issues/5#issuecomment-1839081129) for some subtle differences in what these options mean

### Added

- Added new test job against Gotenberg's `:edge` tag

## [0.3.0] - 2023-10-17

### Added

- Support for the output filename and request tracing for all routes

### Removed

- References to compression and Brotli. Gotenberg doesn't seem to ever compress response data

### Fixed

- An issue with the sorting of merging PDFs. Expanded testing to cover the merged ordering

### Changed

- Multiple merge calls on the same route will maintain the ordering of all files, rather than just per merge call

## [0.2.0] - 2023-10-16

### Added

- CodeQL scanning via GitHub
- Codecov.io coverage shield

### Changed

- Updated pypa/gh-action-pypi-publish from 1.8.8 to 1.8.10
- Updated actions/checkout from 3 to 4
- Mis-spelled `gotenerg_url` for a `Client` is now `host` and no longer keyword only

## [0.1.0] - 2023-10-15

### Added

- Chromium conversion routes
- LibreOffice conversion routes
- PDF/A conversion route
- PDF merge route
- Health status route
- Testing and typing all setup and passing
