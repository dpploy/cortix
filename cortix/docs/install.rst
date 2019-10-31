:orphan:
Installation and Getting Started
===================================

**Pythons**: Python 3.4, 3.5, 3.6, 3.7

**Platforms**: Linux/Unix (inluding macOS)

**PyPI package name**: `cortix <https://pypi.org/project/cortix/>`_

**Dependencies**: 
   * `mpi4py <https://mpi4py.readthedocs.io/en/stable/>`_
   * `pandas <https://pandas.pydata.org/>`_
   * `networkx <https://networkx.github.io/>`_
   * `matplotlib <https://matplotlib.org/>`_
   * `numpy <https://www.numpy.org/>`_
   * `scipy <https://www.scipy.org/>`_
   * `pytest <https://www.pytest.org/>`_

**Documentation as PDF**: `download latest <https://dpploy.github.io/cortix/Cortix.pdf>`_

Install ``cortix``
----------------------------------------

Stable Release (via PyPi)
-----------------------------------
1. Run the following command in your command line::

    pip install --user cortix

Development Version (from source)
--------------------------------------------
1. Clone the repository::
   
   $ git clone https://github.com/dpploy/cortix.git

2. Install the required dependencies listed in `requirements.txt`::
   
   $ pip install --user -r cortix/requirements.txt

3. Add `cortix`'s parent path to the `PYTHONPATH` environment variable::
   
   $ export PYTHONPATH=$PYTHONPATH:/path/to/dir/containing/cortix

.. note::
   The path above is NOT the path to ``cortix`` itself, but rather the
   path to ``cortix``'s parent directory. That is, if ``cortix`` exists in
   ``/some/path/cortix``, be sure to add ``/some/path`` to your ``PYTHONPATH``.
   You may want to add this line to your ``.bashrc`` in order for it 
   to be persistent

Testing your install
--------------------
To test your Cortix install, run the droplet example from the python shell::
   
   >> from cortix.examples.console_run import droplet_run as droplet 
   
   >> droplet.run()
