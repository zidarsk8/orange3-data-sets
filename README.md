Orange3 Example Add-on
======================

[![Build Status](https://travis-ci.org/zidarsk8/world_bank_data.svg?branch=master)](https://travis-ci.org/zidarsk8/world_bank_data/builds)
[![codecov.io](https://codecov.io/github/zidarsk8/world_bank_data/coverage.svg?branch=master)](https://codecov.io/github/zidarsk8/world_bank_data?branch=master)
[![Code Climate](https://codeclimate.com/github/zidarsk8/world_bank_data/badges/gpa.svg)](https://codeclimate.com/github/zidarsk8/world_bank_data)
[![Dependency Status](https://www.versioneye.com/user/projects/5739ad4fa0ca35005084183e/badge.svg?style=flat)](https://www.versioneye.com/user/projects/5739ad4fa0ca35005084183e)

This is an example add-on for [Orange3](http://orange.biolab.si). Add-on can extend Orange either 
in scripting or GUI part, or in both. We here focus on the GUI part and implement a simple (empty) widget,
register it with Orange and add a new workflow with this widget to example tutorials.

Installation
------------

To install the add-on using pip just run

    pip install --process-dependency-links -e .

or install with setup.py

    python setup.py install 

To register this add-on with Orange, but keep the code in the development directory (do not copy it to 
Python's site-packages directory), run

    python setup.py develop

Documentation / widget help can be built by running

    make html htmlhelp

from the doc directory.

Usage
-----

After the installation, the widget from this add-on is registered with Orange. To run Orange from the terminal,
use

    python -m Orange.canvas

The new widget appears in the toolbox bar under the section Example.

![screenshot](https://github.com/biolab/orange3-example-addon/blob/master/screenshot.png)
