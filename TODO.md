# Gotenberg Client TODO

---

## Priority Legend

- **[CRITICAL]** - Bugs or issues that could cause incorrect behavior
- **[HIGH]** - Important improvements or missing features users may need
- **[MEDIUM]** - Nice-to-have improvements
- **[LOW]** - Minor issues, cleanup, or future considerations

---

## MISSING ROUTES

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

### [LOW] Reset Form Fields on Start Options (Chromium)

**Gotenberg Docs:** `resetFormFieldsOnPdfStart` and `resetFormFieldsOnPdfEnd`

These boolean options are not implemented.

---

## CODE QUALITY IMPROVEMENTS

### [MEDIUM] Logging Consistency

**Location:** `src/gotenberg_client/_libreoffice/mixins.py`

Routes receive a logger via constructor (passed from the client's `logging.getLogger("gotenberg-client")`), but `_libreoffice/mixins.py` creates its own module-level logger with `logging.getLogger(__name__)`. This breaks the established pattern.

### [MEDIUM] Type Annotations Improvements

**Location:** `src/gotenberg_client/options.py`

`CookieJar.asdict()` returns `dict[str, str | bool]` and `DownloadFromUrl.asdict()` returns `dict[str, str | bool | dict[str, str]]` without `TypedDict` definitions. These would benefit from stricter typing.

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

### [MEDIUM] Document skipNetworkIdleEvent Version Behavior

**Location:** `src/gotenberg_client/_chromium/mixins.py` - `PerformanceModeMixin`

Prior to Gotenberg 8.11.0, `skipNetworkIdleEvent` defaulted to `false`. The `PerformanceModeMixin` docstring should document this version-specific behavior.

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

- Webhook configurations
- Error scenarios

---

## FUTURE CONSIDERATIONS

### [LOW] WebSocket Support

Gotenberg may add WebSocket support in future versions for long-running operations. The client architecture should be evaluated if this happens.

### [LOW] Streaming Response Support

For large PDF generation, streaming responses could reduce memory usage. Current implementation loads entire response into memory.

### [LOW] Connection Pooling Documentation

Document how `httpx` connection pooling works with the client, especially for high-throughput use cases.

---
