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
    - `.index("index.html")` sets the index from an HTML file
    - `string_index(<html></html>")` sets the index as the HTML string

Optional Properties:

- Provide additional resource files as needed:
    - `.resource("file-here")` or `resources(["file1", "file2"])` adds the file or files as a resource for the HTML index
    - Add string resources with `string_resource("file content")`.

See also [common Chromium options](#chromium-common-options).

!!! note

    `string_resource` currently only supports text data, not binary data

### Markdown file(s) into PDF

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route)

Route Access: `chromium.markdown_to_pdf()`

Required Properties:

- An index file is required:
    - `.index("index.html")` sets the index from an HTML file
    - `string_index(<html></html>")` sets the index as the HTML string

Optional Properties:

- Provide additional resource files as needed:
    - `.resource("file-here")` or `resources(["file1", "file2"])` adds the file or files
      as a resource for the HTML index
    - Add string resources with `string_resource("file content")`.

See also [common Chromium options](#chromium-common-options).

!!! note

    `string_resource` currently only supports text data, not binary data

### Screenshot Routes

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#screenshots-route)

#### Common Settings

| Gotenberg Option | Route Configuration                                                                | Python Type                     | Notes |
| ---------------- | ---------------------------------------------------------------------------------- | ------------------------------- | ----- |
| width            | `.width()`                                                                         | `int`                           |       |
| height           | `height()`                                                                         | `int`                           |       |
| clip             | `clip()` or `clip_to_dimensions()` or `no_clip_to_dimensions()`                    | `bool`                          |       |
| format           | `output_format()`                                                                  | one of "png", "jpeg" or "webp". |       |
| quality          | `quality()`                                                                        | `int`, between 1 and 100        |       |
| omitBackground   | `omit_background()` or `hide_background()` or `show_background()`                  | `bool`                          |       |
| optimizeForSpeed | `image_optimize()` or `image_optimize_for_speed()` or `image_optimize_for_quality` | `bool`                          |       |

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

| Gotenberg Option                                                                                | Route Configuration                                                     | Python Type                   | Notes                                            |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------- | ------------------------------------------------ |
| `singlePage`                                                                                    | `.single_page()`                                                        | `bool`                        | Set via keyword only                             |
| <ul><li>`paperWidth`</li><li>`paperHeight`</li></ul>                                            | `.size()`                                                               | `PageSize`                    | Current only allows size configuration in inches |
| <ul><li>`marginTop`</li><li>`marginBottom`</li><li>`marginLeft`</li><li>`marginRight`</li></ul> | `.margin()`                                                             | `PageMarginsType`             |                                                  |
| `preferCssPageSize`                                                                             | <ul><li>`prefer_css_page_size()`<li>`prefer_set_page_size()`</li></ul>  | N/A                           |                                                  |
| `printBackground`                                                                               | <ul><li>`background_graphics()`<li>`no_background_graphics()`</li></ul> | N/A                           |                                                  |
| `omitBackground`                                                                                | <ul><li>`hide_background()`<li>`show_background()`</li></ul>            | N/A                           |                                                  |
| `landscape`                                                                                     | `.orient()`                                                             | `PageOrientation`             |                                                  |
| `scale`                                                                                         | `scale()`                                                               | <code>int &#124; float</code> |                                                  |
| `nativePageRanges`                                                                              | `page_ranges()`                                                         | `str`                         |                                                  |

#### Header & Footer

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#header-footer-chromium)

| Gotenberg Option | Route Configuration | Python Type | Notes |
| ---------------- | ------------------- | ----------- | ----- |
| `header.html`    | `.header()`         | `Path`      |       |
| `footer.html`    | `.footer()`         | `Path`      |       |

#### Render Control

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#wait-before-rendering-chromium)

| Gotenberg Option    | Route Configuration | Python Type                   | Notes |
| ------------------- | ------------------- | ----------------------------- | ----- |
| `waitDelay`         | `.render_wait()`    | <code>int &#124; float</code> |       |
| `waitForExpression` | `.render_expr()`    | `str`                         |       |

#### Emulated Media Type

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#emulated-media-type-chromium)

| Gotenberg Option    | Route Configuration | Python Type         | Notes |
| ------------------- | ------------------- | ------------------- | ----- |
| `emulatedMediaType` | `.media_type()`     | `EmulatedMediaType` |       |

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

#### HTTP Status Codes

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#invalid-http-status-codes-chromium)

| Gotenberg Option        | Route Configuration       | Python Type     | Notes |
| ----------------------- | ------------------------- | --------------- | ----- |
| `failOnHttpStatusCodes` | `.fail_on_status_codes()` | `Iterable[int]` |       |

#### Network Errors

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#network-errors-chromium)

| Gotenberg Option              | Route Configuration               | Python Type | Notes |
| ----------------------------- | --------------------------------- | ----------- | ----- |
| `failOnResourceLoadingFailed` | `fail_on_resource_loading_failed` | `bool`      |       |

#### Console Exceptions

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#console-exceptions-chromium)

| Gotenberg Option          | Route Configuration                                                     | Python Type | Notes |
| ------------------------- | ----------------------------------------------------------------------- | ----------- | ----- |
| `failOnConsoleExceptions` | <ul><li>`fail_on_exceptions()`<li>`dont_fail_on_exceptions()`</li></ul> | N/A         |       |

#### Performance Mode

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#performance-mode-chromium)

| Gotenberg Option       | Route Configuration                                             | Python Type | Notes |
| ---------------------- | --------------------------------------------------------------- | ----------- | ----- |
| `skipNetworkIdleEvent` | <ul><li>`skip_network_idle()`<li>`use_network_idle()`</li></ul> | N/A         |       |

#### Split

[Gotenberg Documentation Link](https://gotenberg.dev/docs/routes#performance-mode-chromium)

| Gotenberg Option | Route Configuration | Python Type                 | Notes |
| ---------------- | ------------------- | --------------------------- | ----- |
| splitMode        | `.split_mode()`     | one of "pages", "intervals" |       |
| splitSpan        | `split_span()`      | `str`                       |       |
| splitUnify       | `split_unify()`     | `bool`                      |       |

#### PDF/A & PDF/UA

| Gotenberg Option | Route Configuration                                                           | Python Type  | Notes |
| ---------------- | ----------------------------------------------------------------------------- | ------------ | ----- |
| `pdfa`           | `.pdf_format()`                                                               | `PdfAFormat` |       |
| `pdfua`          | <ul><li>`enable_universal_access()`<li>`disable_universal_access()`</li></ul> | N/A          |       |

#### PDF Metadata Support

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#metadata-chromium)

Add metadata to your PDFs:

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
                creation_date=datetime.now(),
                keywords=["sample", "document"],
                subject="Sample PDF Generation",
                trapped="Unknown"
            )
            .run())
