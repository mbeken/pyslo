"""Tests for pyslo.sli
"""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name

import time
import datetime
import pytest
import pandas as pd
from google.cloud import monitoring_v3
from pyslo import sli
from pyslo.metric_client.stackdriver import StackdriverMetricClient

DATA_PATH = './pyslo/tests/data'

@pytest.fixture
def sli_instance():
    '''
    Returns an SLI instance with a dummy metric client
    '''
    return sli.Sli(StackdriverMetricClient(None))


@pytest.fixture
def stackdriver_metric_client():
    """
    Returns a stackdriver metric client instance for testing
    """
    return StackdriverMetricClient(None)


def test_days_to_seconds():
    assert sli.Sli.days_to_seconds(10) == 864000


def test_window_length_seconds(sli_instance):
    assert sli_instance.window_length_seconds == 0

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
    """sli.calculate

    Test the end to end calculate function.
    Provide known input dataset and verify it matches
    known output set. Tests routing to aggregated vs simple
    calculation, as well as routing to correct type calculation (ie BOOL)

    Also tests that slo and period fields are added properly to df

    Currently only BOOL is supported
    """
    # Test that without initiaizing value type it throws
    with pytest.raises(sli.SliException.UnsupportedMetricType):
        sli_instance.calculate()

    # Set to unssuported type and check it throws
    sli_instance.metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.INT64

    with pytest.raises(sli.SliException.UnsupportedMetricType):
        sli_instance.calculate()

    # Load sample boolean data and test boolean non-agg and agg calcs
    sample_df = pd.read_csv(f'{DATA_PATH}/one_day_bool.csv', parse_dates=[0, 1])
    expected = pd.read_csv(
        f'{DATA_PATH}/one_day_bool_no_agg_result.csv',
        parse_dates=[4, 5],
        index_col=0
        )

    window_end = sample_df['end_timestamp'].max()
    sli_instance.window_end = datetime.datetime.timestamp(window_end)
    sli_instance.window_length = 1
    sli_instance.metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL
    sli_instance.slo = 0.99

    sli_instance.metric_data = sample_df
    sli_instance.calculate()
    sli_instance.slo_data['sli'] = sli_instance.slo_data['sli'].round(decimals=9)
    expected['sli'] = expected['sli'].round(decimals=9)

    assert sli_instance.slo_data.equals(expected)

    expected = pd.read_csv(
        f'{DATA_PATH}/one_day_bool_agg_result.csv', parse_dates=[7, 8], index_col=0
        )
    sli_instance.group_by_resource_labels = ['environment_name', 'project_id']
    sli_instance.group_by_metric_labels = ['image_version']
    sli_instance.calculate()

    sli_instance.slo_data['sli'] = sli_instance.slo_data['sli'].round(decimals=9)
    expected['sli'] = expected['sli'].round(decimals=9)
    assert sli_instance.slo_data.equals(expected)


def test_calc_bool(sli_instance):
    """sli.calc_bool
    Tests both the agg and non-agg version of the calc bool.
    Testing the routing to agg vs non-agg
    """
    sample_df = pd.read_csv(f'{DATA_PATH}/one_day_bool.csv', parse_dates=[0, 1])
    expected = pd.read_csv(
        f'{DATA_PATH}/one_day_bool_no_agg_result.csv', parse_dates=[4, 5], index_col=0
        )
    expected.drop(columns=['period_from', 'period_to', 'slo'], inplace=True)

    window_end = sample_df['end_timestamp'].max()
    sli_instance.window_end = datetime.datetime.timestamp(window_end)
    sli_instance.window_length = 1
    sli_instance.metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL
    sli_instance.slo = 0.99

    sli_instance.metric_data = sample_df
    sli_instance.calc_bool()
    sli_instance.slo_data['sli'] = sli_instance.slo_data['sli'].round(decimals=9)
    expected['sli'] = expected['sli'].round(decimals=9)

    assert sli_instance.slo_data.equals(expected)

    expected = pd.read_csv(
        f'{DATA_PATH}/one_day_bool_agg_result.csv', parse_dates=[7, 8], index_col=0
        )
    expected.drop(columns=['period_from', 'period_to', 'slo'], inplace=True)

    sli_instance.group_by_resource_labels = ['environment_name', 'project_id']
    sli_instance.group_by_metric_labels = ['image_version']
    sli_instance.calc_bool()

    sli_instance.slo_data['sli'] = sli_instance.slo_data['sli'].round(decimals=9)
    expected['sli'] = expected['sli'].round(decimals=9)

    assert sli_instance.slo_data.equals(expected)

