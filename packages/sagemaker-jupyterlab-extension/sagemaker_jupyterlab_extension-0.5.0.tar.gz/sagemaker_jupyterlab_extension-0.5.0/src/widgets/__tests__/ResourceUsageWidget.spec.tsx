import React from 'react';
import { render, act } from '@testing-library/react';
import { ResourceUsageWidget } from './../ResourceUsageWidget';
import { ReactWidgetWrapper } from '../../utils/ReactWidgetWrapper';

describe('ResourceUsageWidget suite', () => {
  it('should fetch metrics and update the widget', async () => {
    const resourceUsageWidget = new ResourceUsageWidget();

    // Use act to handle asynchronous updates
    await act(async () => {
      render(<ReactWidgetWrapper item={resourceUsageWidget} />);
      await resourceUsageWidget.getInstanceMetrics();
    });

    // Assertions
    const metricsResponse = resourceUsageWidget.getInstanceMetricsResponse(); // Use the getter method
    expect(metricsResponse).toEqual({
      metrics: {
        memory: {
          rss_in_bytes: 5326798848,
          total_in_bytes: 16287559680,
          memory_percentage: 34.8,
        },
        cpu: {
          cpu_count: 8,
          cpu_percentage: 0.0,
        },
        storage: {
          free_space_in_bytes: 418265493504,
          used_space_in_bytes: 109974339584,
          total_space_in_bytes: 528342487040,
        },
      },
    });
  });
});
