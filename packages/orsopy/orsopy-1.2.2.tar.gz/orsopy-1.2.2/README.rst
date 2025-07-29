======
orsopy
======

.. image:: https://img.shields.io/pypi/v/orsopy.svg
        :target: https://pypi.python.org/pypi/orsopy

.. image:: https://github.com/reflectivity/orsopy/actions/workflows/pytest.yml/badge.svg
        :target: https://github.com/reflectivity/orsopy/actions/workflows/pytest.yml

.. image:: https://github.com/reflectivity/orsopy/actions/workflows/docs_build.yml/badge.svg
        :target: https://github.com/reflectivity/orsopy/actions/workflows/docs_build.yml

.. image:: https://coveralls.io/repos/github/reflectivity/orsopy/badge.svg?branch=main
        :target: https://coveralls.io/github/reflectivity/orsopy?branch=main
        :alt: Coverage Level

orsopy is a Python library that implements ORSO functionality, which currently includes the `reduced data file format`_.
The orsopy package is used by a range of data reduction and analysis packages for the writing and reading of reduced reflectometry data. 
This data is written following the `ORSO defined specification`_, enabling a metadata-rich and flexible file to be created. 

`ORSO`_ is an open organisation aimed at improving the scientific techniques of neutron and X-ray reflectometry. 
In the interest of transparency, all minutes from orsopy developer meetings are available in the `Documents`_ in the sidebar of this page. 
If you are interested in getting involved in developing orsopy, please feel free to `contribute`_ or get in touch on the `ORSO Slack`_ (where there is a channel dedicated to orsopy).

Features
--------

* `Reading and writing of ORSO specification reduced reflectivity files`_. 

.. _`reduced data file format`: https://www.reflectometry.org/file_formats/
.. _`ORSO defined specification`: https://www.reflectometry.org/file_format/specification
.. _`ORSO`: https://www.reflectometry.org
.. _`Documents`: https://www.reflectometry.org/orsopy/documents
.. _`contribute`: https://www.reflectometry.org/orsopy/contributing
.. _`ORSO Slack`: https://join.slack.com/t/orso-co/shared_invite/zt-z7p3v89g-~JgCbzcxurQP6ufqdfTCfw
.. _`Reading and writing of ORSO specification reduced reflectivity files`: modules.html#fileio
