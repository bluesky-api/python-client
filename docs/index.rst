.. blueskyapi documentation master file, created by
   sphinx-quickstart on Wed Dec 29 13:17:02 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

blueskyapi.io Python client
===========================

`blueskyapi.io <https://blueskyapi.io>`_ provides easy access to
current and historical weather forecast data. This library provides
simple access to the API using Python 3.7+.

For more detailed information about the endpoints and available
variables see the `documentation on blueskyapi.io
<https://blueskyapi.io/docs/api>`_.

Installation
------------

You can install it using any of the common package managers:

.. code:: console

    $ pip install blueskyapi

.. code:: console

    $ poetry add blueskyapi

.. code:: console

    $ pipenv install blueskyapi

Or using `conda` from the conda-forge channel:

.. code:: console

    $ conda config --add channels conda-forge
    $ conda install blueskyapi


Example
-------

Here's a quick example to get you started, no API key needed::

    import blueskyapi

    client = blueskyapi.Client()
    berlin_forecast = client.latest_forecast(52.5, 13.5)

    print(berlin_forecast)
    #              forecast_moment  forecast_distance  apparent_temperature_at_2m  categorical_rain_at_surface  ...  wind_v_at_80m  wind_v_at_100m  wind_v_at_max_wind  visibility_at_surface
    # 0  2021-12-29 06:00:00+00:00                  0                      272.00                            1  ...           2.33            2.33              -14.98                24128.0
    # 1  2021-12-29 06:00:00+00:00                  3                      272.16                            1  ...           2.10            2.10              -17.45                 4848.0
    # 2  2021-12-29 06:00:00+00:00                  6                      271.84                            0  ...          -1.23           -1.23              -28.05                   95.2
    # ...


Client
------

.. autoclass:: blueskyapi.Client
   :members:
   :undoc-members:


Default configuration
---------------------

.. automodule:: blueskyapi.default_config
   :members:


Errors
------

.. automodule:: blueskyapi.errors
   :members:
   :show-inheritance:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
