"""Stackdriver specific MetricClient
"""

import time
import datetime
import pytz
import pandas as pd
from google.cloud import monitoring_v3
from ..metric_client import MetricClient
from ..metric_client import NoMetricDataAvailable
from .stackdriver_filter import StackDriverFilter

MetricDescriptor = monitoring_v3.enums.MetricDescriptor


class StackdriverMetricClient(MetricClient):
    """Stackdriver Metric Client

    This client will allow you to retrieve metrics from a Stackdriver
    monitoring instance.

    Attributes:
        project:        string. id of the GCP project hosting Stackdriver
        metric_type:    string. the metric type as defined in Stackdriver.
                        e.g. composer.googleapis.com/environment/healthy
                        This is most easily found by locating the metric in StackDriver Metrics
                        Explorer, then viewing as JSON.
                        The metric type is found as part of the timeSeriesFilter.
        resource_type:  string. the resource type as defined in Stackdriver.
                        This is most easily found by locating the metric in StackDriver Metrics
                        Explorer, then viewing as JSON.
                        The resource type is found as part of the timeSeriesFilter.    
        value_type:     metric type, as a type defined in google.cloud.monitoring_v3
                        e.g. monitoring_v3.enums.MetricDescriptor.ValueType.BOOL


    """

    def __init__(self, project):
        self.project = project
        self._metric_type = None
        self._resource_type = None
        self.value_type = None
        self._filter = StackDriverFilter()

        self._client = monitoring_v3.MetricServiceClient()

    @property
    def metric_type(self):
        return self._metric_type

    @metric_type.setter
    def metric_type(self, metric_type):
        self._filter.metric_type = metric_type
        self._metric_type = metric_type

    @property
    def resource_type(self):
        return self._resource_type

    @resource_type.setter
    def resource_type(self, resource_type):
        self._filter.resource_type = resource_type
        self._resource_type = resource_type

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
        return self.to_df(iterator)


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
            self._filter.string,
            interval,
            monitoring_v3.enums.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        return results_iter

    @staticmethod
    def get_labels(result):
        """Extract the resource and labels from the result object.

        Args:
            result:

        Returns:
            a dict type object with the labels. 
            Resource labels have the key resource__labelname.
            Metric labels have the key metric__labelname.
        """
        resource_labels = result.resource.labels
        metric_labels = result.metric.labels
        r = StackdriverMetricClient.prepend_label_names(resource_labels, 'resource')
        m = StackdriverMetricClient.prepend_label_names(metric_labels, 'metric')

        return {**r, **m}

    @staticmethod
    def prepend_label_names(labels, prepend):
        """For a dictionary of labels, prepend the keys

        Args:
            labels: dictionary of labels
            prepend: string. Value with which to prepend the keys

        Returns:
            A dictionary
        """
        x = [(StackdriverMetricClient.prepend_key(k, prepend), v) for k, v in labels.items()]
        return dict(x)

    @staticmethod
    def prepend_key(key, prepend):
        """Prepends a key

        Args:
            key: string value of the dictionary key
            prepend: string value to be prepended to the key
        
        Returns:
            A string
        """
        return f'{prepend}__{key}'

    def to_df(self, iterator):
        """Transform a results iterator to a Dataframe.

        For a google.api_core.page_iterator.GRPCIterator, create a dataframe.
        Dastaframe will include the result resource and metric labels as
        columns. To prevent possible conflicts, resource labels are prepended with
        resource__ and metrics with metric__.

        Args:
            iterator: google.api_core.page_iterator.GRPCIterator that gets returned
            from the Stackdriver API

        Returns:
            A Dataframe containing the timeseries data and metric/resource labels.
        """
        points = list()
        for result in iterator:
            labels = self.get_labels(result)
            for point in result.points:
                points.append(self.point_dict(point, labels))
        if len(points) == 0:
            raise NoMetricDataAvailable

        return pd.DataFrame(points)


    def point_dict(self, point, labels):
        """Convert Point object to dictionary

        Args:
            point: google.cloud.monitoring_v3.types.Point
            labels: dictionary of the metric and resource labels

        Returns:
            a dictionary containing the points value, start and end time
            and labels
        """
        point_dict = {
            'start_timestamp': StackdriverMetricClient.convert_point_time(
                point.interval.start_time,
                as_timestamp=False
                ),
            'end_timestamp': StackdriverMetricClient.convert_point_time(
                point.interval.end_time,
                as_timestamp=False
                ),
            'value': self.get_point_value(point.value)
            }
        point_dict.update(labels)
        return point_dict

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
