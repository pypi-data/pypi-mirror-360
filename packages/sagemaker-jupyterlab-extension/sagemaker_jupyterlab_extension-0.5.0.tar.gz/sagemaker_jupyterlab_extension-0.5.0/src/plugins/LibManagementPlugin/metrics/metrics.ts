/**
 * Metrics utility for CloudWatch Embedded Metric Format
 * Provides functionality to record and log metrics for library management operations
 */
import { ServerConnection } from '@jupyterlab/services';
import { PageConfig } from '@jupyterlab/coreutils';

// Data structure for metric information
export interface MetricData {
  latency?: number;
  success?: number;
  error?: number;
  output?: string;
  [key: string]: any;
}

// Definition of a CloudWatch metric
interface MetricDefinition {
  Name: string;
  Unit?: string;
  StorageResolution?: number;
}

// Structure for CloudWatch metric configuration
interface CloudWatchMetric {
  Namespace: string;
  Dimensions: string[][];
  Metrics: MetricDefinition[];
}

// Complete metric object in CloudWatch Embedded Metric Format
interface MetricObject {
  _aws: {
    Timestamp: number;
    CloudWatchMetrics: CloudWatchMetric[];
  };
  Operation: string;
  [key: string]: any;
}

// Simple metrics service for sending custom metrics to the server
class MetricsService {
  private baseUrl: string;
  private settings: ServerConnection.ISettings;

  constructor() {
    this.baseUrl = PageConfig.getBaseUrl();
    this.settings = ServerConnection.makeSettings({ baseUrl: this.baseUrl });
  }

  /**
   * Send a metric to the server
   *
   * @param metricData - The metric data to send
   * @param output - Optional output data to print to local log
   * @returns A promise that resolves when the metric is sent
   */
  async sendMetric(metricData: any, output?: string): Promise<void> {
    // Ensure the URL has a leading slash
    const url = `${this.baseUrl}aws/sagemaker/api/add-metrics`;

    // Create request body with metric and optional output
    const requestBody = {
      metric: metricData,
      ...(output && { output }),
    };

    // Convert to JSON string
    const body = JSON.stringify(requestBody);

    // Set proper headers
    const init = {
      method: 'POST',
      body,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    // Send the metric to the server
    const response = await ServerConnection.makeRequest(url, init, this.settings);

    if (!response.ok) {
      throw new Error(`Failed to send metric: ${response.statusText}`);
    }
  }
}

// Create a singleton instance
const metricsService = new MetricsService();

/**
 * Records a metric in CloudWatch Embedded Metric Format and writes it to the log file
 *
 * @param operation - The operation name being measured
 * @param data - Metric data including latency, success, error counts, and output
 * @param namespace - CloudWatch namespace for the metrics
 */
export function recordMetric(operation: string, data: MetricData, namespace = 'Extension Management'): void {
  const timestamp = Date.now();

  const metric: MetricObject = {
    _aws: {
      Timestamp: timestamp,
      CloudWatchMetrics: [
        {
          Namespace: namespace,
          Dimensions: [['Operation']],
          Metrics: [],
        },
      ],
    },
    Operation: operation,
  };

  if (data.latency !== undefined) {
    metric._aws.CloudWatchMetrics[0].Metrics.push({
      Name: 'Latency',
      Unit: 'Milliseconds',
    });
    metric['Latency'] = data.latency;
  }

  if (data.success !== undefined) {
    metric._aws.CloudWatchMetrics[0].Metrics.push({
      Name: 'Success',
      Unit: 'Count',
    });
    metric['Success'] = data.success;
  }

  if (data.error !== undefined) {
    metric._aws.CloudWatchMetrics[0].Metrics.push({
      Name: 'Error',
      Unit: 'Count',
    });
    metric['Error'] = data.error;
  }

  Object.keys(data).forEach((key) => {
    if (!['latency', 'success', 'error', 'output'].includes(key.toLowerCase())) {
      metric._aws.CloudWatchMetrics[0].Metrics.push({
        Name: key,
        Unit: 'None',
      });
      metric[key] = data[key];
    }
  });

  // Write to log file
  void writeMetricToLogFile(JSON.stringify(metric), data.output);
}

/**
 * Writes metric data to the SageMaker Studio log file
 * Uses the metrics service to send metrics to the server API
 *
 * @param metricString - JSON string containing the metric data
 * @param output - Optional output data to include separately
 */
async function writeMetricToLogFile(metricString: string, output?: string): Promise<void> {
  const metricObject = JSON.parse(metricString);
  await metricsService.sendMetric(metricObject, output);
}
