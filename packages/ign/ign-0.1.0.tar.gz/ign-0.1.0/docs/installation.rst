Installation
============

System Requirements
-------------------

- Python 3.10 or higher
- Internet connection for fetching templates from GitHub

Package Installation
--------------------

Using uv (recommended)
~~~~~~~~~~~~~~~~~~~~~~

``uv`` is the modern Python package manager and is the recommended way to install ``ign``::

    uv add ign

For development work::

    uv add --dev ign

Using pip
~~~~~~~~~

Install from PyPI::

    pip install ign

Install from source::

    git clone https://github.com/astralblue/ign.git
    cd ign
    pip install -e .

Development Installation
------------------------

For development, clone the repository and install in development mode::

    git clone https://github.com/astralblue/ign.git
    cd ign
    uv sync

This will install all dependencies including development tools.

Verification
------------

Verify your installation::

    ign --version

You should see the version number printed.

Optional Dependencies
---------------------

GitHub API Token
~~~~~~~~~~~~~~~~

While not required, setting a GitHub API token will increase your rate limits::

    export GITHUB_API_TOKEN=ghp_your_token_here

Or create a ``.env`` file in your project directory::

    GITHUB_API_TOKEN=ghp_your_token_here

To generate a token:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select appropriate scopes (public_repo is sufficient)
4. Copy the token and set it as an environment variable

Troubleshooting Installation
----------------------------

Common Issues
~~~~~~~~~~~~~

**Python version mismatch**
    Ensure you're using Python 3.10 or higher::

        python --version

**Permission errors**
    Use ``--user`` flag with pip::

        pip install --user ign

**Network issues**
    If you're behind a corporate firewall, you may need to configure proxy settings::

        pip install --proxy http://proxy.company.com:8080 ign

Getting Help
~~~~~~~~~~~~

If you encounter issues:

1. Check the GitHub issues: https://github.com/astralblue/ign/issues
2. Enable debug logging: ``ign --debug --verbose``
3. Verify your Python and pip versions
4. Try installing in a fresh virtual environment