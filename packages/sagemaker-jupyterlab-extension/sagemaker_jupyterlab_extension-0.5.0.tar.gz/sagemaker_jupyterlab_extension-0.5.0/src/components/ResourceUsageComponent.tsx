import React, { useState, FC, useEffect } from 'react';
import { il18Strings } from '../constants';
import * as styles from './../widgets/styles/resourceUsageStyle';
import LinearProgress from '@mui/material/LinearProgress';
import { LinearProgressWithLabel } from '../components/common/LinearProgressWithLabel';
import {
  InstanceMetricsResponse,
  MISSING_METRIC_VALUE,
  STORAGE_USAGE_NOTIFICATION_THRESHOLD,
} from '../constants/resourceUsageConstants';
import { Notification } from '@jupyterlab/apputils';

const smJupyterLabPrefix = 'jlStudio-';
const instanceMetricsClassNames = {
  widgetContainer: `${smJupyterLabPrefix}ResourceUsageWidgetContainer`,
  metricsContainer: `${smJupyterLabPrefix}MetricsWidgetContainer`,
};

interface ResourceUsageComponentProps {
  onClickHandler: any;
  instanceMetricsResponse: InstanceMetricsResponse | null;
  instanceMetricsDisplayValue: number | undefined;
}

const ResourceUsageComponent: FC<ResourceUsageComponentProps> = ({
  onClickHandler,
  instanceMetricsResponse,
  instanceMetricsDisplayValue,
}) => {
  const [openMetricWindow, setOpenMetricWindow] = useState<boolean>(false);
  const [cpuUsage, setCpuUsage] = useState<undefined | number>(0);
  const [memoryUsage, setMemoryUsage] = useState<undefined | number>(0);
  const [storageUsage, setStorageUsage] = useState<undefined | number>(0);
  const [displayStorageFullNotification, setDisplayStorageFullNotification] = useState<boolean>(false);

  const clickHandler = (openMetricWindow: boolean) => {
    setOpenMetricWindow(!openMetricWindow);
    onClickHandler();
  };

  const getMetricValue = (metric: number | undefined) => {
    return metric && metric !== undefined ? Math.round(metric) : 0;
  };

  const getMetricDisplayValue = (metric: number | undefined) => {
    if (metric === 0) {
      return '0.0';
    }
    return metric && metric !== undefined ? metric.toFixed(2).toString() : MISSING_METRIC_VALUE;
  };

  useEffect(() => {
    if (instanceMetricsResponse !== undefined && instanceMetricsResponse?.metrics) {
      const { metrics } = instanceMetricsResponse;

      const cpuUsage = metrics.cpu.cpu_percentage;
      const memoryUsage = metrics.memory.memory_percentage;

      const usedStorageInBytes = metrics.storage.used_space_in_bytes;
      const totalStorageInBytes = metrics.storage.total_space_in_bytes;
      const storageUsage =
        usedStorageInBytes && totalStorageInBytes && (usedStorageInBytes / totalStorageInBytes) * 100;

      setCpuUsage(cpuUsage);
      setMemoryUsage(memoryUsage);
      setStorageUsage(storageUsage);
    }
  }, [instanceMetricsResponse]);

  useEffect(() => {
    if (
      storageUsage &&
      storageUsage > STORAGE_USAGE_NOTIFICATION_THRESHOLD &&
      displayStorageFullNotification === false
    ) {
      const { stoargeSpaceLimitDialog } = il18Strings.ResourceUsage;
      Notification.info(stoargeSpaceLimitDialog.title);
      setDisplayStorageFullNotification(true);
    }
  }, [displayStorageFullNotification, storageUsage]);

  const {
    instanceMemoryProgressBarTitle,
    instanceMetricsTitle,
    cpuMetricTitle,
    memoryMetricTitle,
    storageMetricTitle,
  } = il18Strings.ResourceUsage;

  return (
    <div
      data-testid={'resource-usage-widget'}
      data-analytics-type="eventContext"
      data-analytics="JupyterLab"
      className={`${instanceMetricsClassNames.widgetContainer} ${styles.RemoteStatusContainer}`}
    >
      <div
        className={styles.ResourceWidgetConatiner}
        onClick={() => clickHandler(openMetricWindow)}
        data-testid={'resource-usage-widget-click-handler'}
        data-analytics-type="eventDetail"
        data-analytics="ResourceUsage-Widget-Click"
      >
        {instanceMemoryProgressBarTitle}{' '}
        {instanceMetricsDisplayValue === undefined ? (
          <LinearProgress
            data-testid={'resource-usage-linear-progress-spinner'}
            className={styles.StatusBarProgressBarContainerStyle}
          />
        ) : (
          <div className={styles.ResourceWidgetConatiner} data-testid={'resource-usage-status-bar-container'}>
            <LinearProgress
              className={styles.StatusBarProgressBarContainerStyle}
              variant="determinate"
              value={instanceMetricsDisplayValue | 0}
            />
            {instanceMetricsDisplayValue ? Math.round(instanceMetricsDisplayValue) : 0}%
          </div>
        )}
      </div>
      {openMetricWindow && (
        <div
          className={`${instanceMetricsClassNames.metricsContainer} ${styles.MetricsWindowStyle}`}
          data-testid={'resource-usage-data-container'}
        >
          <div className={styles.KernelMetricContainer}>
            <div className={styles.MetricsTitleStyle}>{instanceMetricsTitle}</div>
            <div className={styles.MetricsContainerStyle}>
              <div>
                <LinearProgressWithLabel
                  value={getMetricValue(cpuUsage)}
                  displayValue={getMetricDisplayValue(cpuUsage)}
                  label={cpuMetricTitle}
                  labelClassName={styles.SingleMetricLabel}
                  singleProgressBarStyle={styles.SingleProgressBarStyle}
                  conatinerClassName={styles.SingleMetricContainer}
                  data-testid={'resource-usage-data-container-cpu'}
                />
                <LinearProgressWithLabel
                  value={getMetricValue(memoryUsage)}
                  displayValue={getMetricDisplayValue(memoryUsage)}
                  label={memoryMetricTitle}
                  labelClassName={styles.SingleMetricLabel}
                  singleProgressBarStyle={styles.SingleProgressBarStyle}
                  conatinerClassName={styles.SingleMetricContainer}
                  data-testid={'resource-usage-data-container-memory'}
                />
                <LinearProgressWithLabel
                  value={getMetricValue(storageUsage)}
                  displayValue={getMetricDisplayValue(storageUsage)}
                  label={storageMetricTitle}
                  labelClassName={styles.SingleMetricLabel}
                  singleProgressBarStyle={styles.SingleProgressBarStyle}
                  conatinerClassName={styles.SingleMetricContainer}
                  data-testid={'resource-usage-data-container-storage'}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export { ResourceUsageComponent };
