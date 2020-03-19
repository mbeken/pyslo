"""Metric Client

Metric clients are used to retrieve time series data from a vairety of
sources. The MetricClient class can be inherited by provider specific derivatives.

Currently supported:
    - StackDriver
        Client library is in alpha. Using version v3:-
            https://googleapis.dev/python/monitoring/latest/gapic/v3/api.html

Planned implementations:
    - Azure Metric Service
    - Prometheus
"""

from google.cloud import monitoring_v3

MetricDescriptor = monitoring_v3.enums.MetricDescriptor


class NoMetricDataAvailable(Exception):
    """ NoMetricDataAvailable

    Thrown if you try to retrieve data using invalid
    or out of range parameters
    """


class MetricClient():
    """Parent object for source specific metric clients.

    Attributes:
        project:       id of the GCP project hosting Stackdriver

    """

    value_type = None

    def timeseries_dataframe(self):
        """Retrieve data from time series db and return as a pandas dataframe
        """
        return
