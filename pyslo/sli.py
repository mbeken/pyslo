import time
from datetime import datetime
from google.cloud import monitoring_v3
import pandas as pd
from .metric_client import MetricClient

MetricDescriptor = monitoring_v3.enums.MetricDescriptor


class SliException():

    class ValueNotSet(Exception):
        pass

    class UnsupportedMetricType(Exception):
        pass


class Sli():

    def __init__(self, metric_client=MetricClient()):
        """
        window_length - number of days over which to calculate the sli
        """
        self.metric_client = metric_client
        self.metric_data = None
        self.duration = None
        self.window_end = time.time()
        self.window_length = 0
        self.slo = None
        self.valid_events = None
        self.good_events = None
        self.group_by_labels = None

    @staticmethod
    def days_to_seconds(days):
        return days*24*60*60

    @property
    def window_length_seconds(self):
        return Sli.days_to_seconds(self.window_length)

    @property
    def window_start(self):
        return self.window_end - self.window_length_seconds

    def calculate(self):
        """
        Calculate SLI based on metric type
        Only boolean is supported right now
        """
        if self.metric_client.value_type == MetricDescriptor.ValueType.BOOL:
            self.calc_bool()
            self.add_period()
            self.add_slo()
            return self.slo_data
        elif self.metric_client.value_type == 'Some other type':
            # TODO
            pass
        else:
            raise SliException.UnsupportedMetricType

    def get_metric_data(self):
        """
        Retrieve metric data from the metric_client

        """
        if self.window_length is None:
            raise SliException.ValueNotSet("window_length cannot be None")
        self.metric_data = self.metric_client.timeseries_dataframe(
            end=self.window_end, duration=self.window_length_seconds
            )

    def get_bool_data(self):
        resampler = self.metric_data.resample(
            '30T', base=0, on='start_timestamp'
            )
        self.good = resampler.sum()
        self.valid = resampler.count()[['value']]

    def calc_bool(self):
        """

        """
        # self.get_metric_data()
        if self.group_by_labels:
            return self.calc_bool_agg()
        else:
            return self.calc_bool_simple()

    def calc_bool_agg(self):
        """
        Calculate sli aggregating over the columns in group_by_labels
        """
        good_events = self.metric_data.groupby(
            self.group_by_labels
            ).sum().reset_index().rename(columns={'value': 'count_good'})

        valid_events = self.metric_data.groupby(
            self.group_by_labels
            ).count().reset_index().rename(columns={'value': 'count_valid'})['count_valid']

        slo_data = good_events.merge(
            valid_events,
            how='left',
            left_index=True,
            right_index=True)

        slo_data['sli'] = slo_data['count_good']/slo_data['count_valid']

        self.slo_data = slo_data
        return self.slo_data

    def calc_bool_simple(self):
        """
        Calculate sli over the entire dataframe with no aggregation by labels
        """
        valid_events = self.metric_data.shape[0]
        good_events = self.metric_data['value'].sum()
        self.slo_data = pd.DataFrame([
            {
                'count_good': good_events,
                'count_valid': valid_events,
                'sli': good_events/valid_events
            }
        ]

        )
        return self.slo_data

    def error_budget(self):
        """
        Using previously calculated good event and valid event count,
        return the error budget, and budget remaining.
        """
        if not self.slo:
            raise SliException.ValueNotSet("slo has not been defined")

        data = self.slo_data
        data['error_budget'] = \
            data['count_valid'] * (1-self.slo)
        data['error_budget_remaining'] = \
            data['error_budget'] - (data['count_valid'] - data['count_good'])
        self.slo_data = data
        return data

    def add_period(self):
        self.slo_data['period_from'] = datetime.fromtimestamp(
            self.window_end - self.window_length_seconds)
        self.slo_data['period_to'] = datetime.fromtimestamp(self.window_end)

    def add_slo(self):
        self.slo_data['slo'] = self.slo

    def add_labels(self):
        pass
