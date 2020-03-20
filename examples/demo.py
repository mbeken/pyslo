from google.cloud import monitoring_v3
from pyslo.metric_client.stackdriver import StackdriverMetricClient
from pyslo.sli import Sli

PROJECT = <MY_GCP_PROJECT>

metric_client = StackdriverMetricClient(project=PROJECT)
metric_client.metric_type = 'composer.googleapis.com/environment/healthy'
metric_client.resource_type = 'cloud_composer_environment'
metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL

sli = Sli(metric_client)

sli.window_length = 1  # days
sli.slo = 0.99

sli.get_metric_data()

# Calculate sli/slo doing no group bys.
sli.calculate()
sli.error_budget()

# Group by some metric labels
sli.group_by_resource_labels = ['environment_name', 'project_id']
sli.group_by_metric_labels = ['image_version']

sli.calculate()
sli.error_budget()
print(sli.slo_data)