import os
import sys
import pandas as pd
from google.cloud import monitoring_v3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from pyslo.metric_client.stackdriver import StackdriverMetricClient
from pyslo import sli

TEST_DATA_PATH = './tests/data'

metric_client = StackdriverMetricClient(project='slb-it-op-dev')
metric_client.metric_type = 'composer.googleapis.com/environment/healthy'
metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL


sli = sli.Sli(metric_client)
sli.window_length = 1
sli.slo = 0.99
# sli.get_metric_data()
# sli.metric_data.to_csv('one_day_bool.csv', index=False)
sample_df = pd.read_csv(f'{TEST_DATA_PATH}/one_day_bool.csv', parse_dates=[0,1])
window_end = sample_df['end_timestamp'].max()
window_length = 1

sli.window_end = datetime.datetime.timestamp(window_end)
sli.window_length = 1
sli.metric_data = sample_df
sli.group_by_resource_labels = ['environment_name', 'project_id']
sli.group_by_metric_labels = ['image_version']
sli.calculate()
# sli.slo_data.to_csv(f'{TEST_DATA_PATH}/one_day_bool_agg_result.csv')

error = sli.error_budget()
error.to_csv(f'{TEST_DATA_PATH}/one_day_bool_agg_error_budget.csv')

