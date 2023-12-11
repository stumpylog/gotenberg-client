# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
