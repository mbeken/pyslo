"""Tests for stackdriver filter
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
from pyslo.metric_client.stackdriver import StackDriverFilter

@pytest.fixture
def stackdriver_filter():
    return StackDriverFilter()


def test_validate_types_set(stackdriver_filter):
    with pytest.raises(ValueError):
        stackdriver_filter.validate_types_set()

    stackdriver_filter.metric_type = 'something'
    assert stackdriver_filter.validate_types_set()

def test_string(stackdriver_filter):
    stackdriver_filter.metric_type = 'composer.googleapis.com/environment/healthy'
    expected_filter = 'metric.type="composer.googleapis.com/environment/healthy" '

    assert stackdriver_filter.string == expected_filter

    stackdriver_filter.metric_type = None
    stackdriver_filter.resource_type = 'cloud_composer_environment'
    expected_filter = 'resource.type="cloud_composer_environment" '
    assert stackdriver_filter.string == expected_filter

    stackdriver_filter.metric_type = 'composer.googleapis.com/environment/healthy'
    expected_filter = 'metric.type="composer.googleapis.com/environment/healthy" resource.type="cloud_composer_environment" '
    assert stackdriver_filter.string == expected_filter