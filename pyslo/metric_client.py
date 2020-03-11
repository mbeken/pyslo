import time
import datetime
import pandas as pd
from google.cloud import monitoring_v3

MetricDescriptor = monitoring_v3.enums.MetricDescriptor


class NoMetricDataAvailable(Exception):
    pass


class MetricClient():
    
    value_type = None


class StackdriverMetricClient(MetricClient):

    def __init__(self, project):
        """
        resource:- instance of the resource actually retrieved from the API
        """
        self.project = project
        self.client = monitoring_v3.MetricServiceClient()
        self.metric_type = None
        self.value_type = None
        self.resource = None

    def timeseries_dataframe(self, end=time.time(), duration=3600):
        """
        By default this will retrieve the last hours worth of data.
        By specifying duration you will get that amount of data from now back.
        If you want a custom range then specify both end and duration.

        end:- the end of the period, as the time in seconds since the epoch as
        a floating point number.
        duration:- length of the period to retrieve in seconds
        """
        iter = self.get_timeseries_iter(end, duration=duration)
        materialized = StackdriverMetricClient.fetch_iter_results(iter)
        return self.to_df(materialized)

    @property
    def filter(self):
        """
        Return a monitoring filter that specifies which time series should be
        returned.
        The filter must specify a single metric type, and can additionally
        specify metric labels and other information. For example:

        metric.type = "compute.googleapis.com/instance/cpu/usage_time" AND
            metric.labels.instance_name = "my-instance-name"

        Todo: - for now we are just making the simplest case filter!
        """
        return f'metric.type = "{self.metric_type}"'

    def get_timeseries_iter(self, end, duration=None):
        interval = StackdriverMetricClient.set_interval(end, end-duration)
        project_name = self.client.project_path(self.project)
        results_iter = self.client.list_time_series(
            project_name,
            self.filter,
            interval,
            monitoring_v3.enums.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        return results_iter

    def get_labels(self, result):
        """
        Return the resource labels from the result object
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
            for point in result.points:
                start_time = StackdriverMetricClient.convert_point_time(
                    point.interval.start_time
                    )

                end_time = StackdriverMetricClient.convert_point_time(
                    point.interval.end_time
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
        if self.value_type == MetricDescriptor.ValueType.BOOL:
            return int(point_value.bool_value)
        else:
            raise Exception

    @staticmethod
    def convert_point_time(point_time):
        seconds = point_time.seconds
        nanos = point_time.nanos
        return datetime.datetime.fromtimestamp(seconds + nanos/10**9)

    @staticmethod
    def fetch_iter_results(iter):
        results = list()
        for result in iter:
            results.append(result)
        return results

    @staticmethod
    def set_interval(end_time, start_time=None):
        """
        We've decided to not care about nano seconds for this implementation.
        """
        interval = monitoring_v3.types.TimeInterval()
        interval.end_time.seconds = int(end_time)
        if start_time:
            interval.start_time.seconds = int(start_time)
        return interval
