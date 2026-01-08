# Gotenberg Client TODO

---

## Priority Legend

- **[CRITICAL]** - Bugs or issues that could cause incorrect behavior
- **[HIGH]** - Important improvements or missing features users may need
- **[MEDIUM]** - Nice-to-have improvements
- **[LOW]** - Minor issues, cleanup, or future considerations

---

## MISSING ROUTES

### [HIGH] Version Route Not Implemented

**Location:** `src/gotenberg_client/client/base.py`

The `version` property raises `NotImplementedError`. The route is simple:

- Endpoint: `GET /version`
- Returns: Plain text version string (e.g., "8.25.1")

**Implementation needed:**

- Create `_version/routes.py` with sync/async route classes
- Return a simple string response (not PDF)

### [MEDIUM] Encrypt Route (Standalone PDF Engines)

**Location:** Not implemented

Gotenberg provides a standalone encrypt route:

- Endpoint: `POST /forms/pdfengines/encrypt`
- Required: `files` (PDF files), `userPassword`
- Optional: `ownerPassword`

Currently, encryption is only available as options on other routes (Chromium, LibreOffice), not as a standalone operation.

### [MEDIUM] Embed Files Route (Standalone PDF Engines)

**Location:** Not implemented

Gotenberg provides a standalone embed route:

- Endpoint: `POST /forms/pdfengines/embed`
- Required: `files` (PDFs to embed into), `embeds` (files to embed)

This is useful for ZUGFeRD/Factur-X invoice embedding. Currently not implemented as standalone.

### [LOW] Debug Route

**Location:** Not implemented

- Endpoint: `GET /debug`
- Only available if `--api-enable-debug-route` is set
- Returns debug information

Low priority as it requires server-side configuration.

### [LOW] Prometheus Metrics Route

**Location:** Not implemented

- Endpoint: `GET /prometheus/metrics`
- Returns Prometheus-format metrics

Low priority, specialized use case.

---

## MISSING FEATURES/OPTIONS

### [HIGH] Embed Files Support on Conversion Routes

**Gotenberg Docs:** All Chromium and LibreOffice routes accept an `embeds` form field

The `embeds` form field allows embedding files (like XML invoices) into generated PDFs. This is not currently implemented as a mixin.

**Routes affected:**

- All Chromium conversion routes
- LibreOffice conversion route
- Merge route
- Split route

**Implementation:** Create an `EmbedFilesMixin` class.

### [HIGH] Encrypt Options on Chromium Routes

**Gotenberg Docs:** Chromium routes accept `userPassword` and `ownerPassword`

The encryption options (`userPassword`, `ownerPassword`) are documented for Chromium routes but not implemented in the Chromium mixins.

**Implementation:** Create an `EncryptMixin` class and add to Chromium route inheritance.

### [HIGH] Download From Feature

**Gotenberg Docs:** All multipart/form-data endpoints accept `downloadFrom`

The `downloadFrom` form field allows Gotenberg to fetch files from URLs instead of requiring file uploads. This is useful for:

- Large files
- Files already hosted elsewhere
- Reduced upload bandwidth

**Structure:**

```json
[
    {
        "url": "http://url/to/file.com",
        "extraHttpHeaders": { "X-Header": "value" },
        "embedded": false
    }
]
```

### [MEDIUM] Flatten Option on Chromium Routes

**Gotenberg Docs:** Chromium routes accept the `flatten` form field

The flatten option is implemented for LibreOffice and PDFEngines routes but not for Chromium conversion routes.

### [MEDIUM] Resource Status Code Filtering (Chromium)

**Gotenberg Docs:** `failOnResourceHttpStatusCodes` form field

Currently only `failOnHttpStatusCodes` (for main page) is implemented via `InvalidStatusCodesMixin`. The docs also mention `failOnResourceHttpStatusCodes` for loaded resources.

### [MEDIUM] String-based Header/Footer for Chromium

**Location:** `src/gotenberg_client/_chromium/mixins.py`

The `HeaderFooterMixin` only accepts `Path` objects. Consider adding methods for in-memory HTML strings:

