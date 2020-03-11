import os
import sys
import pandas as pd
from google.cloud import monitoring_v3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from sli.metric_client import StackdriverMetricClient
from sli import sli

metric_client = StackdriverMetricClient(project='slb-ads-eds-dev')
metric_client.metric_type = 'composer.googleapis.com/environment/healthy'
metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL


sli_ = sli.Sli(metric_client)
sli_.window_length = 30
# sli_.get_metric_data()
# sli_.metric_data.to_csv('one_month.csv', index=False)
sample_df = pd.read_csv('one_month.csv', parse_dates=[0,1])

sli_.metric_data = sample_df

# sli_.get_bool_data()
# sli_.good.to_csv('./tests/data/sample_good.csv')
# sli_.valid.to_csv('./tests/data/sample_valid.csv')