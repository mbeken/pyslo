"""pyslo

Module to help standardise the calculation of SLO data from metrics.

This module implements the logic defined in the
[SRE Workbook](https://landing.google.com/sre/workbook/toc/) in an
agnostic way.

In order to have SLO's reported consistently regardless of backend
timeseries database, aggregations and computations are all performed
within the module, as opposed to relying upon the backend's API
functionality.

Whilst this may not be the most efficient methodology if you know you
can exist in a single cloud environment, or utilize a single monitoring
framework, it is helpful if you are strung out over multiple clouds
and on prem environments.
"""

__version__ = '0.0.6'
