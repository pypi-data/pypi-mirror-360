==============================================================================
*mckit-nuclides*: tables with information on elements and nuclides
==============================================================================



|Maintained| |License| |Versions| |PyPI| |Docs|

.. contents::


Description
-----------

The module presents basic information on chemical elements and nuclides including natural presence.
The data is organized as Pandas tables.
Pandas allows to use dataset approach on data indexing, joining and selecting.
There are also some tools to work with composition fractions.

.. note::

    The documentation is in progress yet.

Installation
------------

.. TODO


Examples
--------

.. TODO

Contributing
------------

.. image:: https://github.com/MC-kit/mckit-nuclides/workflows/Tests/badge.svg
   :target: https://github.com/MC-kit/mckit-nuclides/actions?query=workflow%3ATests
   :alt: Tests
.. image:: https://codecov.io/gh/MC-kit/mckit-nuclides/branch/master/graph/badge.svg?token=wlqoa368k8
  :target: https://codecov.io/gh/MC-kit/mckit-nuclides
.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
   :target: https://pycqa.github.io/isort/
.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

Notes
-----

Half lives are extracted from [4] with /home/dvp/.julia/dev/Tools.jl/scripts/extract-half-lives.jl (nice script by the way).

References
----------

1. Kim, Sunghwan, Gindulyte, Asta, Zhang, Jian, Thiessen, Paul A. and Bolton, Evan E..
   "PubChem Periodic Table and Element pages: improving access to information on chemical
   elements from authoritative sources" Chemistry Teacher International, vol. 3, no. 1, 2021, pp. 57-65.
   https://doi.org/10.1515/cti-2020-0006
2. Elements table. https://pubchem.ncbi.nlm.nih.gov/rest/pug/periodictable/CSV
3. Coursey, J.S., Schwab, D.J., Tsai, J.J., and Dragoset, R.A. (2018-06-14),
   Atomic Weights and Isotopic Compositions (version 4.1). [Online]
   Available: http://physics.nist.gov/Comp [year, month, day].
   National Institute of Standards and Technology, Gaithersburg, MD.
4. JEFF-3.3 radioactive decay data file https://www.oecd-nea.org/dbdata/jeff/jeff33/downloads/JEFF33-rdd_all.asc


.. Substitutions

.. |Maintained| image:: https://img.shields.io/badge/Maintained%3F-yes-green.svg
   :target: https://github.com/MC-kit/mckit-nuclides/graphs/commit-activity
.. |Tests| image:: https://github.com/MC-kit/mckit-nuclides/workflows/Tests/badge.svg
   :target: https://github.com/MC-kit/mckit-nuclides/actions?workflow=Tests
   :alt: Tests
.. |License| image:: https://img.shields.io/github/license/MC-kit/mckit-nuclides
   :target: https://github.com/MC-kit/mckit-nuclides
.. |Versions| image:: https://img.shields.io/pypi/pyversions/mckit-nuclides
   :alt: PyPI - Python Version
.. |PyPI| image:: https://img.shields.io/pypi/v/mckit-nuclides
   :target: https://pypi.org/project/mckit-nuclides/
   :alt: PyPI
.. |Docs| image:: https://readthedocs.org/projects/mckit-nuclides/badge/?version=latest
   :target: https://mckit-nuclides.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
