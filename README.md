# pyslo 
Calculate service level objective measurements from metrics stored in common backends in accordance with the logic set out in the [SRE Workbook](https://landing.google.com/sre/workbook/toc/)

# Getting Started

### Installation process
```sh
pip install pyslo
```

# Build and Test
```sh
pytest
```
# Current Support
## Providers
At this time, the [Stackdriver](https://cloud.google.com/monitoring/api/metrics_gcp) backend is supported. Future plans include Prometheus and [Azure Monitoring](https://docs.microsoft.com/en-us/azure/azure-monitor/platform/rest-api-walkthrough)

## Metric Types
### Stackdriver
*  Boolean

# Logic

The library pulls raw timeseries data from the metric provider and performs aggregations in memory. This is in order to standardize the computation across providers.
## Boolean Metrics

sli = good_events/valid_events

where 
*  good events = (sum of metric entries == True)
*  valic_events = (sum of metric entries)

# Examples
## Google Cloud StackDriver
This example uses a metric provided by GCP for the Composer service.
```py
from google.cloud import monitoring_v3
from pyslo.metric_client import StackdriverMetricClient
from pyslo.sli import Sli

PROJECT = <>

metric_client = StackdriverMetricClient(project=PROJECT)
metric_client.metric_type = 'composer.googleapis.com/environment/healthy'
metric_client.value_type = monitoring_v3.enums.MetricDescriptor.ValueType.BOOL

sli = Sli(metric_client)

sli.window_length = 30  # days
sli.slo = 0.99

sli.get_metric_data()

# Calculate sli/slo doing no group bys.
sli.calculate()
sli.error_budget()
print(sli.slo_data)

# Group by some metric labels
sli.group_by_labels = ['environment_name', 'project_id']
sli.calculate()
sli.error_budget()
print(sli.slo_data)
```