- `string_header(html: str) -> Self`
- `string_footer(html: str) -> Self`

### [LOW] Reset Form Fields on Start Options (Chromium)

**Gotenberg Docs:** `resetFormFieldsOnPdfStart` and `resetFormFieldsOnPdfEnd`

These boolean options are not implemented.

---

## CODE QUALITY IMPROVEMENTS

### [MEDIUM] Consolidate Common Mixins

Several mixins are duplicated or could be shared more effectively:

1. **EncryptMixin** - `userPassword`/`ownerPassword` appears on multiple routes
2. **EmbedsMixin** - `embeds` field appears on multiple routes
3. **FlattenMixin** - exists but not used on all applicable routes

### [MEDIUM] Type Annotations Improvements

**Location:** Various files

Some areas could benefit from stricter typing:

- Use `Final` more consistently for class constants
- Consider using `TypedDict` for complex dictionary structures (cookies, downloadFrom)
- Replace `dict[str, str]` with more specific types where applicable

### [MEDIUM] Consistent Mixin Naming

Current pattern is inconsistent:

- `PdfFormatMixin` vs `PfdUniversalAccessMixin` (typo: "Pfd" should be "Pdf")
- Some use "Mixin" suffix, class naming is generally good otherwise

**Fix:** Rename `PfdUniversalAccessMixin` to `PdfUniversalAccessMixin` (breaking change).

### [LOW] ExitStack Usage Review

**Location:** `src/gotenberg_client/_base/routes.py`

The `ExitStack` is created but its usage pattern could be documented better. It appears to be for managing file handles opened during request preparation.

### [LOW] Logging Consistency

Some modules create their own loggers (`logger = logging.getLogger(__name__)`), while routes use a passed-in logger. Consider standardizing.

---

## DOCUMENTATION IMPROVEMENTS

### [MEDIUM] Add Usage Examples in Docstrings

Many mixins have good docstrings but lack concrete usage examples. For example:

```python
def cookies(self, cookies: list[CookieJar]) -> Self:
    """
    Sets cookies for the rendering process.

    Example:
        route.cookies([
            CookieJar("session", "abc123", "example.com", path="/", secure=True)
        ])
    """
```

### [LOW] Document Gotenberg Version Compatibility

Add a compatibility matrix or note about which Gotenberg server versions are supported/tested.

### [LOW] Constants Module Expansion

**Location:** `src/gotenberg_client/constants.py`

The constants module has paper sizes but could also include:

- Common margin presets (no margins, standard margins)
- Common cookie configurations

---

## TESTING IMPROVEMENTS

### [MEDIUM] Add Unit Tests for Options Classes

**Location:** `tests/`

The `options.py` module (PageSize, Measurement, CookieJar, etc.) would benefit from dedicated unit tests:

- Test `to_form()` methods produce correct output
- Test edge cases (zero values, None handling)
- Test measurement unit formatting

### [MEDIUM] Mock Tests for Missing Routes

Add mock-based tests for features that can't be tested against a live server:

- `downloadFrom` functionality
- Webhook configurations
- Error scenarios

---

## DEPRECATIONS TO TRACK

### Gotenberg 8.11.0 Change

**Note:** Prior to Gotenberg 8.11.0, `skipNetworkIdleEvent` defaulted to `false`. The client's `PerformanceModeMixin` should document this version-specific behavior.

### PDF/A-1a Deprecation

The `PdfAFormat.A1a` is marked deprecated. Consider:

- Adding a note about when it will be removed
- Updating users to use `A1b` (once implemented)

---

## FUTURE CONSIDERATIONS

### [LOW] WebSocket Support

Gotenberg may add WebSocket support in future versions for long-running operations. The client architecture should be evaluated if this happens.

### [LOW] Streaming Response Support

For large PDF generation, streaming responses could reduce memory usage. Current implementation loads entire response into memory.

### [LOW] Connection Pooling Documentation

Document how `httpx` connection pooling works with the client, especially for high-throughput use cases.

---
