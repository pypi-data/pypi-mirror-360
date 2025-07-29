Development Guide
=================

This guide covers development setup, testing, and contributing to ``ign``.

Development Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.10 or higher
- ``uv`` (recommended) or ``pip``
- Git

Getting Started
~~~~~~~~~~~~~~~

1. **Clone the repository**::

       git clone https://github.com/astralblue/ign.git
       cd ign

2. **Set up development environment**::

       uv sync

   This installs all dependencies including development tools.

3. **Verify installation**::

       python -m ign --version

Project Structure
-----------------

::

    ign/
    ├── ign/                 # Main package
    │   ├── __init__.py       # Main module and CLI entry point
    │   ├── __main__.py       # Module execution entry point
    │   ├── _logging.py       # Structured logging utilities
    │   ├── consts.py         # Constants and configuration
    │   ├── net.py            # Network operations and GitHub API
    │   └── utils.py          # Utility functions and classes
    ├── docs/                 # Sphinx documentation
    ├── tests/                # Test suite (when created)
    ├── pyproject.toml        # Project configuration
    ├── uv.lock              # Dependency lock file
    ├── README.rst           # Project documentation
    └── CLAUDE.md            # AI assistant context

Development Workflow
--------------------

Code Style
~~~~~~~~~~

The project follows these style guidelines:

- **Primary tool**: Ruff (handles formatting, linting, and import sorting)
- **Legacy tool**: Black (still available but prefer Ruff)
- **Line length**: 88 characters (Ruff default, compatible with Black)

Format and lint code before committing::

    ruff format .
    ruff check --fix .

Or use legacy tool if needed::

    black .

Testing
~~~~~~~

Run the test suite::

    pytest

Run tests with coverage::

    pytest --cov=ign --cov-report=html

The coverage report will be generated in ``htmlcov/``.

Testing specific modules::

    pytest tests/test_net.py
    pytest tests/test_net.py::test_get_template

Documentation
~~~~~~~~~~~~~

Build documentation locally::

    cd docs
    make html

View the built documentation::

    open _build/html/index.html

Clean documentation build::

    make clean

Architecture
------------

Core Components
~~~~~~~~~~~~~~~

**Main Module (``ign/__init__.py``)**
    - CLI argument parsing
    - Main orchestration logic
    - Template marker processing
    - Diff application and merging

**Network Module (``ign/net.py``)**
    - HTTP client management
    - GitHub API integration
    - Template fetching
    - SHA resolution

**Logging Module (``ign/_logging.py``)**
    - Structured logging adapter
    - Multiple output formats
    - Context binding

Key Algorithms
~~~~~~~~~~~~~~

**Template Marker Processing**
    Uses a state machine to process BEGIN/END marker pairs:

    1. Parse input line by line
    2. Detect marker comments with regex
    3. Track current template state
    4. Validate marker consistency
    5. Extract local modifications

**Merge Strategy**
    Implements two-strategy diff application:

    1. **Strategy A**: Apply (new - old) to local
    2. **Strategy B**: Apply (local - old) to new
    3. Compare results and choose best option
    4. Fall back gracefully on conflicts

**HTTP Client Management**
    Uses context variables for async client reuse:

    1. Check for existing client in context
    2. Create new client if needed
    3. Share client across async operations
    4. Properly clean up resources

Adding Features
---------------

Adding New Commands
~~~~~~~~~~~~~~~~~~~

1. **Add argument parsing**::

       # In _build_argparser()
       parser.add_argument(
           "--new-option",
           action="store_true",
           help="Description of new option"
       )

2. **Implement logic**::

       # In async_main()
       if args.new_option:
           await handle_new_option()

3. **Add tests**::

       # In tests/test_main.py
       def test_new_option():
           # Test implementation

Adding New Template Sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Extend constants**::

       # In consts.py
       ALTERNATIVE_REPO = "alternative/gitignore"

2. **Update network module**::

       # In net.py
       async def get_template_from_source(source: str, name: str):
           # Implementation

3. **Add CLI support**::

       # In argument parser
       parser.add_argument(
           "--source",
           choices=["github", "alternative"],
           default="github"
       )

Testing Guidelines
------------------

Test Organization
~~~~~~~~~~~~~~~~~

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test full CLI workflows
- **Mock external dependencies**: Use ``httpx_mock`` for HTTP requests

Writing Tests
~~~~~~~~~~~~~

Example test structure::

    import pytest
    from unittest.mock import AsyncMock, patch
    
    from ign.net import get_template
    
    
    @pytest.mark.asyncio
    async def test_get_template():
        """Test template fetching."""
        with patch("ign.net.httpx_client") as mock_client:
            mock_response = AsyncMock()
            mock_response.text = "# Test template\n*.pyc\n"
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            lines, sha = await get_template("Python")
            
            assert "# Test template\n" in lines
            assert len(sha) == 40  # SHA length

Test Fixtures
~~~~~~~~~~~~~

Create reusable test fixtures::

    @pytest.fixture
    def sample_gitignore():
        """Sample .gitignore content."""
        return [
            "# Local files\n",
            "*.local\n",
            "# --- BEGIN https://raw.githubusercontent.com/.../Python.gitignore ---\n",
            "*.pyc\n",
            "__pycache__/\n",
            "# --- END https://raw.githubusercontent.com/.../Python.gitignore ---\n",
        ]

Contributing
------------

Getting Started
~~~~~~~~~~~~~~~

1. **Fork the repository** on GitHub
2. **Create a feature branch**::

       git checkout -b feature/new-feature

3. **Make your changes** following the development workflow
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Run the full test suite**::

       pytest
       ruff format .
       ruff check --fix .

7. **Commit your changes**::

       git commit -m "Add new feature: description"

8. **Push to your fork**::

       git push origin feature/new-feature

9. **Create a pull request** on GitHub

Code Review Process
~~~~~~~~~~~~~~~~~~~

All contributions go through code review:

1. **Automated checks**: CI runs tests and linting
2. **Manual review**: Maintainers review code quality and design
3. **Feedback**: Address any comments or suggestions
4. **Merge**: Once approved, changes are merged

Pull Request Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

- **Clear description**: Explain what the PR does and why
- **Reference issues**: Link to related GitHub issues
- **Small, focused changes**: Keep PRs manageable
- **Tests included**: Add tests for new functionality
- **Documentation updated**: Update docs for user-facing changes

Release Process
---------------

Versioning
~~~~~~~~~~

The project uses semantic versioning:

- **Major**: Breaking changes
- **Minor**: New features, backwards compatible
- **Patch**: Bug fixes, backwards compatible

Release Steps
~~~~~~~~~~~~~

1. **Update version** in ``ign/__init__.py``
2. **Update changelog** with new features and fixes
3. **Run full test suite** to ensure quality
4. **Create release commit**::

       git commit -m "Release version X.Y.Z"

5. **Tag the release**::

       git tag -a vX.Y.Z -m "Release version X.Y.Z"

6. **Push to GitHub**::

       git push origin main --tags

7. **Build and publish** to PyPI::

       flit build
       flit publish

Getting Help
------------

If you need help with development:

1. **Check the documentation** for existing guidance
2. **Look at existing code** for patterns and examples
3. **Ask questions** in GitHub discussions
4. **Report bugs** in GitHub issues
5. **Join the community** and contribute to discussions

Resources
---------

- **GitHub Repository**: https://github.com/astralblue/ign
- **Issue Tracker**: https://github.com/astralblue/ign/issues
- **Documentation**: https://ign.readthedocs.io/
- **PyPI Package**: https://pypi.org/project/ign/
- **Template Source**: https://github.com/github/gitignore