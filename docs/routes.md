# API Routes

## Chromium

Access to the Chromium module of Gotenberg, as documented
[here](https://gotenberg.dev/docs/routes#convert-with-chromium).

### URL into PDF

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#url-into-pdf-route)

Route Access: `client.chromium.url_to_pdf()`

Required Properties:

- `.url("http://localhost:8888")`

See also [common Chromium options](#chromium-common-options)

### HTML file into PDF

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#html-file-into-pdf-route)

Route Access: `client.chromium.html_to_pdf()`

Required Properties:

- An index file is required:
    - `.index(Path("index.html"))` sets the index from an HTML file
    - `.string_index("<html></html>")` sets the index as the HTML string

Optional Properties:

- Provide additional resource files as needed:
    - `.resource(Path("file-here"))` or `.resources([Path("file1"), Path("file2")])` adds the file or files as a resource for the HTML index
    - Add a single string resource with `.string_resource("file content", name="style.css")`
    - Add multiple string resources with `.string_resources([("content", "name.css", "text/css"), ...])`

See also [common Chromium options](#chromium-common-options).

!!! note

    `string_resource` and `string_resources` currently only support text data, not binary data

### Markdown file(s) into PDF

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route)

Route Access: `client.chromium.markdown_to_pdf()`

Required Properties:

- An index file is required:
    - `.index(Path("index.html"))` sets the index from an HTML file
    - `.string_index("<html></html>")` sets the index as the HTML string
- At least one Markdown file:
    - `.markdown_file(Path("readme.md"))` adds a single Markdown file
    - `.markdown_files([Path("a.md"), Path("b.md")])` adds multiple Markdown files

Optional Properties:

- Provide additional resource files as needed:
    - `.resource(Path("file-here"))` or `.resources([Path("file1"), Path("file2")])` adds the file or files as a resource for the HTML index
    - Add string resources with `.string_resource("file content", name="style.css")`

See also [common Chromium options](#chromium-common-options).

!!! note

    `string_resource` currently only supports text data, not binary data

### Screenshot Routes

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#screenshots-route)

Three screenshot routes are available, each corresponding to a different input source:

| Route Access                            | Input                                                                               |
| --------------------------------------- | ----------------------------------------------------------------------------------- |
| `client.chromium.screenshot_url()`      | A URL — use `.url("https://example.com")`                                           |
| `client.chromium.screenshot_html()`     | An HTML file — uses the same `.index()` / `.resource()` methods as HTML-to-PDF      |
| `client.chromium.screenshot_markdown()` | Markdown — uses the same `.index()` / `.markdown_file()` methods as Markdown-to-PDF |

#### Common Settings

| Gotenberg Option | Route Configuration                                                                     | Python Type                      | Notes                           |
| ---------------- | --------------------------------------------------------------------------------------- | -------------------------------- | ------------------------------- |
| width            | `.width()`                                                                              | `int`                            |                                 |
| height           | `.height()`                                                                             | `int`                            |                                 |
| clip             | `.clip()` or `.clip_to_dimensions()` or `.no_clip_to_dimensions()`                      | `bool`                           |                                 |
| format           | `.output_format()`                                                                      | `Literal["png", "jpeg", "webp"]` | defaults to `"png"`             |
| quality          | `.quality()`                                                                            | `int`, between 0 and 100         | out-of-range values are clamped |
| omitBackground   | `.omit_background()` or `.hide_background()` or `.show_background()`                    | `bool`                           |                                 |
| optimizeForSpeed | `.image_optimize()` or `.image_optimize_for_speed()` or `.image_optimize_for_quality()` | `bool`                           |                                 |

This route also supports other Chromium options:

- [Wait Before Rendering](#render-control)
- [Emulated Media Type](#emulated-media-type)
- [Cookies](#cookies)
- [Custom HTTP headers](#custom-http-headers)
- [Invalid HTTP Status Codes](#http-status-codes)
- [Console Exceptions](#console-exceptions)
- [Performance Mode](#performance-mode)

### Chromium Common Options

#### Page Properties

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#page-properties-chromium)

| Gotenberg Option                                                                                | Route Configuration                                                       | Python Type                   | Notes        |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------- | ------------ |
| `singlePage`                                                                                    | `.single_page()`                                                          | `bool`                        | keyword only |
| <ul><li>`paperWidth`</li><li>`paperHeight`</li></ul>                                            | `.size()`                                                                 | `PageSize`                    |              |
| <ul><li>`marginTop`</li><li>`marginBottom`</li><li>`marginLeft`</li><li>`marginRight`</li></ul> | `.margins()`                                                              | `PageMarginsType`             |              |
| `preferCssPageSize`                                                                             | <ul><li>`.prefer_css_page_size()`<li>`.prefer_set_page_size()`</li></ul>  | N/A                           |              |
| `printBackground`                                                                               | <ul><li>`.background_graphics()`<li>`.no_background_graphics()`</li></ul> | N/A                           |              |
| `omitBackground`                                                                                | <ul><li>`.hide_background()`<li>`.show_background()`</li></ul>            | N/A                           |              |
| `landscape`                                                                                     | `.orient()`                                                               | `PageOrientation`             |              |
| `scale`                                                                                         | `.scale()`                                                                | <code>int &#124; float</code> |              |
| `nativePageRanges`                                                                              | `.page_ranges()`                                                          | `str`                         |              |
| `generateDocumentOutline`                                                                       | `.generate_document_outline()`                                            | `bool`                        | keyword only |

#### Header & Footer

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#header-footer-chromium)

| Gotenberg Option | Route Configuration | Python Type | Notes |
| ---------------- | ------------------- | ----------- | ----- |
| `header.html`    | `.header()`         | `Path`      |       |
| `footer.html`    | `.footer()`         | `Path`      |       |

#### Render Control

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#wait-before-rendering-chromium)

| Gotenberg Option    | Route Configuration    | Python Type                                    | Notes                                          |
| ------------------- | ---------------------- | ---------------------------------------------- | ---------------------------------------------- |
| `waitDelay`         | `.render_wait()`       | <code>int &#124; float &#124; timedelta</code> | Raises `NegativeWaitDurationError` if negative |
| `waitForExpression` | `.render_expression()` | `str`                                          |                                                |

#### Emulated Media Type

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#emulated-media-type-chromium)

| Gotenberg Option    | Route Configuration | Python Type                  | Notes |
| ------------------- | ------------------- | ---------------------------- | ----- |
| `emulatedMediaType` | `.media_type()`     | `Literal["print", "screen"]` |       |

#### Cookies

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#cookies-chromium)

| Gotenberg Option | Route Configuration | Python Type       | Notes |
| ---------------- | ------------------- | ----------------- | ----- |
| `cookies`        | `.cookies()`        | `list[CookieJar]` |       |

#### Custom HTTP Headers

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#custom-http-headers-chromium)

| Gotenberg Option   | Route Configuration | Python Type      | Notes                                                 |
| ------------------ | ------------------- | ---------------- | ----------------------------------------------------- |
| `extraHttpHeaders` | `.headers()`        | `dict[str, str]` | The dictionary of values will be JSON encoded for you |
| `userAgent`        | `.user_agent()`     | `str`            |                                                       |

#### HTTP Status Codes

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#invalid-http-status-codes-chromium)

| Gotenberg Option        | Route Configuration       | Python Type            | Notes |
| ----------------------- | ------------------------- | ---------------------- | ----- |
| `failOnHttpStatusCodes` | `.fail_on_status_codes()` | `Iterable[HTTPStatus]` |       |

#### Network Errors

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#network-errors-chromium)

| Gotenberg Option              | Route Configuration                                                          | Python Type | Notes |
| ----------------------------- | ---------------------------------------------------------------------------- | ----------- | ----- |
| `failOnResourceLoadingFailed` | `.fail_on_resource_loading_failed(*, fail_on_resource_loading_failed: bool)` | `bool`      |       |

#### Console Exceptions

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#console-exceptions-chromium)

| Gotenberg Option          | Route Configuration                                                       | Python Type | Notes |
| ------------------------- | ------------------------------------------------------------------------- | ----------- | ----- |
| `failOnConsoleExceptions` | <ul><li>`.fail_on_exceptions()`<li>`.dont_fail_on_exceptions()`</li></ul> | N/A         |       |

#### Performance Mode

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#performance-mode-chromium)

| Gotenberg Option       | Route Configuration                                               | Python Type | Notes |
| ---------------------- | ----------------------------------------------------------------- | ----------- | ----- |
| `skipNetworkIdleEvent` | <ul><li>`.skip_network_idle()`<li>`.use_network_idle()`</li></ul> | N/A         |       |

#### Split

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#split-chromium)

| Gotenberg Option | Route Configuration | Python Type                     | Notes        |
| ---------------- | ------------------- | ------------------------------- | ------------ |
| `splitMode`      | `.split_mode()`     | `Literal["pages", "intervals"]` |              |
| `splitSpan`      | `.split_span()`     | `str`                           |              |
| `splitUnify`     | `.split_unify()`    | `bool`                          | keyword only |

#### PDF/A & PDF/UA

| Gotenberg Option | Route Configuration                                                             | Python Type  | Notes |
| ---------------- | ------------------------------------------------------------------------------- | ------------ | ----- |
| `pdfa`           | `.pdf_format()`                                                                 | `PdfAFormat` |       |
| `pdfua`          | <ul><li>`.enable_universal_access()`<li>`.disable_universal_access()`</li></ul> | N/A          |       |

#### PDF Metadata Support

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#metadata-chromium)

Add metadata to your PDFs:

```python
from gotenberg_client import GotenbergClient
from datetime import datetime
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.html_to_pdf() as route:
        response = (route
            .index(Path("my-index.html"))
            .metadata(
                title="My Document",
                author="John Doe",
                creation_date=datetime.now(),
                keywords=["sample", "document"],
                subject="Sample PDF Generation",
            )
            .run())
```

Supported metadata fields:

- `title`: Document title
- `author`: Document author
- `subject`: Document subject
- `keywords`: List of keywords (no commas in individual keywords)
- `creator`: Creating application
- `creation_date`: Creation datetime
- `modification_date`: Last modification datetime
- `producer`: PDF producer
- `trapped`: Trapping status (`bool`, or `TrappedStatus.TRUE` / `TrappedStatus.FALSE` / `TrappedStatus.UNKNOWN`)
- `pdf_copyright`: Copyright information
- `marked`: PDF marked status (`bool`)
- `pdf_version`: PDF version number (1.0–2.0)

!!! note

    Some fields cannot be set or will be overwritten, depending on Gotenberg and its utilized PDF engine

#### Flatten, Watermark, Stamp, Rotate, Encrypt, Embeds, Download From

Chromium conversion routes also support flattening, watermarking, stamping, rotation,
encryption, file embedding, and URL-based input. See the [Global Options](#global-options)
section for details.

## LibreOffice

### Office Documents to PDF

| Gotenberg Link                                                                      | Route Access                   | Required Properties                                                                                                                                                      | Optional Properties                                       |
| ----------------------------------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------- |
| [Documentation](https://gotenberg.dev/docs/routes#office-documents-into-pdfs-route) | `client.libre_office.to_pdf()` | <p>Any of:</p><ul><li>`.convert(Path("mydoc.docx"))`</li><li>`.convert_files([Path("mydoc.docx")])`</li><li>`.convert_in_memory_file(data, name="mydoc.docx")`</li></ul> | See [common LibreOffice options](#libreoffice-properties) |

!!! note

    `convert` / `convert_in_memory_file` may be called multiple times

!!! note

    `convert_files` is a convenience method to convert a list of files into PDF

### LibreOffice Properties

#### Page Properties

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#page-properties-libreoffice)

| Gotenberg Option                  | Route Configuration                      | Python Type       | Notes                            |
| --------------------------------- | ---------------------------------------- | ----------------- | -------------------------------- |
| `landscape`                       | `.orient()`                              | `PageOrientation` |                                  |
| `nativePageRanges`                | `.page_ranges()`                         | `str`             | e.g. `"1-5,8,11-13"`             |
| `exportFormFields`                | `.export_form_fields()`                  | `bool`            | keyword only                     |
| `singlePageSheets`                | `.single_page_sheets()`                  | `bool`            | keyword only; spreadsheets only  |
| `password`                        | `.password()`                            | `str`             | for password-protected documents |
| `updateIndexes`                   | `.update_indexes()`                      | `bool`            | keyword only                     |
| `allowDuplicateFieldNames`        | `.allow_duplicate_form_fields()`         | `bool`            | keyword only                     |
| `exportBookmarks`                 | `.export_bookmarks()`                    | `bool`            | keyword only                     |
| `exportBookmarksToPdfDestination` | `.export_bookmarks_to_pdf_destination()` | `bool`            | keyword only                     |
| `exportNotes`                     | `.export_notes()`                        | `bool`            | keyword only                     |
| `exportNotesPages`                | `.export_notes_pages()`                  | `bool`            | keyword only; presentations only |
| `exportOnlyNotesPages`            | `.export_only_notes_pages()`             | `bool`            | keyword only; presentations only |
| `exportNotesInMargin`             | `.export_notes_in_margin()`              | `bool`            | keyword only                     |
| `convertOooTargetToPdfTarget`     | `.convert_ooo_target_to_pdf_target()`    | `bool`            | keyword only                     |
| `exportLinksRelativeFsys`         | `.export_links_relative_fsys()`          | `bool`            | keyword only                     |
| `exportHiddenSlides`              | `.export_hidden_slides()`                | `bool`            | keyword only; presentations only |
| `skipEmptyPages`                  | `.skip_empty_pages()`                    | `bool`            | keyword only                     |
| `addOriginalDocumentAsStream`     | `.add_original_document_as_stream()`     | `bool`            | keyword only                     |

#### Compress

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#compress-libreoffice)

| Gotenberg Option           | Route Configuration             | Python Type                        | Notes                           |
| -------------------------- | ------------------------------- | ---------------------------------- | ------------------------------- |
| `losslessImageCompression` | `.lossless_image_compression()` | `bool`                             | keyword only                    |
| `quality`                  | `.quality()`                    | `int` (1–100)                      | out-of-range values are clamped |
| `reduceImageResolution`    | `.reduce_image_resolution()`    | `bool`                             | keyword only                    |
| `maxImageResolution`       | `.max_image_resolution()`       | `Literal[75, 150, 300, 600, 1200]` | DPI                             |

#### Merge

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#merge-libreoffice)

| Gotenberg Option | Route Configuration                              | Python Type | Notes |
| ---------------- | ------------------------------------------------ | ----------- | ----- |
| `merge`          | <ul><li>`.do_merge()`<li>`.no_merge()`</li></ul> | N/A         |       |

!!! note

    If multiple files are provided, and the merge is left as default or `no_merge()` is called, the resulting file will be a zip

#### Split

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#split-libreoffice)

| Gotenberg Option | Route Configuration | Python Type                     | Notes        |
| ---------------- | ------------------- | ------------------------------- | ------------ |
| `splitMode`      | `.split_mode()`     | `Literal["pages", "intervals"]` |              |
| `splitSpan`      | `.split_span()`     | `str`                           | e.g. `"1-3"` |
| `splitUnify`     | `.split_unify()`    | `bool`                          | keyword only |

#### PDF/A & PDF/UA

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#pdfa-libreoffice)

| Gotenberg Option | Route Configuration                                                             | Python Type  | Notes |
| ---------------- | ------------------------------------------------------------------------------- | ------------ | ----- |
| `pdfa`           | `.pdf_format()`                                                                 | `PdfAFormat` |       |
| `pdfua`          | <ul><li>`.enable_universal_access()`<li>`.disable_universal_access()`</li></ul> | N/A          |       |

#### Metadata

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#metadata-libreoffice)

See [PDF Metadata Support](#pdf-metadata-support) for the API interface.

#### Flatten

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#flatten-libreoffice)

| Gotenberg Option | Route Configuration | Python Type | Notes        |
| ---------------- | ------------------- | ----------- | ------------ |
| `flatten`        | `.flatten()`        | `bool`      | keyword only |

#### Watermark, Stamp, Rotate, Encrypt, Embeds, Download From

The LibreOffice route also supports watermarking, stamping, rotation, encryption, file
embedding, and URL-based input. See the [Global Options](#global-options) section for
details.

## Convert into PDF/A & PDF/UA

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route)

Route Access: `client.pdf_convert.to_pdfa()`

Required Properties:

- At least one file via `.convert(Path("file.pdf"))` or `.convert_files([...])`
- At least one of `pdf_format()`, `enable_universal_access()`, or `disable_universal_access()` must be set

| Gotenberg Option | Route Configuration                                                             | Python Type  | Notes |
| ---------------- | ------------------------------------------------------------------------------- | ------------ | ----- |
| `pdfa`           | `.pdf_format()`                                                                 | `PdfAFormat` |       |
| `pdfua`          | <ul><li>`.enable_universal_access()`<li>`.disable_universal_access()`</li></ul> | N/A          |       |

```python
from gotenberg_client import GotenbergClient
from gotenberg_client.options import PdfAFormat
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.pdf_convert.to_pdfa() as route:
        response = (
            route.convert(Path("my.pdf"))
            .pdf_format(PdfAFormat.A2b)
            .run()
        )
        response.to_file(Path("my-pdfa.pdf"))
```

## Read PDF Metadata

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#read-pdf-metadata-route)

Route Access: `client.metadata.read()`

Required Properties:

- At least one file via `.read(Path("file.pdf"))` or `.read_files([...])`

!!! note

    Unlike other routes, `.run()` returns `dict[str, dict[str, str]]` — one entry per input file mapping to that file's metadata fields — rather than a file response.

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.metadata.read() as route:
        metadata = route.read(Path("my.pdf")).run()
        # metadata == {"my.pdf": {"Title": "...", "Author": "...", ...}}
```

## Write PDF Metadata

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#write-pdf-metadata-route)

Route Access: `client.metadata.write()`

Required Properties:

- At least one file via `.write(Path("file.pdf"))` or `.write_files([...])`
- At least one metadata field set via `.metadata()`

See [PDF Metadata Support](#pdf-metadata-support) for all available metadata fields.

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.metadata.write() as route:
        response = (
            route.write(Path("my.pdf"))
            .metadata(title="New Title", author="New Author")
            .run()
        )
        response.to_file(Path("my-updated.pdf"))
```

## Merge PDFs

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#merge-pdfs-route)

Route Access: `client.merge.merge()`

Required Properties:

- At least one call to `.merge([Path("a.pdf"), Path("b.pdf")])` — list order determines merge order

Optional Properties:

| Gotenberg Option | Route Configuration                                                             | Python Type             | Notes                                             |
| ---------------- | ------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------- |
| `pdfa`           | `.pdf_format()`                                                                 | `PdfAFormat`            |                                                   |
| `pdfua`          | <ul><li>`.enable_universal_access()`<li>`.disable_universal_access()`</li></ul> | N/A                     |                                                   |
| `flatten`        | `.flatten()`                                                                    | `bool`                  | keyword only                                      |
| `metadata`       | `.metadata()`                                                                   | N/A                     | See [PDF Metadata Support](#pdf-metadata-support) |
| watermark        | See [Watermark](#watermark)                                                     | `WatermarkStampSource`  |                                                   |
| stamp            | See [Stamp](#stamp)                                                             | `WatermarkStampSource`  |                                                   |
| rotate           | `.rotate()`                                                                     | `RotateAngle`           |                                                   |
| encrypt          | `.user_password()` / `.owner_password()`                                        | `str`                   |                                                   |
| embeds           | `.embed()` / `.embed_files()`                                                   | `Path` / `list[Path]`   |                                                   |
| downloadFrom     | `.download_from()`                                                              | `list[DownloadFromUrl]` |                                                   |

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.merge.merge() as route:
        response = route.merge([Path("a.pdf"), Path("b.pdf"), Path("c.pdf")]).run()
        response.to_file(Path("merged.pdf"))
```

!!! note

    Prefixes will be added to the file to ensure they are merged in the order provided to `merge()`, even with multiple calls

## Split PDFs

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#split-pdfs-route)

Route Access: `client.split.split()`

Required Properties:

- At least one file via `.split(Path("file.pdf"))` or `.split_files([...])`
- `.split_mode()` and `.split_span()` must be configured

Optional Properties:

| Gotenberg Option | Route Configuration                                                             | Python Type                     | Notes                                             |
| ---------------- | ------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------- |
| `splitMode`      | `.split_mode()`                                                                 | `Literal["pages", "intervals"]` |                                                   |
| `splitSpan`      | `.split_span()`                                                                 | `str`                           | e.g. `"1-3"`                                      |
| `splitUnify`     | `.split_unify()`                                                                | `bool`                          | keyword only                                      |
| `pdfa`           | `.pdf_format()`                                                                 | `PdfAFormat`                    |                                                   |
| `pdfua`          | <ul><li>`.enable_universal_access()`<li>`.disable_universal_access()`</li></ul> | N/A                             |                                                   |
| `flatten`        | `.flatten()`                                                                    | `bool`                          | keyword only                                      |
| `metadata`       | `.metadata()`                                                                   | N/A                             | See [PDF Metadata Support](#pdf-metadata-support) |
| watermark        | See [Watermark](#watermark)                                                     | `WatermarkStampSource`          |                                                   |
| stamp            | See [Stamp](#stamp)                                                             | `WatermarkStampSource`          |                                                   |
| rotate           | `.rotate()`                                                                     | `RotateAngle`                   |                                                   |
| encrypt          | `.user_password()` / `.owner_password()`                                        | `str`                           |                                                   |
| embeds           | `.embed()` / `.embed_files()`                                                   | `Path` / `list[Path]`           |                                                   |
| downloadFrom     | `.download_from()`                                                              | `list[DownloadFromUrl]`         |                                                   |

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.split.split() as route:
        response = (
            route.split(Path("large.pdf"))
            .split_mode("pages")
            .split_span("1-3")
            .run()
        )
        # Split produces a ZIP containing the resulting pages
        response.to_file(Path("split.zip"))
```

## Flatten PDFs

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#flatten-pdfs-route)

Route Access: `client.flatten.flatten()`

Required Properties:

- At least one file via `.flatten(Path("file.pdf"))` or `.flatten_files([...])`

```python
from gotenberg_client import GotenbergClient
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.flatten.flatten() as route:
        response = route.flatten(Path("my.pdf")).run()
        response.to_file(Path("flattened.pdf"))
```

## Health Check

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#health-check-route)

Route Access: `client.health.health()`

Returns a `HealthStatus` object with:

- `overall`: overall service status (`StatusOptions.Up` or `StatusOptions.Down`)
- `chromium`: `ModuleStatus` for the Chromium module (or `None` if not present)
- `uno`: `ModuleStatus` for the LibreOffice/UNO module (or `None` if not present)

## Metrics

!!! warning

    This route is not implemented

## Version

!!! warning

    This route is not implemented

## Debug

!!! warning

    This route is not implemented

## Global Options

### Request Tracing

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#request-tracing)

Set a trace ID on any route to correlate Gotenberg server logs with your requests:

```python
with client.chromium.html_to_pdf() as route:
    response = route.index(Path("index.html")).trace_id("my-request-123").run()
```

### Output Filename

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#output-filename)

Control the filename Gotenberg sets in the `Content-Disposition` response header:

```python
with client.chromium.html_to_pdf() as route:
    response = route.index(Path("index.html")).output_filename("report.pdf").run()
```

### Download From

[Gotenberg Documentation](https://gotenberg.dev/docs/webhook-download)

Instruct Gotenberg to fetch input files from URLs instead of requiring direct uploads.
Available on Chromium, LibreOffice, Merge, and Split routes.

```python
from gotenberg_client import GotenbergClient
from gotenberg_client.options import DownloadFromUrl
from pathlib import Path

with GotenbergClient("http://localhost:3000") as client:
    with client.chromium.url_to_pdf() as route:
        response = route.download_from([
            DownloadFromUrl(url="https://example.com/my.html"),
        ]).run()
        response.to_file(Path("output.pdf"))
```

`DownloadFromUrl` fields:

| Field                | Type                     | Notes                                            |
| -------------------- | ------------------------ | ------------------------------------------------ |
| `url`                | `str`                    | Required                                         |
| `extra_http_headers` | `dict[str, str] \| None` | Additional request headers                       |
| `embedded`           | `bool`                   | Embed the file in the request (default: `False`) |
| `field`              | `str \| None`            | Override the form field name                     |

### Watermark

[Gotenberg Documentation](https://gotenberg.dev/docs/manipulate-pdfs/watermark-pdfs)

Apply a watermark behind the content of each page. Available on Chromium, LibreOffice,
Merge, and Split routes.

| Route Method              | Python Type             | Notes                                                                |
| ------------------------- | ----------------------- | -------------------------------------------------------------------- |
| `.watermark_source()`     | `WatermarkStampSource`  | `Text`, `Image`, or `Pdf`                                            |
| `.watermark_expression()` | `str`                   | Text string or expression (when source is `Text`)                    |
| `.watermark_pages()`      | `str`                   | Page range (e.g. `"1-3"`)                                            |
| `.watermark_options()`    | `WatermarkStampOptions` | Font, size, color, rotation, opacity, scale                          |
| `.watermark_file()`       | `Path`                  | Image or PDF file to use as watermark (when source is `Image`/`Pdf`) |

### Stamp

[Gotenberg Documentation](https://gotenberg.dev/docs/manipulate-pdfs/stamp-pdfs)

Apply a stamp on top of the content of each page. Available on Chromium, LibreOffice,
Merge, and Split routes. Uses the same option types as Watermark.

| Route Method          | Python Type             | Notes                                             |
| --------------------- | ----------------------- | ------------------------------------------------- |
| `.stamp_source()`     | `WatermarkStampSource`  | `Text`, `Image`, or `Pdf`                         |
| `.stamp_expression()` | `str`                   | Text string or expression (when source is `Text`) |
| `.stamp_pages()`      | `str`                   | Page range (e.g. `"1-3"`)                         |
| `.stamp_options()`    | `WatermarkStampOptions` | Font, size, color, rotation, opacity, scale       |
| `.stamp_file()`       | `Path`                  | Image or PDF file to use as stamp                 |

### Rotate

[Gotenberg Documentation](https://gotenberg.dev/docs/manipulate-pdfs/rotate-pdfs)

Rotate PDF pages. Available on Chromium, LibreOffice, Merge, and Split routes.

| Route Method | Python Type   | Notes                                         |
| ------------ | ------------- | --------------------------------------------- |
| `.rotate()`  | `RotateAngle` | `Clockwise90`, `Clockwise180`, `Clockwise270` |

An optional `pages` string argument limits rotation to specific pages (e.g. `"1-3"`).

### Encrypt

[Gotenberg Documentation](https://gotenberg.dev/docs/manipulate-pdfs/encrypt-pdfs)

Password-protect the output PDF. Available on Chromium, LibreOffice, Merge, and Split routes.

| Route Method        | Python Type | Notes                        |
| ------------------- | ----------- | ---------------------------- |
| `.user_password()`  | `str`       | User (open) password         |
| `.owner_password()` | `str`       | Owner (permissions) password |

### Embeds

[Gotenberg Documentation](https://gotenberg.dev/docs/manipulate-pdfs/attachments)

Attach external files as embedded attachments inside the PDF container. Available on
Chromium, LibreOffice, Merge, and Split routes.

| Route Method     | Python Type  | Notes                                   |
| ---------------- | ------------ | --------------------------------------- |
| `.embed()`       | `Path`       | Attach a single file                    |
| `.embed_files()` | `list[Path]` | Convenience method to attach many files |
