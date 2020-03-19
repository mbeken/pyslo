class StackDriverFilter():
    """Hold variables and generate filter strings.
    metric.type="composer.googleapis.com/environment/healthy"
    resource.type="cloud_composer_environment"
    resource.label."project_id"="slb-it-op-dev"
    metric.label."image_version"="composer-1-7-1-airflow-1-10-2"
    resource.label."location"="europe-west1"
    """

    def __init__(self):
        self.metric_type = None
        self.resource_type = None
        self.resource_labels = []
        self.metric_labels = []

    @property
    def string(self):
        """Create a filter string based on properties
        Args:

        Returns:
            A string that can be passed as the filter_ arg during a MetricServiceClient
            list_time_series call.  The filter specifies which time series data is being requested.
            The filter must specify a single metric type, and can additionally
            specify metric labels and other information. For example:

            metric.type = "compute.googleapis.com/instance/cpu/usage_time" AND
                metric.labels.instance_name = "my-instance-name"
        """
        filter_string = ""
        self.validate_types_set()
        if self.metric_type:
            filter_string += f'metric.type="{self.metric_type}" '
        if self.resource_type:
            filter_string += f'resource.type="{self.resource_type}" '
        return filter_string

    def validate_types_set(self):
        if not self.metric_type and not self.resource_type:
            raise ValueError("Either metric_type or resource_type must be set")
        else:
            return True
  