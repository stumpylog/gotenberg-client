# Contributing

This document outlines how to contribute to the gotenberg-client project effectively.

## Questions and Support

For general questions and support, please use our
[Q&A Discussions](https://github.com/stumpylog/gotenberg-client/discussions/categories/q-a)
forum.

## Feature Requests

We use the
[Ideas category in Github Discussions](https://github.com/stumpylog/gotenberg-client/discussions/categories/ideas)
for feature requests and project improvements. Please check existing discussions before
creating a new one to avoid duplicates.

## Bug Reports

If you've identified a bug:

1. Check existing issues to avoid duplicates
2. Create a new issue using the bug report template
3. Include:
    - Python version
    - gotenberg-client version
    - Gotenberg server version
    - Minimal code example demonstrating the bug
    - Expected vs actual behavior
    - Error messages/stack traces if applicable

## Development Setup

1. Fork and clone the repository
1. Install [`uv`](https://astral.sh/uv/) for independent tool installations
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv
    ```
1. Install [`hatch`](https://github.com/pypa/hatch) and
   [`pre-commit`](https://github.com/pre-commit/pre-commit)
    ```bash
    uv tool install hatch pre-commit
    ```
1. Set up pre-commit hooks:
    ```bash
    pre-commit install
    ```

## Code Style

We use [`hatch`](https://github.com/pypa/hatch) for project management, testing, and
formatting:

- Run tests: `hatch test`
- Format & lint code: `hatch fmt`
- Check formatting: `hatch fmt --check`
- Check typing: `hatch run typing:run`
- Build documentation: `hatch run docs:build`

Please ensure all tests pass and code is properly formatted before submitting changes.
The code must pass the CI to be merged.

## Pull Request Process

1. Create a new branch from `develop`
2. Make your changes
3. Update tests and documentation
4. Run the test suite
5. Submit a PR against `develop`
6. Reference any related issues

PRs should:

- Focus on a single feature/fix
- Include tests for new functionality
- Update documentation as needed
- Follow existing code style

## License

By contributing, you agree that your contributions will be licensed under the same terms
as the project.
