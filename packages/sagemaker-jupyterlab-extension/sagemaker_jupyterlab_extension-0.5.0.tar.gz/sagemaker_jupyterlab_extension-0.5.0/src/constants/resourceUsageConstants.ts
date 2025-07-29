type InstanceMetricsResponse = {
  metrics: {
    cpu: {
      cpu_count: number;
      cpu_percentage: number;
    };
    memory: {
      memory_percentage: number;
      rss_in_bytes: number;
      total_in_bytes: number;
    };
    storage: {
      free_space_in_bytes: number;
      used_space_in_bytes: number;
      total_space_in_bytes: number;
    };
  };
};

const MISSING_METRIC_VALUE = '--';
const STORAGE_USAGE_NOTIFICATION_THRESHOLD = 95;

const RESOURCE_USAGE_METRICS_RETRIES = 2;
export {
  InstanceMetricsResponse,
  MISSING_METRIC_VALUE,
  RESOURCE_USAGE_METRICS_RETRIES,
  STORAGE_USAGE_NOTIFICATION_THRESHOLD,
};
