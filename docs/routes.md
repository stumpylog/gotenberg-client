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

| Gotenberg Option                                                                                | Route Configuration                                                     | Python Type                   | Notes                                              |
| ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------- | -------------------------------------------------- |
| `singlePage`                                                                                    | `.single_page()`                                                        | `bool`                        | Set via keyword only                               |
| <ul><li>`paperWidth`</li><li>`paperHeight`</li></ul>                                            | `.size()`                                                               | `PageSize`                    | Current only allows size configuration in inches   |
| <ul><li>`marginTop`</li><li>`marginBottom`</li><li>`marginLeft`</li><li>`marginRight`</li></ul> | `.margin()`                                                             | `Margin`                      | Current only allows margin configuration in inches |
| `preferCssPageSize`                                                                             | <ul><li>`prefer_css_page_size()`<li>`prefer_set_page_size()`</li></ul>  | N/A                           |                                                    |
| `printBackground`                                                                               | <ul><li>`background_graphics()`<li>`no_background_graphics()`</li></ul> | N/A                           |                                                    |
| `omitBackground`                                                                                | <ul><li>`hide_background()`<li>`show_background()`</li></ul>            | N/A                           |                                                    |
| `landscape`                                                                                     | `.orient()`                                                             | `PageOrientation`             |                                                    |
| `scale`                                                                                         | `scale()`                                                               | <code>int &#124; float</code> |                                                    |
| `nativePageRanges`                                                                              | `page_ranges()`                                                         | `str`                         |                                                    |

#### Header & Footer

#### Render Control

#### Emulated Media Type

#### Cookies

These options are not yet implemented

#### Custom HTTP Headers

#### HTTP Status Codes

#### Console Exceptions

#### Performance Mode

#### PDF/A & PDF/UA

#### Metadata

These options are not yet implemented

## LibreOffice

## Convert

## Merge

## Health Check
