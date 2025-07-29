Usage Guide
===========

This guide covers common usage patterns and advanced features of ``ign``.

Quick Start
-----------

Add templates to your .gitignore::

    ign Python Node

Update existing templates::

    ign

Basic Workflow
--------------

1. **Initial setup**: Add templates to your project::

       cd my-project
       ign Python JetBrains

2. **Regular updates**: Sync templates with upstream changes::

       ign

3. **Add new templates**: Include additional templates as needed::

       ign Rust

Command Line Interface
----------------------

Syntax
~~~~~~

::

    ign [OPTIONS] [TEMPLATE[@HASH]...]

Options Reference
~~~~~~~~~~~~~~~~~

Input/Output Options
^^^^^^^^^^^^^^^^^^^^

``-f, --file FILE``
    Specify input .gitignore file. Default is ``.gitignore``.
    Use ``-`` for stdin.

``-o, --output FILE``
    Specify output file. Default is same as input file.
    Use ``-`` for stdout.

Preview Options
^^^^^^^^^^^^^^^

``-n, --dry-run``
    Preview changes without writing to files.

``-d, --diff``
    Show unified diff of changes.

Logging Options
^^^^^^^^^^^^^^^

``-v, --verbose``
    Enable verbose output.

``--debug``
    Enable debug logging.

``--logging TYPE``
    Set logging format: ``console`` or ``json``.

Common Use Cases
----------------

Adding Templates
~~~~~~~~~~~~~~~~

Add Python and Node.js support::

    ign Python Node

The result will be a .gitignore with sections like::

    # --- BEGIN https://raw.githubusercontent.com/github/gitignore/abc123/Python.gitignore ---
    # Python template content
    # --- END https://raw.githubusercontent.com/github/gitignore/abc123/Python.gitignore ---

    # --- BEGIN https://raw.githubusercontent.com/github/gitignore/def456/Node.gitignore ---
    # Node.js template content  
    # --- END https://raw.githubusercontent.com/github/gitignore/def456/Node.gitignore ---

Updating Templates
~~~~~~~~~~~~~~~~~~

Update all existing templates::

    ign

This will:

- Detect existing templates from marker comments
- Check for newer versions
- Apply updates while preserving local modifications

Custom Modifications
~~~~~~~~~~~~~~~~~~~~

You can add custom rules within template sections::

    # --- BEGIN https://raw.githubusercontent.com/github/gitignore/.../Python.gitignore ---
    # Original Python rules...
    
    # My custom additions
    *.local
    /my-specific-file
    debug.log
    
    # --- END https://raw.githubusercontent.com/github/gitignore/.../Python.gitignore ---

These modifications will be preserved during updates.

Version Pinning
~~~~~~~~~~~~~~~

Pin templates to specific versions::

    ign Python@4f15b43d Node@main

This ensures reproducible builds and controlled updates.

Preview Changes
~~~~~~~~~~~~~~~

Preview what would change::

    ign --dry-run --diff Python

This shows the diff without applying changes.

Advanced Usage
--------------

Working with Pipes
~~~~~~~~~~~~~~~~~~~

Read from stdin, write to stdout::

    cat .gitignore | ign Python - > new-gitignore

Generate .gitignore from scratch::

    echo | ign Python Node Java > .gitignore

Custom Files
~~~~~~~~~~~~

Work with custom .gitignore files::

    ign --file backend/.gitignore --output backend/.gitignore Python Django

Multiple Projects
~~~~~~~~~~~~~~~~~

Batch update multiple projects::

    for dir in */; do
        (cd "$dir" && ign)
    done

Integration with Scripts
~~~~~~~~~~~~~~~~~~~~~~~~

Use in shell scripts::

    #!/bin/bash
    set -e
    
    echo "Updating .gitignore templates..."
    if ign --diff; then
        echo "Templates updated successfully"
    else
        echo "Failed to update templates" >&2
        exit 1
    fi

Template Selection
------------------

Finding Templates
~~~~~~~~~~~~~~~~~

Available templates are in the `GitHub gitignore repository`_.

.. _GitHub gitignore repository: https://github.com/github/gitignore

Common templates include:

**Languages**
    Python, Java, JavaScript, TypeScript, Go, Rust, C++, C#, PHP, Ruby, Swift, Kotlin

**Frameworks**
    Node, Django, Rails, Laravel, React, Vue, Angular, Spring, Unity

**Tools**
    JetBrains, VisualStudio, Vim, Emacs, SublimeText, Xcode

**Platforms**
    macOS, Windows, Linux, Android, iOS

**Build Tools**
    Maven, Gradle, CMake, Bazel, Buck

Template Naming
~~~~~~~~~~~~~~~

Template names must match exactly (case-sensitive) with files in the repository:

- ``Python`` (not ``python``)
- ``Node`` (not ``nodejs`` or ``node.js``)
- ``JetBrains`` (not ``jetbrains``)

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Template not found**
    Check the exact name at https://github.com/github/gitignore::

        ign NonExistentTemplate
        # Error: Template not found

**Merge conflicts**
    When automatic merging fails, content is preserved::

        ign Python
        # Warning: Cannot apply diff, local contents unchanged

**Malformed markers**
    If marker comments are corrupted::

        ign
        # Error: Unexpected marker type

**Rate limits**
    Set GitHub API token for higher limits::

        export GITHUB_API_TOKEN=ghp_your_token_here

Debug Information
~~~~~~~~~~~~~~~~~

Enable debug logging for detailed information::

    ign --debug --verbose Python

This shows:

- Template fetching details
- SHA resolution process
- Merge strategy decisions
- Diff application results

Best Practices
--------------

1. **Regular updates**: Run ``ign`` periodically to stay current
2. **Version control**: Commit .gitignore changes to track template evolution
3. **Custom sections**: Keep custom rules in separate sections or files
4. **Preview first**: Use ``--dry-run --diff`` for major updates
5. **API token**: Set ``GITHUB_API_TOKEN`` for better performance
6. **Backup**: Keep backups of heavily customized .gitignore files