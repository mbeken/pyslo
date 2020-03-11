import os
import sys
import time
import pytest
from google.cloud import monitoring_v3
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    )

from sli import sli
from sli.metric_client import StackdriverMetricClient


@pytest.fixture
def sli_instance():
    '''
    Returns an SLI instance with a dummy metric client
    '''
    return sli.Sli()


@pytest.fixture
def stackdriver_metric_client():
    """
    Returns a stackdriver metric client instance for testing
    """
    return StackdriverMetricClient(None)


def test_days_to_seconds():
    assert sli.Sli.days_to_seconds(10) == 864000


def test_window_length_seconds(sli_instance):
    sli_instance.window_length = 10
    assert sli_instance.window_length_seconds == 864000


def test_window_length_start(sli_instance):
    now = time.time()
    window_length_days = 10
    expected_window_start = now - (10*24*60*60)

    sli_instance.window_end = now
    sli_instance.window_length = window_length_days
    assert sli_instance.window_start == expected_window_start


def test_calculate(sli_instance):
    with pytest.raises(sli.SliException.UnsupportedMetricType):
        sli_instance.calculate()

    value_type = monitoring_v3.enums.MetricDescriptor.ValueType.INT64
    stackdriver_metric_client.value_type = value_type
    sli_instance.metric_client = stackdriver_metric_client

    with pytest.raises(sli.SliException.UnsupportedMetricType):
        sli_instance.calculate()
    

# def test_sli_get_bool_data(sli_instance):
#     sample_df = pd.read_csv('./tests/data/sample_bool.csv', parse_dates=[0,1])
#     sample_good = pd.read_csv('./tests/data/sample_good.csv', parse_dates=[0], index_col=0)
#     sample_valid = pd.read_csv('./tests/data/sample_valid.csv', parse_dates=[0], index_col=0)

    # sli_instance.metric_data = sample_df
    # sli_instance.get_bool_data()

    # assert sli_instance.good.equals(sample_good)
    # assert sli_instance.valid.equals(sample_valid)


def test_error_budget(sli_instance):
    with pytest.raises(sli.SliException.ValueNotSet):
        sli_instance.error_budget()

    sli_instance.slo = 0.99
    # sli_instance.error_budget()
