.. Pythonic FP - Circular Array documentation master file, created by
   sphinx-quickstart on Fri Jun 27 11:13:22 2025.
   To regenerate the documentation do: ``$ Sphinx-build -M html docs/source/ docs/build/``
   from the root repo directory.

Pythonic FP - Circular Array project
====================================

Part of of the `pythonic-fp namespace projects <https://github.com/grscheller/pythonic-fp/README.md>`_.

Overview
--------

PyPI project `pythonic.circular-array <https://pypi.org/project/pythonic-fp.circulararray/>`_
implements a full featured, generic, stateful circular array data structure.

- O(1) amortized pushes and pops either end 
- O(1) indexing
- Auto-resizing larger when necessary, can be manually compacted if desired
- Iterable, can safely be mutated while iterators continue iterating over previous state
- Fully supports slicing

Documentation
-------------

:doc:`Installation <installing>`
    Installing and importing the module.

:doc:`API docs <api>`
    Detailed API documentation.

Development
-----------

:doc:`changelog`
    CHANGELOG for the current and predecessor projects.

.. Hidden TOCs

.. toctree::
   :caption: Documentation
   :maxdepth: 2
   :hidden:

   installing
   api

.. toctree::
   :caption: Development
   :maxdepth: 2
   :hidden:

   changelog

