Install
=======

Graphdict requires Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12 or 3.13.  If you do not already
have a Python environment configured on your computer, please see the
instructions for installing the full `scientific Python stack
<https://scipy.org/install.html>`_.

Below we assume you have the default Python environment already configured on
your computer and you intend to install ``graphdict`` inside of it.  If you want
to create and work with Python virtual environments, please follow instructions
on `venv <https://docs.python.org/3/library/venv.html>`_ and `virtual
environments <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

First, make sure you have the latest version of ``pip`` (the Python package manager)
installed. If you do not, refer to the `Pip documentation
<https://pip.pypa.io/en/stable/installing/>`_ and install ``pip`` first.

Install the released version
----------------------------

Install the current release of ``graphdict`` with ``pip``::

    $ pip install graphdict[default]

To upgrade to a newer release use the ``--upgrade`` flag::

    $ pip install --upgrade graphdict[default]

If you do not have permission to install software systemwide, you can
install into your user directory using the ``--user`` flag::

    $ pip install --user graphdict[default]

If you do not want to install our dependencies (e.g., ``numpy``, ``scipy``, etc.),
you can use::

    $ pip install graphdict

This may be helpful if you are using PyPy or you are working on a project that
only needs a limited subset of our functionality and you want to limit the
number of dependencies.

Alternatively, you can manually download ``graphdict`` from
`GitHub <https://github.com/taylortech75/graphdict/releases>`_  or
`PyPI <https://pypi.python.org/pypi/graphdict>`_.
To install one of these versions, unpack it and run the following from the
top-level source directory using the Terminal::

    $ pip install .[default]

Install the development version
-------------------------------

If you have `Git <https://git-scm.com/>`_ installed on your system, it is also
possible to install the development version of ``graphdict``.

Before installing the development version, you may need to uninstall the
standard version of ``graphdict`` using ``pip``::

    $ pip uninstall graphdict

Then do::

    $ git clone https://github.com/taylortech75/graphdict.git
    $ cd graphdict
    $ pip install -e .[default]

The ``pip install -e .[default]`` command allows you to follow the development branch as
it changes by creating links in the right places and installing the command
line scripts to the appropriate locations.

Then, if you want to update ``graphdict`` at any time, in the same directory do::

    $ git pull

Extra packages
--------------

.. note::
   Some optional packages (e.g., `gdal`) may require compiling
   C or C++ code.  If you have difficulty installing these packages
   with `pip`, please consult the homepages of those packages.

The following extra packages provide additional functionality. See the
files in the ``requirements/`` directory for information about specific
version requirements.

- `PyGraphviz <http://pygraphviz.github.io/>`_ and
  `pydot <https://github.com/erocarrera/pydot>`_ provide graph drawing
  and graph layout algorithms via `GraphViz <http://graphviz.org/>`_.
- `PyYAML <http://pyyaml.org/>`_ provides YAML format reading and writing.
- `gdal <http://www.gdal.org/>`_ provides shapefile format reading and writing.
- `lxml <http://lxml.de/>`_ used for GraphML XML format.

To install ``graphdict`` and extra packages, do::

    $ pip install graphdict[default,extra]

To explicitly install all optional packages, do::

    $ pip install pygraphviz pydot pyyaml gdal lxml

Or, install any optional package (e.g., ``pygraphviz``) individually::

    $ pip install pygraphviz

Testing
-------

Graphdict uses the Python ``pytest`` testing package.  You can learn more
about pytest on their `homepage <https://pytest.org>`_.

Test a source distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can test the complete package from the unpacked source directory with::

    pytest graphdict

Test an installed package
^^^^^^^^^^^^^^^^^^^^^^^^^

From a shell command prompt you can test the installed package with::

   pytest --pyargs graphdict
