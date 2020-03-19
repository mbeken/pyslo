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

import time
import datetime
import pytz
import pandas as pd
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


class StackdriverMetricClient(MetricClient):
    """Stackdriver Metric Client

    This client will allow you to retrieve metrics from a Stackdriver
    monitoring instance.

    Attributes:
        project:        string. id of the GCP project hosting Stackdriver
        metric_type:    string. the metric type as defined in stackdriver.
                        e.g. composer.googleapis.com/environment/healthy
                        This is most easily found by locating the metric in StackDriver Metrics
                        Explorer, then viewing as JSON.
                        The metric type is found as part of the timeSeriesFilter.
        value_type:     metric type, as a type defined in google.cloud.monitoring_v3
                        e.g. monitoring_v3.enums.MetricDescriptor.ValueType.BOOL

    """

    def __init__(self, project):
        self.project = project
        self.metric_type = None
        self.value_type = None

        self._client = monitoring_v3.MetricServiceClient()

    def timeseries_dataframe(self, end=time.time(), end_nanos=0, duration=3600):
        """Fetches and returns a dataframe of timeseries data

        By default this will retrieve the last hours worth of data.
        By specifying duration you will get that amount of data from now back.
        If you want a custom range then specify both end and duration.

        Args:
            end:        Optional. A float that represents the end of the period, as the time in
                        seconds since the epoch. default is now. Value will be converted to an
                        integer second. Use end_nanos if you need nanosecond precision.
            end_nanos:  Optional. Integer number of nano seconds that will be added to the end
                        value. deafult = 0
            duration:   Optional. An integer length of the period to retrieve in seconds.
                        default = 3600s

        Returns:
            A pandas dataframe
        """
        interval = self.set_interval(end, end_nanos, start_time=(end - duration))
        iterator = self.get_timeseries_iter(interval)
        materialized = self.fetch_iter_results(iterator)
        return self.to_df(materialized)

    @property
    def filter(self):
        """Formats a metric filter

        Returns:
            A string that can be passed as the filter_ arg during a MetricServiceClient
            list_time_series call.  The filter specifies which time series data is being requested.
            The filter must specify a single metric type, and can additionally
            specify metric labels and other information. For example:

            metric.type = "compute.googleapis.com/instance/cpu/usage_time" AND
                metric.labels.instance_name = "my-instance-name"

        Todo: - for now we are just making the simplest case filter!
        """
        return f'metric.type = "{self.metric_type}"'

    def get_timeseries_iter(self, interval):
        """Retrieves timeseries data from Stackdriver

        Args:
            interval: google.cloud.monitoring_v3.types.TimeInterval()

        Returns:
            A page or results iterator.
        """
        project_name = self._client.project_path(self.project)
        results_iter = self._client.list_time_series(
            project_name,
            self.filter,
            interval,
            monitoring_v3.enums.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        return results_iter

    @staticmethod
    def get_labels(result):
        """Extract the resource labels from the result object

        Args:
            result:

        Returns:
            a 'google.protobuf.pyext._message.ScalarMapContainer'. Basically
            a dict type object with the labels.
        """
        return result.resource.labels

    def to_df(self, results):
        """
        For a set of results, create a dataframe.
        Dastaframe will include the result resource labels as
        columns.
        """
        points = list()
        for result in results:
            labels = self.get_labels(result)
            print(type(labels))
            for point in result.points:
                start_time = self.convert_point_time(
                    point.interval.start_time,
                    as_timestamp=False
                    )

                end_time = self.convert_point_time(
                    point.interval.end_time,
                    as_timestamp=False
                )

                point_dict = {
                        'start_timestamp': start_time,
                        'end_timestamp': end_time,
                        'value': self.get_point_value(point.value)
                        }
                point_dict.update(labels)
                points.append(point_dict)
        if len(points) == 0:
            raise NoMetricDataAvailable

        return pd.DataFrame(points)

    def get_point_value(self, point_value):
        """EXtract value from point_value object

        Args:
            point_value: instance of google.cloud.monitoring_v3.types.TypedValue
        Returns:
            The value of the TypedValue object
        """
        if self.value_type == MetricDescriptor.ValueType.BOOL:
            return int(point_value.bool_value)
        else:
            raise Exception

    @staticmethod
    def convert_point_time(point_time, as_timestamp):
        """Convert a TypedValues time to a datetime value
        
        Args:
            point_time: google.cloud.monitoring_v3.types.TypedValue

        Returns:
            datetime object. Note datetime object only supports microsecond
            accuracy.
        """
        seconds = point_time.seconds
        nanos = point_time.nanos
        if as_timestamp:
            return seconds + nanos/10**9
        else:
            return datetime.datetime.fromtimestamp(seconds + nanos/10**9, tz=pytz.UTC)


    @staticmethod
    def fetch_iter_results(results_iterator):
        results = list()
        for result in results_iterator:
            results.append(result)
        return results


    @staticmethod
    def set_interval(end_time, end_time_nanos=0, start_time=None):
        """Create a TimeInterval object based on input start and end times

        For GAUGE kind metrics, a time interval could be provided to the API with no start_time
        specified. In this case api client assumes start=end and will try to retrieve a single
        data point. In this application there is not much use for that, but its supported in case
        you are trying to retrieve a single GAUGE metric point.
        We support setting the end time nanoseconds, which is unlikely to be needed in an SLO
        calculation but we do not bother to set the start_nanos.

        Args:
            end_time:       the end of the period, as the time in seconds since the epoch.
                            If a float is provided it is converted to an int regardless
                            (which will round the float down).
            end_time_nanos: Optional. Provide the number of nano seconds that will be added
                            to the end_time.
            start_time:     the start of the period in seconds since the epoch.

        Returns:
            An instance of google.cloud.monitoring_v3.types.TimeInterval()
        """
        interval = monitoring_v3.types.TimeInterval()  # pylint: disable=no-member
        interval.end_time.seconds = int(end_time)
        interval.end_time.nanos = int(end_time_nanos)
        if start_time:
            interval.start_time.seconds = int(start_time)
        return interval
