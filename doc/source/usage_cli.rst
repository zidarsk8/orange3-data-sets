Usage CLI
*********

This plugin is an extension of the simple_wbd_ API helper. For more information
look at the original source.

.. _simple_wbd: https://github.com/zidarsk8/simple_wbd

Starting
========

This is a starting point for all code snippets below.

.. code-block:: python

    from orangecontrib.wbd import api_wrapper
    api = api_wrapper.IndicatorAPI()


Getting countries
=================

You can filter the final dataset by specific countries. But the World Bank Data
API includes aggregate regions and some non standard ISO country codes. You can
get all possible codes with 

.. code-block:: python

    api.get_countries()


This will return a list of all country data. When writing the query you can use
the alpha-2 or alpha-3 country code.

Getting indicators
==================

There are around 18k indicators currently on World Band Data API. Since most of
them do not have any data in, the default indicator filter is set for Common.
You can also fetch all and featured indicators.

.. code-block:: python

    # get all common indicators
    indicators = api.get_indicators()

    featured_indicators = api.get_indicators(filter_="featured")

    all_indicators = api.get_indicators(filter_=None)

Fetching data
=============

Fetching data for a single indicator
------------------------------------

.. code-block:: python

    dataset = api.get_dataset("some.indicator.id")
    dataset = api.get_dataset(["some.indicator.id"])  # this is the same call


The API will return our modified Indicator dataset that can generate an Orange
table.

.. code-block:: python

    # Get indicator data with countries in rows and dates in columns.
    dataset.as_orange_table()

    # Get time series data where dates are in rows and each column 
    # represents data for one country.
    dataset.as_orange_table(timeseries=True)


Fetching data for multiple indicators
-------------------------------------

.. code-block:: python

    dataset = api.get_dataset([
        "some.indicator.id",
        "some.indicator.id.2",
        "some.indicator.id.XYZ",
    ])

You can get an Orange table same as with single indicator, the only difference
here is that column headers will have indicator prefix. So in this case, each
column would appear 3 times with a different indicator prefix and data.
