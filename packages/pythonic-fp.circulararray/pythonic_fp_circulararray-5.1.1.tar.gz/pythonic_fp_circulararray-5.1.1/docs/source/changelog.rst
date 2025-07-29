*********
CHANGELOG
*********

PyPI pythonic-fp.circulararray project changelog.

Semantic Versioning
===================

Strict 3 digit semantic versioning adopted 2025-05-19.

- **MAJOR** version incremented for incompatible API changes
- **MINOR** version incremented for backward compatible added functionality
- **PATCH** version incremented for backward compatible bug fixes

See `Semantic Versioning 2.0.0 <https://semver.org>`_.

Releases and Important Milestones
=================================

5.1.1 - TBA
-----------

Devel environment changes.

- updated changelog.rst
- Pythonic FP homepage now points to its GitHub README.md

  - used to point to its GH-Pages


5.1.0 - 2025-07-04
------------------

First PyPI Release with Sphinx replacing pdoc.

- switched from ``pdoc`` to ``sphinx`` for document generation

  - no longer source code controlling generated HTML (too wasteful)
  - using ``sphinx.ext.githubpages`` extension to publish from this repo
  - using ``sphinx.ext.autodoc`` to generate detailed API documentation
  - using the ``piccolo-theme at https://pypi.org/project/piccolo-theme/``

    - beautiful dark mode
    - plays nice with ``autodoc`` and ``DarkReader`` 

- some formatting changes

  - no actual code changes
  - did remove TypeVar hack used for pdoc

- made pyproject.toml improvements

  - better tooling configurations
  - removed all version caps from pyproject.toml, see this
    `blog post <https://iscinumpy.dev/post/bound-version-constraints>`_.

5.0.0 - 2025-05-23
------------------

First PyPI release as ``pythonic-fp.circular-array``.

- there was already a PyPI project with the dtools name
- the name pythonic-fp was not taken

  - using it as the namespace name for the entire group
  - does exist as an "skeleton" project just to claim the name
  - installing it will break all the namespace packages
  - didn't want any confusion caused by someone else claiming the name

3.14.0 - 2025-05-10
-------------------

Made package just a single module.

- dtools.circular_array.ca -> dtools.circular_array
- docstring consolidations/updates

3.13.0 - 2025-05-06
-------------------

Version no longer determined dynamically.

- made all non-splatted method parameters position only
- version now set in pyproject.toml
- no longer doing 4 part development versioning
- version will either denote

  - the current PyPI release - if no substantive changes made
  - the next PyPI release - what development is working toward

3.12.1 - 2025-04-22
-------------------

- docstring changes
- pyproject.toml standardization

3.12.0 - 2025-04-07
-------------------

API change.

- class CA[D] no longer inherits from Sequence[D]
- typing improvements

3.11.0 - 2025-04-06
-------------------

Major API change.

- swapped names `ca` and `CA`

  - class name now `CA`
  - factory function taking variable number of arguments is now `ca`

- class initializer still takes `1` or `0` iterables

  - still want this class to behave like a builtin
  - but got tired fighting linters
  - maybe being "Pythonic" means

    - that only builtins should break naming conventions
    - naming conventions being

      - snake_case for functions and method names
      - CamelCase for class names

    - perhaps a visual distinction is useful to tell when you
      - are dealing with user/library Python code
      - C code presenting itself as a Python class

  - typing improvements

3.10.1 - 2025-04-03
-------------------

Major API changes.

- class name still `ca`

  - initializer takes 1 or 0 iterables

    - like Python builtin types `list` or `tuple`

  - factory function `CA` provided to create a `ca` from mult args

    - like `[]` or `{}`

- otherwise, method names are all snake_case compatible

  - examples

    - popL -> popl
    - pushR -> pushr
    - fractionFilled -> fraction_filled

- updated pyproject.toml
  - to better match other dtools namespace projects

3.9.1 - 2025-02-16
------------------

Fixed pdoc issues with new typing notation.

- updated docstrings
- had to add TypeVars

3.9.0 - 2025-01-16
------------------

First release as dtools.circular-array,
was previously grscheller.circular-array.

3.8.0 - 2025-01-03
------------------

Now circular-array indexing methods fully support slicing, also added
the rotL(n) and rotR(n) methods.

3.7.1 - 2024-11-18
------------------

For internal changes. Mostly for consistency across PyPI namespace projects

3.7.0 - 2024-10-26
------------------

Regenerated docs for PyPI release.

3.6.3.2 - 2024-10-20
--------------------

Just a commit, preparing for a 3.7.0 PyPI release.

- renamed class ca -> CA
- created factory function for original constructor use case
- generated docs in docs repo

3.6.2 - 2024-10-20
------------------

