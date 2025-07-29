import React from 'react';
import { InstanceMetricsResponse } from '../constants/resourceUsageConstants';
import { INSTANCE_METRICS_URL, METRICS_FETCH_INTERVAL_IN_MILLISECONDS } from '../service/constants';
import { fetchApiResponse, OPTIONS_TYPE } from '../service';
import { ReactWidget } from '@jupyterlab/apputils';
import { ResourceUsageComponent } from './../components/ResourceUsageComponent';

class ResourceUsageWidget extends ReactWidget {
  private _instanceMetricsResponse: InstanceMetricsResponse | null;
  private _instanceMetricsDisplayValue: number | undefined;

  constructor() {
    super();
    this._instanceMetricsResponse = null;
    this._instanceMetricsDisplayValue = undefined;
  }

  public getInstanceMetricsResponse(): InstanceMetricsResponse | null {
    return this._instanceMetricsResponse;
  }

  clickHandler = () => {
    this.update();
    // @TODO: record telemetry on click
    // this.telemetry.record({
    //   schema: TelemetrySchemas.TelemetryUserAction,
    //   action: TelemetryActionTypes.RemoteStatusMetricsOpen,
    //   how: TelemetryUserActionEventTypes.Click,
    // });
  };

  /**
   * Fetches and parses instance and kernel metrics
   */
  getInstanceMetrics = async () => {
    // @TODO: update the type
    await fetchApiResponse(INSTANCE_METRICS_URL, OPTIONS_TYPE.GET).then((result: any) => {
      result &&
        result.json().then((data: any) => {
          this._instanceMetricsResponse = data ? (data as InstanceMetricsResponse) : null;
          if (this._instanceMetricsResponse?.metrics.memory) {
            this._instanceMetricsDisplayValue = this._instanceMetricsResponse?.metrics.memory.memory_percentage;
          } else {
            this._instanceMetricsDisplayValue = undefined;
          }
        });
    });

    this.update();
  };

  render() {
    return (
      <ResourceUsageComponent
        onClickHandler={this.clickHandler}
        instanceMetricsResponse={this._instanceMetricsResponse}
        instanceMetricsDisplayValue={this._instanceMetricsDisplayValue}
      />
    );
  }

  // Using interval to schedule the repetitive task to fetch metrics.
  _getInstanceMetricsLoop = setInterval(this.getInstanceMetrics, METRICS_FETCH_INTERVAL_IN_MILLISECONDS);
}

export { ResourceUsageWidget };
