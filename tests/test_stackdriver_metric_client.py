"""Tests for pyslo.metric_client
"""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=wrong-import-position
# pylint: disable=protected-access
# pylint: disable=no-member

import sys
import os
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    )
import datetime
import pytest
import pytz
from google.cloud import monitoring_v3
import google.protobuf as protobuf
from pyslo.metric_client.stackdriver import StackdriverMetricClient


@pytest.fixture
def stackdriver_metric_client():
    """
    Returns a stackdriver metric client instance for testing
    """
    return StackdriverMetricClient(None)

def test_metric_type(stackdriver_metric_client):
    stackdriver_metric_client.metric_type = 'something_crazy'
    assert stackdriver_metric_client.metric_type == 'something_crazy'
    assert stackdriver_metric_client._filter.metric_type == 'something_crazy'

def test_resource_type(stackdriver_metric_client):
    stackdriver_metric_client.resource_type = 'a_crazy_resource'
    assert stackdriver_metric_client.resource_type == 'a_crazy_resource'
    assert stackdriver_metric_client._filter.resource_type == 'a_crazy_resource'    

def test_filter(stackdriver_metric_client):
    stackdriver_metric_client.metric_type = 'composer.googleapis.com/environment/healthy'
    assert stackdriver_metric_client._filter.string == 'metric.type="composer.googleapis.com/environment/healthy" '
    

def test_set_interval(stackdriver_metric_client):
    end_time = 123456
    interval = stackdriver_metric_client.set_interval(
        end_time=end_time
    )
    assert interval.end_time.seconds == 123456
    assert interval.end_time.nanos == 0
    assert interval.start_time.seconds == 0
    assert interval.start_time.nanos == 0

def test_get_point_value(stackdriver_metric_client):
    stackdriver_metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL
    point_value = monitoring_v3.types.TypedValue()  # pylint: disable=no-member

    point_value.bool_value = True
    assert stackdriver_metric_client.get_point_value(point_value)

    point_value.bool_value = False
    assert not stackdriver_metric_client.get_point_value(point_value)

def test_convert_point_time():
    timestamp = protobuf.timestamp_pb2.Timestamp()
    timestamp.seconds = 1584627079
    timestamp.nanos = 123456789

    d_t = StackdriverMetricClient.convert_point_time(timestamp, as_timestamp=False)
    assert d_t.day == 19
    assert d_t.month == 3
    assert d_t.year == 2020
    assert d_t.hour == 14
    assert d_t.minute == 11
    assert d_t.second == 19
    assert d_t.microsecond == 123457

    tsp = StackdriverMetricClient.convert_point_time(timestamp, as_timestamp=True)
    assert tsp == 1584627079.123456789

def test_prepend_label_names():
    labels = {
        'key':'value'
    }
    prepended_labels = StackdriverMetricClient.prepend_label_names(labels, 'pre')
    assert prepended_labels == {
        'pre__key':'value'
    }


def test_prepend_key():
    key = 'my_key'
    prepend = 'before'
    expected = 'before__my_key'
    assert StackdriverMetricClient.prepend_key(key, prepend) == expected

def test_get_labels():
    result = monitoring_v3.types.TimeSeries()  # pylint: disable=no-member
    result.resource.labels['r1'] = 'r_value1'
    result.resource.labels['r2'] = 'r_value2'
    assert StackdriverMetricClient.get_labels(result) == {
        'resource__r1':'r_value1',
        'resource__r2':'r_value2'
        }

    result.metric.labels['m1'] = 'm_value1'
    result.metric.labels['m2'] = 'm_value2'
    assert StackdriverMetricClient.get_labels(result) == {
        'resource__r1':'r_value1',
        'resource__r2':'r_value2',
        'metric__m1':'m_value1',
        'metric__m2':'m_value2',
    }

def test_point_dict(stackdriver_metric_client):
    point = monitoring_v3.types.Point()
    point.interval.end_time.seconds = 1584627079
    point.interval.end_time.nanos = 123456789
    point.interval.start_time.seconds = point.interval.end_time.seconds - (24*60*60)
    point.interval.start_time.nanos = point.interval.end_time.nanos
    point.value.bool_value = True

    labels = {'label1':'some_value', 'label2':'some_other_value'}

    stackdriver_metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL

    expected = {
        'start_timestamp': datetime.datetime(2020, 3, 18, 14, 11, 19, 123457, tzinfo=pytz.UTC),
        'end_timestamp': datetime.datetime(2020, 3, 19, 14, 11, 19, 123457, tzinfo=pytz.UTC),
        'value': 1,
        'label1': 'some_value',
        'label2': 'some_other_value'
        }

    assert stackdriver_metric_client.point_dict(point, labels) == expected
