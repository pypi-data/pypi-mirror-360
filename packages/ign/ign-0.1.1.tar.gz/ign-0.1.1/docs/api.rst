API Reference
=============

This section provides detailed API documentation for the ``ign`` package.

Main Module
-----------

.. automodule:: ign
   :members:
   :undoc-members:
   :show-inheritance:

Core Functions
~~~~~~~~~~~~~~

.. autofunction:: ign.main

.. autofunction:: ign.async_main

.. autofunction:: ign.patch_with_diff

Context Managers
~~~~~~~~~~~~~~~~

.. autofunction:: ign.input_file

.. autofunction:: ign.output_file

Network Module
--------------

.. automodule:: ign.net
   :members:
   :undoc-members:
   :show-inheritance:

Template Operations
~~~~~~~~~~~~~~~~~~~

.. autofunction:: ign.net.get_template

.. autofunction:: ign.net.get_latest_sha

HTTP Client Management
~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: ign.net.httpx_client

Exceptions
~~~~~~~~~~

.. autoexception:: ign.net.NoCommitError
   :members:
   :show-inheritance:

Logging Module
--------------

.. automodule:: ign._logging
   :members:
   :undoc-members:
   :show-inheritance:

Structured Logging
~~~~~~~~~~~~~~~~~~

.. autoclass:: ign._logging.StructLogAdapter
   :members:
   :show-inheritance:

Formatters
~~~~~~~~~~

.. autoclass:: ign._logging.ExtraFormatter
   :members:
   :show-inheritance:

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ign._logging.LoggingType
   :members:
   :show-inheritance:

.. autofunction:: ign._logging.make_logging_handler

Constants Module
----------------

.. automodule:: ign.consts
   :members:
   :undoc-members:

Utilities Module
----------------

.. automodule:: ign.utils
   :members:
   :undoc-members:
   :show-inheritance:

Metaclasses
~~~~~~~~~~~

.. autoclass:: ign.utils.FinalMeta
   :members:
   :show-inheritance:

Type Annotations
----------------

Common Types
~~~~~~~~~~~~

The following types are commonly used throughout the codebase:

.. code-block:: python

   from typing import Sequence, TextIO, Generator
   from pathlib import Path
   
   # Template content and SHA
   TemplateResult = tuple[Sequence[str], str]
   
   # File content as lines
   FileLines = Sequence[str]

Error Handling
--------------

Exception Hierarchy
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   BaseException
   └── Exception
       └── RuntimeError
           └── NoCommitError

Custom Exceptions
~~~~~~~~~~~~~~~~~

All custom exceptions inherit from standard Python exceptions and provide
additional context for debugging.

Constants and Configuration
---------------------------

GitHub Integration
~~~~~~~~~~~~~~~~~~

.. data:: ign.consts.OWNER_REPO
   
   The GitHub repository containing gitignore templates.

.. data:: ign.consts.RAW_BASE_URL
   
   Base URL for fetching raw template files.

.. data:: ign.consts.API_ENDPOINT
   
   GitHub API endpoint for repository operations.

Regular Expressions
~~~~~~~~~~~~~~~~~~~

.. data:: ign.MARKER_RE
   
   Regular expression pattern for matching template marker comments.

Internal APIs
-------------

.. note::
   
   The following APIs are considered internal and may change without notice.
   Use at your own risk.

Argument Parsing
~~~~~~~~~~~~~~~~

.. autofunction:: ign._build_argparser

These functions are used internally by the command-line interface and are
not intended for direct use by library consumers.