Removed docs from repo, now docs for all grscheller namespace projects located
[here](https://grscheller.github.io/grscheller-pypi-namespace-docs/).

3.6.1 - 2024-10-18
------------------

Infrastructure and minor docstring changes. Should be compatible with
version 3.6.0.

3.6.0 - 2024-09-21
------------------

No future changes planned for the foreseeable future

- feature complete
- no external dependencies
- well tested with other grscheller namespace packages
- final API tweaks made
- several more pytest tests added
- made the `compact` method private, now called `_compact_storage_capacity`

3.5.0 - 2024-09-21
------------------

- made the `double` method
- O(1) amortized pushes and pops either end.
- O(1) indexing
- fully supports slicing
- safely mutates over previous cached state, now called `_double_storage_capacity`
- major docstring improvements
- improved indentation and code alignment, now much more Pythonic

3.4.1 - 2024-08-17
------------------

- updated README.md to reflect name changes of CA methods
- docstring improvements

3.4.0 - 2024-08-15
------------------

Updated `__eq__` comparisons.

- first compare elements by identity before equality

  - I noticed that is what Python builtins do
  - makes dealing with grscheller.fp.nada module easier

- standardizing docstrings across grscheller PyPI projects

3.3.0.1 - 2024-08-05
--------------------

Just a commit, made a paradigm "regression".

- made a paradigm "regression", preparing for a 3.4.0 release
- felt CA was becoming way too complicated
- grscheller.datastructures needed it to fully embrace type annotations

  - but I was shifting too many features back into grscheller.circular-array
  - want ca to be useful for non-functional applications

The changes made were

- removed grscheller.fp dependency
- remove `_sentinel` and `_storable` slots from CA class
- remove copy method, just use `ca2 = CA(*ca1)` to make a shallow copy
- adjust `__repr__` and `__str__` methods
- experimenting with Sphinx syntax in docstrings (still using pdoc3)
- changed nomenclature from "left/right" to "front/rear"
- unsafe and safe versions of pop & fold functionality
- left and right folds improvements

  - consolidated `foldL, foldL1, foldR, foldR1` into `foldL` & `foldR`

- tests working

  - basically I changed pops to unsafe pops and added `try except` blocks
  - safe versions tests needed

    - safe pops return multiple values in tuples
    - will take a `default` value to return

      - if only asked to return 1 value and CA is empty
      - seems to work properly from iPython

3.2.0 - 2024-07-26
------------------

The class name was changed ``CircularArray -> CA`` Now takes a "sentinel" or "fallback" value in its
initializer, formally used ``None`` for this.

3.1.0 - 2024-07-11
------------------

Generic typing now being used, first PyPI release where multiple values can be
pushed on CircularArray.

3.0.0 - 2024-06-28
------------------
Just a commit, not a PyPI release.

CircularArray class now using Generic Type Parameter. new epoch in development,
start of 3.0 series. Now using TypeVars.

API changes:

- ``foldL(self, f: Callable[[T, T], T]) -> T|None``
- ``foldR(self, f: Callable[[T, T], T]) -> T|None``
- ``foldL1(self, f: Callable[[S, T], S], initial: S) -> S``
- ``foldR1(self, f: Callable[[T, S], S], initial: S) -> S``

2.0.0 - 2024-03-08
------------------

New "epoch" due to resizing bug fixed on previous commit.

- much improved and cleaned up
- better test suite
- method `_double()` made "public" and renamed `double()`
- method `resize(new_size)` now resizes to at least new_size

1.1.0.0 - 2024-03-08
--------------------

Just a commit to prepare for PyPI release 2.0.0!!!

- BUGFIX: Fixed a subtle resizing bug

  - bug probably present in all previous versions
  - not previously identified due to inadequate test coverage
  - test coverage improved vastly

- made some major code API changes

  - upon initialization minimizing size of the CircularArray
  - have some ideas on how to improve API for resizing CircularArrays
  - need to test my other 2 PyPI projects, both use circular-array as a dependency

1.0.1 - 2024-03-01
------------------

Docstring updates to match other grscheller PyPI repos.

1.0.0 - 2024-02-10
------------------

First stable PyPI release, dropped minimum Python requirement to 3.10.

0.1.1 - 2024-01-30
------------------

Changed circular-array from a package to just a module, actually a breaking API
change. Version number should have been 0.2.0 Also, gave CircularArray class
`foldL` & `foldR` methods.

0.1.0 - 2024-01-28
------------------

- initial PyPI grscheller.circular-array release
- migrated Circulararray class from grscheller.datastructures
- update docstrings to reflect current nomenclature

0.0.3 - 2024-01-28
------------------

Got gh-pages working for the repo.

0.0.2 - 2024-01-28
------------------

Pushed repo up to GitHub, created README.md file for project.

0.0.1 - 2024-01-28
------------------

Decided to split Circulararray class out of grscheller.datastructures, will make it its own PyPI
project. Got it working with datastructures locally.