def test_calc_bool_simple(sli_instance):
    """sli.calc_bool_simple
    Directly test calc_bool_simple
    """
    sample_df = pd.read_csv(f'{DATA_PATH}/one_day_bool.csv', parse_dates=[0, 1])
    expected = pd.read_csv(
        f'{DATA_PATH}/one_day_bool_no_agg_result.csv', parse_dates=[4, 5], index_col=0
        )
    expected.drop(columns=['period_from', 'period_to', 'slo'], inplace=True)

    window_end = sample_df['end_timestamp'].max()
    sli_instance.window_end = datetime.datetime.timestamp(window_end)
    sli_instance.window_length = 1
    sli_instance.metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL
    sli_instance.slo = 0.99

    sli_instance.metric_data = sample_df
    sli_instance.calc_bool_simple()
    sli_instance.slo_data['sli'] = sli_instance.slo_data['sli'].round(decimals=9)
    expected['sli'] = expected['sli'].round(decimals=9)

    assert sli_instance.slo_data.equals(expected)

def test_calc_bool_agg(sli_instance):
    """sli.calc_bool_simple
    Directly test calc_bool_simple
    """
    sample_df = pd.read_csv(f'{DATA_PATH}/one_day_bool.csv', parse_dates=[0, 1])
    expected = pd.read_csv(
        f'{DATA_PATH}/one_day_bool_agg_result.csv', parse_dates=[7, 8], index_col=0
        )
    expected.drop(columns=['period_from', 'period_to', 'slo'], inplace=True)

    window_end = sample_df['end_timestamp'].max()
    sli_instance.window_end = datetime.datetime.timestamp(window_end)
    sli_instance.window_length = 1
    sli_instance.metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL
    sli_instance.slo = 0.99

    sli_instance.metric_data = sample_df
    sli_instance.group_by_resource_labels = ['environment_name', 'project_id']
    sli_instance.group_by_metric_labels = ['image_version']
    sli_instance.calc_bool_agg()
    sli_instance.slo_data['sli'] = sli_instance.slo_data['sli'].round(decimals=9)
    expected['sli'] = expected['sli'].round(decimals=9)

    assert sli_instance.slo_data.equals(expected)

def test_group_by_labels(sli_instance):
    sli_instance.group_by_resource_labels = ['environment_name', 'project_id']
    sli_instance.group_by_metric_labels = ['image_version']
    assert sli_instance.group_by_labels == [
        'resource__environment_name',
        'resource__project_id',
        'metric__image_version'
        ]

def test_error_budget(sli_instance):
    """sli.error_budget
    """
    with pytest.raises(sli.SliException.ValueNotSet):
        sli_instance.error_budget()

    sample_df = pd.read_csv(f'{DATA_PATH}/one_day_bool.csv', parse_dates=[0, 1])
    expected = pd.read_csv(
        f'{DATA_PATH}/one_day_bool_error_budget.csv', parse_dates=[4, 5], index_col=0
        )
    window_end = sample_df['end_timestamp'].max()
    sli_instance.window_end = datetime.datetime.timestamp(window_end)
    sli_instance.window_length = 1
    sli_instance.metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL
    sli_instance.slo = 0.99

    sli_instance.metric_data = sample_df
    sli_instance.calculate()
    sli_instance.error_budget()

    slo_data = sli_instance.slo_data

    assert pytest.approx(slo_data['count_good'], 1E-10) == expected['count_good']
    assert pytest.approx(slo_data['count_valid'], 1E-10) == expected['count_valid']
    assert pytest.approx(slo_data['sli'], 1E-10) == expected['sli']
    assert slo_data['period_from'].equals(expected['period_from'])
    assert slo_data['period_to'].equals(expected['period_to'])
    assert pytest.approx(slo_data['slo'], 1E-10) == expected['slo']
    assert pytest.approx(slo_data['error_budget'], 1E-10) == expected['error_budget']
    assert pytest.approx(
        slo_data['error_budget_remaining'], 1E-10
        ) == expected['error_budget_remaining']

def test_error_budget_agg(sli_instance):
    """sli.error_budget
    """
    with pytest.raises(sli.SliException.ValueNotSet):
        sli_instance.error_budget()

    sample_df = pd.read_csv(f'{DATA_PATH}/one_day_bool.csv', parse_dates=[0, 1])
    expected = pd.read_csv(
        f'{DATA_PATH}/one_day_bool_agg_error_budget.csv', parse_dates=[7, 8], index_col=0
        )
    window_end = sample_df['end_timestamp'].max()
    sli_instance.window_end = datetime.datetime.timestamp(window_end)
    sli_instance.window_length = 1
    sli_instance.metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL
    sli_instance.slo = 0.99

    sli_instance.metric_data = sample_df
    sli_instance.group_by_resource_labels = ['environment_name', 'project_id']
    sli_instance.group_by_metric_labels = ['image_version']
    sli_instance.calculate()
    sli_instance.error_budget()

    slo_data = sli_instance.slo_data
    assert pytest.approx(slo_data['error_budget'], 1E-10) == expected['error_budget']
