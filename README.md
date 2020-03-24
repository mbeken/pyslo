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

# Documentation

Visit [readthedocs](https://pyslo.readthedocs.io/en/latest/pyslo.html) for full documentation.

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

