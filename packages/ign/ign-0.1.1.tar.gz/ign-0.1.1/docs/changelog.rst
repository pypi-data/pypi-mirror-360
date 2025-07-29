Changelog
=========

This document records all notable changes to the ``ign`` project.

The format is based on `Keep a Changelog`_ and this project adheres to
`Semantic Versioning`_.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

Unreleased
----------

Added
~~~~~

- None yet

Changed
~~~~~~~

- None yet

Fixed
~~~~~

- None yet

Removed
~~~~~~~

- None yet

0.1.1 - 2025-07-06
------------------

Added
~~~~~

- Template caching for improved performance using ``async-lru``
- Quiet mode (``-q``/``--quiet``) for minimal output
- Auto-detection of TTY for default logging format

Changed
~~~~~~~

- Default log level changed from WARNING to INFO for better user experience
- Verbose flag (``-v``/``--verbose``) now enables DEBUG logging specifically for ign
- Debug flag (``--debug``) now enables DEBUG logging for all libraries
- JSON logging is now default when stderr is not a TTY
- Improved logging messages with better categorization
- Consolidated code quality tools to use only Ruff (removed Black dependency)
- Moved development dependencies to PEP 735 dependency groups

Fixed
~~~~~

- Double logging issue when using ``-v`` and ``-d`` flags together
- Improved progress reporting and template update notifications

Removed
~~~~~~~

- Black formatter dependency (replaced entirely by Ruff)

Performance
~~~~~~~~~~~

- Added LRU caching for template fetching to reduce redundant HTTP requests

0.1.0 - 2025-07-06
-----------

Added
~~~~~

- Initial release of ``ign``
- Core functionality for .gitignore template management
- Template synchronization from GitHub's gitignore repository
- Support for local modifications preservation
- Dual merge strategy implementation
- Command-line interface with comprehensive options
- Auto-detection of existing templates
- Dry-run and diff preview capabilities
- Environment variable configuration
- Comprehensive error handling
- Structured logging system
- GitHub API integration for template fetching
- Intelligent merge strategies for local modifications
- Support for template version pinning
- Structured logging with multiple output formats
- Comprehensive documentation with Sphinx
- Development tools and workflows
- Converted README from Markdown to reStructuredText format

Features
~~~~~~~~

**Template Management**
    - Fetch templates from GitHub's official gitignore repository
    - Automatic version detection and updates
    - Preserve local modifications during updates
    - Support for multiple templates in single file

**Merge Strategies**
    - Strategy A: Apply upstream changes to local modifications
    - Strategy B: Apply local changes to new upstream version
    - Automatic conflict resolution with graceful fallbacks

**Command Line Interface**
    - Flexible input/output options (files, stdin/stdout)
    - Template version pinning with commit hashes
    - Preview mode with unified diff output
    - Verbose and debug logging options

**Developer Experience**
    - Structured logging with context binding
    - Rich console output with colors and formatting
    - JSON logging for automated processing
    - Comprehensive error messages and debugging

**Integration**
    - GitHub API integration with token support
    - Environment variable configuration
    - Shell-friendly exit codes
    - Pipe-friendly input/output handling

Technical Details
~~~~~~~~~~~~~~~~~

**Dependencies**
    - Python 3.10+ required
    - async-lru for caching
    - httpx for HTTP client
    - PyGithub for GitHub API
    - patch-ng for diff application
    - rich for console formatting
    - python-json-logger for structured logging

**Architecture**
    - Async/await throughout for better performance
    - Context variable-based HTTP client management
    - Regular expression-based marker parsing
    - Diff/patch-based merge algorithms
    - Structured logging with bound context

**Testing**
    - pytest for test framework
    - Full test coverage of core functionality
    - Mock-based testing for external dependencies
    - Integration tests for end-to-end workflows

**Documentation**
    - Sphinx-based documentation
    - Comprehensive API reference
    - Usage examples and tutorials
    - Development guide for contributors

Contributors
~~~~~~~~~~~~

- Eugene Kim (@astralblue) - Initial development and architecture

Special thanks to the GitHub team for maintaining the official gitignore
template repository that makes this tool possible.