# Implemented Routes

## Chromium

Access to the Chromium module of Gotenberg, as documented [here](https://gotenberg.dev/docs/routes#convert-with-chromium).

### URL into PDF

| Gotenberg Link                                                        | Route Access          | Required Properties                               | Optional Properties                                     |
| --------------------------------------------------------------------- | --------------------- | ------------------------------------------------- | ------------------------------------------------------- |
| [Documentation](https://gotenberg.dev/docs/routes#url-into-pdf-route) | `chromium.url_to_pdf` | <ul><li>`.url("http://localhost:8888")`</li></ul> | See [common Chromium options](#chromium-common-options) |

### HTML file into PDF

| Gotenberg Link                                                              | Route Access           | Required Properties                      | Optional Properties                                                                                                                     |
| --------------------------------------------------------------------------- | ---------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| [Documentation](https://gotenberg.dev/docs/routes#html-file-into-pdf-route) | `chromium.html_to_pdf` | <ul><li>`.index("index.html")`</li></ul> | <ul><li>Add extra files by chaining `.resource("file-here")`</li><li> See [common Chromium options](#chromium-common-options)</li></ul> |

### Markdown file(s) into PDF

| Gotenberg Link                                                                   | Route Access               | Required Properties                                                                   | Optional Properties                                                                                                                     |
| -------------------------------------------------------------------------------- | -------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| [Documentation](https://gotenberg.dev/docs/routes#markdown-files-into-pdf-route) | `chromium.markdown_to_pdf` | <ul><li>`.index("index.html")`</li><li>`.markdown_file` or `markdown_files`</li></ul> | <ul><li>Add extra files by chaining `.resource("file-here")`</li><li> See [common Chromium options](#chromium-common-options)</li></ul> |

### Screenshots

### Chromium Common Options

#### Page Properties

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

| Gotenberg Option | Route Configuration | Python Type | Notes |
| ---------------- | ------------------- | ----------- | ----- |
| `header.html`    | `.header()`         | `Path`      |       |
| `footer.html`    | `.footer()`         | `Path`      |       |

#### Render Control

| Gotenberg Option    | Route Configuration | Python Type                   | Notes |
| ------------------- | ------------------- | ----------------------------- | ----- |
| `waitDelay`         | `.render_wait()`    | <code>int &#124; float</code> |       |
| `waitForExpression` | `.render_expr()`    | `str`                         |       |

#### Emulated Media Type

| Gotenberg Option    | Route Configuration | Python Type         | Notes |
| ------------------- | ------------------- | ------------------- | ----- |
| `emulatedMediaType` | `.media_type()`     | `EmulatedMediaType` |       |

#### Cookies

These options are not yet implemented

#### Custom HTTP Headers

| Gotenberg Option   | Route Configuration | Python Type      | Notes                                                 |
| ------------------ | ------------------- | ---------------- | ----------------------------------------------------- |
| `extraHttpHeaders` | `.headers()`        | `dict[str, str]` | The dictionary of values will be JSON encoded for you |

#### HTTP Status Codes

| Gotenberg Option        | Route Configuration       | Python Type     | Notes |
| ----------------------- | ------------------------- | --------------- | ----- |
| `failOnHttpStatusCodes` | `.fail_on_status_codes()` | `Iterable[int]` |       |

#### Console Exceptions

| Gotenberg Option          | Route Configuration                                                     | Python Type | Notes |
| ------------------------- | ----------------------------------------------------------------------- | ----------- | ----- |
| `failOnConsoleExceptions` | <ul><li>`fail_on_exceptions()`<li>`dont_fail_on_exceptions()`</li></ul> | N/A         |       |

#### Performance Mode

| Gotenberg Option       | Route Configuration                                             | Python Type | Notes |
| ---------------------- | --------------------------------------------------------------- | ----------- | ----- |
| `skipNetworkIdleEvent` | <ul><li>`skip_network_idle()`<li>`use_network_idle()`</li></ul> | N/A         |       |

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

## LibreOffice

### Office Documents to PDF

| Gotenberg Link                                                                      | Route Access          | Required Properties                                                                            | Optional Properties                                       |
| ----------------------------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| [Documentation](https://gotenberg.dev/docs/routes#office-documents-into-pdfs-route) | `libre_office.to_pdf` | <ul><li>`.convert("mydoc.docx")`</li><li>or</li><li>`.convert_files(["mydoc.docx"])`</li></ul> | See [common LibreOffice options](#libreoffice-properties) |

Additional Notes:

- `convert` may be called multiple times
- `convert_files` is a convenience method to convert a list of file into PDF

### LibreOffice Properties

#### Page Properties

| Gotenberg Option   | Route Configuration | Python Type       | Notes                              |
| ------------------ | ------------------- | ----------------- | ---------------------------------- |
| `landscape`        | `.orient()`         | `PageOrientation` |                                    |
| `nativePageRanges` | `page_ranges()`     | `str`             |                                    |
| `exportFormFields` | N/A                 | N/A               | This option is not implemented yet |
| `singlePageSheets` | N/A                 | N/A               | This option is not implemented yet |

#### Merge

| Gotenberg Option | Route Configuration                         | Python Type | Notes |
| ---------------- | ------------------------------------------- | ----------- | ----- |
| `merge`          | <ul><li>`merge()`<li>`no_merge()`</li></ul> | N/A         |       |

Additional Notes:

- If multiple files are provided, and the merge is left as default or `no_merge()` is called, the resulting file will be a zip

#### PDF/A & PDF/UA

| Gotenberg Option | Route Configuration                                                           | Python Type  | Notes |
| ---------------- | ----------------------------------------------------------------------------- | ------------ | ----- |
| `pdfa`           | `.pdf_format()`                                                               | `PdfAFormat` |       |
| `pdfua`          | <ul><li>`enable_universal_access()`<li>`disable_universal_access()`</li></ul> | N/A          |       |

#### Metadata

[Gotenberg Documentation](https://gotenberg.dev/docs/routes#metadata-libreoffice)

These options are not yet implemented

## Convert

| Gotenberg Link                                                                    | Route Access                                                                  | Required Properties                                                                          | Optional Properties |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------- |
| [Documentation](https://gotenberg.dev/docs/routes#convert-into-pdfa--pdfua-route) | `pdf_a.to_pdfa`                                                               | <ul><li>`.convert("mydoc.pdf")`</li><li>or</li><li>`.convert_files(["mydoc.pdf"])`</li></ul> |                     |
| `pdfa`                                                                            | `.pdf_format()`                                                               | `PdfAFormat`                                                                                 |                     |
| `pdfua`                                                                           | <ul><li>`enable_universal_access()`<li>`disable_universal_access()`</li></ul> | N/A                                                                                          |                     |

Additional Notes:

- At least one of `pdf_format()`, `enable_universal_access()` or `disable_universal_access()` must be set

## Merge

| Gotenberg Link                                                      | Route Access                                                                  | Required Properties                                    | Optional Properties                |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------- |
| [Documentation](https://gotenberg.dev/docs/routes#merge-pdfs-route) | `merge.merge`                                                                 | <ul><li>`.merge(["file1.pdf", "file2.pdf"])`</li></ul> |                                    |
| `pdfa`                                                              | `.pdf_format()`                                                               | `PdfAFormat`                                           |                                    |
| `pdfua`                                                             | <ul><li>`enable_universal_access()`<li>`disable_universal_access()`</li></ul> | N/A                                                    |                                    |
| `metadata`                                                          | N/A                                                                           | N/A                                                    | This option is not implemented yet |

Additional Notes:

- The library will add prefixes to the file to ensure they are merged in the order provided to `merge()`

## Health Check