```

Supported metadata fields:

- `title`: Document title
- `author`: Document author
- `subject`: Document subject
- `keywords`: List of keywords
- `creator`: Creating application
- `creation_date`: Creation datetime
- `modification_date`: Last modification datetime
- `producer`: PDF producer
- `trapped`: Trapping status ('True', 'False', 'Unknown')
- `copyright`: Copyright information
- `marked`: PDF marked status
- `pdf_version`: PDF version number

!!! note
Some fields cannot be set or will be overwritten, depending on Gotenberg and its utilized PDF engine

## LibreOffice

### Office Documents to PDF

| Gotenberg Link                                                                      | Route Access          | Required Properties                                                                            | Optional Properties                                       |
| ----------------------------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| [Documentation](https://gotenberg.dev/docs/routes#office-documents-into-pdfs-route) | `libre_office.to_pdf` | <ul><li>`.convert("mydoc.docx")`</li><li>or</li><li>`.convert_files(["mydoc.docx"])`</li></ul> | See [common LibreOffice options](#libreoffice-properties) |

!!! note
`convert` may be called multiple times" !!! note "`convert_files` is a convenience method to convert a list of file into PDF

### LibreOffice Properties

#### Page Properties

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#page-properties-libreoffice)

| Gotenberg Option   | Route Configuration | Python Type       | Notes                              |
| ------------------ | ------------------- | ----------------- | ---------------------------------- |
| `landscape`        | `.orient()`         | `PageOrientation` |                                    |
| `nativePageRanges` | `page_ranges()`     | `str`             |                                    |
| `exportFormFields` | N/A                 | N/A               | This option is not implemented yet |
| `singlePageSheets` | N/A                 | N/A               | This option is not implemented yet |

#### Compress

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#compress-libreoffice)

#### Merge

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#merge-libreoffice)

| Gotenberg Option | Route Configuration                         | Python Type | Notes |
| ---------------- | ------------------------------------------- | ----------- | ----- |
| `merge`          | <ul><li>`merge()`<li>`no_merge()`</li></ul> | N/A         |       |

!!! note
If multiple files are provided, and the merge is left as default or `no_merge()` is called, the resulting file will be a zip

#### Split

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#split-libreoffice)

#### PDF/A & PDF/UA

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#pdfa-libreoffice)

| Gotenberg Option | Route Configuration                                                           | Python Type  | Notes |
| ---------------- | ----------------------------------------------------------------------------- | ------------ | ----- |
| `pdfa`           | `.pdf_format()`                                                               | `PdfAFormat` |       |
| `pdfua`          | <ul><li>`enable_universal_access()`<li>`disable_universal_access()`</li></ul> | N/A          |       |

#### Metadata

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#metadata-libreoffice)

See [PDF Metadata Support](#pdf-metadata-support) for the API interface.

#### Flatten

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#flatten-libreoffice)

## Convert into PDF/A & PDF/UA

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route)

| Gotenberg Link | Route Access                                                                  | Required Properties | Optional Properties |
| -------------- | ----------------------------------------------------------------------------- | ------------------- | ------------------- |
| `pdfa`         | `.pdf_format()`                                                               | `PdfAFormat`        |                     |
| `pdfua`        | <ul><li>`enable_universal_access()`<li>`disable_universal_access()`</li></ul> | N/A                 |                     |

!!! note
At least one of `pdf_format()`, `enable_universal_access()` or `disable_universal_access()` must be set

## Read PDF metadata

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#read-pdf-metadata-route)

## Write PDF metadata

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#write-pdf-metadata-route)

## Merge PDFs

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#merge-pdfs-route)

| Gotenberg Link | Route Access                                                                  | Required Properties | Optional Properties                                                      |
| -------------- | ----------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------ |
| `pdfa`         | `.pdf_format()`                                                               | `PdfAFormat`        |                                                                          |
| `pdfua`        | <ul><li>`enable_universal_access()`<li>`disable_universal_access()`</li></ul> | N/A                 |                                                                          |
| `metadata`     | N/A                                                                           | N/A                 | See [PDF Metadata Support](#pdf-metadata-support) for the API interface. |

!!! note
Prefixes will be added to the file to ensure they are merged in the order provided to `merge()`, even with multiple calls

## Split PDFs

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#merge-pdfs-route)

## Flatten PDFs

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#merge-pdfs-route)

## Health Check

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#health-check-route)

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

### Output Filename

### Download From

!!! warning
This feature is not implemented
