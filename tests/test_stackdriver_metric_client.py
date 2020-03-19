"""Tests for pyslo.metric_client
"""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=wrong-import-position

import sys
import os
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    )
import pytest
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
