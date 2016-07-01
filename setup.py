#!/usr/bin/env python

from setuptools import setup

ENTRY_POINTS = {
    # Entry point used to specify packages containing tutorials accessible
    # from welcome screen. Tutorials are saved Orange Workflows (.ows files).
    'orange.widgets.tutorials': (
        # Syntax: any_text = path.to.package.containing.tutorials
        'exampletutorials = orangecontrib.wbd.tutorials',
    ),

    # Entry point used to specify packages containing widgets.
    'orange.widgets': (
        # Syntax: category name = path.to.package.containing.widgets
        # Widget category specification can be seen in
        #    orangecontrib/wbd/widgets/__init__.py
        'Data Sets = orangecontrib.wbd.widgets',
    ),

    # Register widget help
    "orange.canvas.help": (
        'html-index = orangecontrib.wbd.widgets:WIDGET_HELP_PATH',)
}

KEYWORDS = (
    # [PyPi](https://pypi.python.org) packages with keyword "orange3 add-on"
    # can be installed using the Orange Add-on Manager
    'orange3 add-on',
)

if __name__ == '__main__':
    setup(
        name="World Bank Data",
        packages=[
            'orangecontrib',
            'orangecontrib.wbd',
            'orangecontrib.wbd.tutorials',
            'orangecontrib.wbd.widgets'
        ],
        package_data={
            'orangecontrib.wbd': ['tutorials/*.ows'],
            'orangecontrib.wbd.widgets': ['icons/*'],
        },
        install_requires=[
            'observable',
            'simple_wbd',
        ],
        entry_points=ENTRY_POINTS,
        keywords=KEYWORDS,
        namespace_packages=['orangecontrib'],
        include_package_data=True,
        zip_safe=False,
    )
