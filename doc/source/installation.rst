Installation
************

Requirements
============

Before installing this package, make sure to install Orange3_.

.. _Orange3: https://github.com/biolab/orange3/


With pip
========

.. code-block:: bash

   pip install orange3-datasets

With gui
========

You can install this plugin by going to Options > Add-ons... and selecting 
Orange3-DataSets


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
