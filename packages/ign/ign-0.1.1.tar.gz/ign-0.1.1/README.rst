======
ign
======

A tool for composing and synchronizing .gitignore from GitHub's template collection.

Description
===========

``ign`` automatically manages .gitignore files by synchronizing them with templates from GitHub's `gitignore repository`_. It intelligently merges your local modifications with upstream template changes, preserving your customizations while keeping templates up to date.

.. _gitignore repository: https://github.com/github/gitignore

Key Features
============

- **Template synchronization**: Automatically update .gitignore templates from GitHub
- **Local modification preservation**: Keeps your custom additions while updating templates
- **Intelligent merging**: Uses diff/patch algorithms to resolve conflicts
- **Multiple merge strategies**: Tries different approaches to apply changes safely
- **Auto-detection**: Automatically detects existing templates in your .gitignore
- **Flexible input/output**: Works with files or stdin/stdout
- **Dry-run mode**: Preview changes before applying them

Installation
============

Using uv::

    uv add ign

Using pip::

    pip install ign

Usage
=====

Basic Usage
-----------

Add templates to your .gitignore::

    ign Python Node

Update existing templates::

    ign

Sync specific templates with version pinning::

    ign Python@main Node@abc1234

Command Line Options
--------------------

::

    ign [OPTIONS] [TEMPLATE[@HASH]...]

**Options:**

-f, --file FILE         Input .gitignore file (default: .gitignore, - for stdin)
-o, --output FILE       Output file (default: same as input, - for stdout)
-d, --diff              Show unified diff of changes
-n, --dry-run           Preview changes without writing
-v, --verbose           Verbose output: enable debug logging
-q, --quiet             Quiet output: only show errors and warnings
--logging TYPE          Logging format: console or json (default: console if TTY, otherwise JSON)
--debug                 All-debug output: enable debug logging on all libraries
--version               Show version and exit

**Arguments:**

TEMPLATE[@HASH]         GitHub template names (without .gitignore extension)
                        Optional @HASH pins to specific commit

Examples
========

Add Python and Node.js templates::

    ign Python Node

Update all existing templates::

    ign

Preview changes without applying::

    ign --dry-run --diff

Use with custom file::

    ign --file my-project/.gitignore Java Maven

Read from stdin, write to stdout::

    cat .gitignore | ign -f- Python > new-gitignore

Pin template to specific version::

    ign Python@4f15b43 Node@latest

How It Works
============

Template Markers
-----------------

``ign`` uses special marker comments to track template sections::

    # --- BEGIN https://raw.githubusercontent.com/github/gitignore/{SHA}/{TEMPLATE}.gitignore ---
    # Template content here
    # --- END https://raw.githubusercontent.com/github/gitignore/{SHA}/{TEMPLATE}.gitignore ---

These markers allow ``ign`` to:

- Identify which templates are already included
- Track the version (SHA) of each template
- Preserve local modifications between updates

Merge Strategy
--------------

When updating templates, ``ign`` uses a sophisticated merge algorithm:

1. **Fetch versions**: Downloads both old (current) and new (latest) template versions
2. **Apply strategies**: Tries two different merge approaches:
   
   - **Strategy A**: Apply (new - old) changes to your local modifications
   - **Strategy B**: Apply (local - old) changes to the new template
   
3. **Conflict resolution**: Falls back gracefully when automatic merging fails
4. **Preserve customizations**: Your local additions are always preserved

Local Modifications
-------------------

You can safely add custom rules within template sections. For example::

    # --- BEGIN https://raw.githubusercontent.com/github/gitignore/.../Python.gitignore ---
    # Original Python template content...
    
    # Your custom additions
    *.local
    /my-project-specific-file
    
    # --- END https://raw.githubusercontent.com/github/gitignore/.../Python.gitignore ---

These modifications will be preserved during template updates.

Configuration
=============

Environment Variables
---------------------

**GITHUB_API_TOKEN**
    Optional GitHub API token for higher rate limits. Useful for heavy usage
    or when working with private repositories.

**Example .env file**::

    GITHUB_API_TOKEN=ghp_your_token_here

Template Sources
----------------

Templates are fetched from the official `GitHub gitignore repository`_.
Available templates include:

- **Languages**: Python, Java, JavaScript, Go, Rust, C++, etc.
- **Frameworks**: Node, Django, Rails, Laravel, etc.  
- **Tools**: JetBrains, VisualStudio, Vim, macOS, Windows, etc.
- **Platforms**: Android, iOS, Unity, etc.

.. _GitHub gitignore repository: https://github.com/github/gitignore

For a complete list, visit: https://github.com/github/gitignore

Troubleshooting
===============

Common Issues
-------------

**Template not found**
    Ensure the template name matches exactly (case-sensitive) with files in
    the GitHub repository. Check https://github.com/github/gitignore for
    available templates.

**Merge conflicts**
    If automatic merging fails, ``ign`` will preserve your current content
    and log the issue. You may need to manually resolve conflicts.

**API rate limits**
    Set ``GITHUB_API_TOKEN`` environment variable to increase rate limits.

**Missing END marker**
    If you manually edit marker comments, ensure BEGIN/END pairs match exactly.
    Use ``--debug`` for detailed error information.

Debug Mode
----------

Enable debug logging for detailed information::

    ign --debug --verbose Python

This shows:

- Template fetching details
- Merge strategy decisions  
- Diff application results
- API request information

Development
===========

Setting up development environment::

    git clone https://github.com/astralblue/ign.git
    cd ign
    uv sync

Running tests::

    pytest

Code formatting::

    ruff check --fix && ruff format

Building documentation::

    cd docs
    make html

License
=======

MIT License. See LICENSE file for details.

Contributing
============

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite and linting
5. Submit a pull request

For bug reports and feature requests, please use the GitHub issue tracker.

Links
=====

- **Repository**: https://github.com/astralblue/ign
- **Issues**: https://github.com/astralblue/ign/issues
- **PyPI**: https://pypi.org/project/ign/
- **GitHub Templates**: https://github.com/github/gitignore