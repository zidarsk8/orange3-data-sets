Installation
************

Virtualenv
==========

This is an optional step, but it is recommended that you install and use python
libraries in separate virtual environments. For more info see virtualenv_.

.. _virtualenv: https://virtualenv.pypa.io/en/stable/

.. code-block:: bash

    virtualenv --python=python3 --system-site-packages ~/venv3
    source ~/venv3/bin/activate

Requirements
============

Orange3_

.. _Orange3: https://github.com/biolab/orange3/

Installing from tarball
=========

.. code-block:: bash

   pip install https://github.com/zidarsk8/orange3-data-sets/tarball/0.2.0

Installing from source
======================

This is mostly useful for development or if you need to tweak a few lines. Make
sure you have git_ installed on your system.

.. _git: https://git-scm.com/

.. code-block:: bash

   git clone https://github.com/zidarsk8/orange3-data-sets.git
   cd orange3-data-sets
   
   pip install -e .

   # for running tests, linters and generating docs you can also run

   pip install -r requirements.txt


