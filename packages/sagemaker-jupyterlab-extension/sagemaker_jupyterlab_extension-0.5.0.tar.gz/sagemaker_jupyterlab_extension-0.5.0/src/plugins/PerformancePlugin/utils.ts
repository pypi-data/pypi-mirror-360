import { JupyterFrontEnd } from '@jupyterlab/application';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';

const TIME_TO_APP_STARTED_MARK = 'timeToAppStarted';

/* Added TimeToAppRestored metric, since app restored promise is the promise Jupyter use to remove
 * spinning logo from DOM
 * https://github.com/jupyterlab/jupyterlab/blob/aceec90efae52744fdae75ca73ccaf0118e7ad7d/packages/apputils-extension/src/index.ts#L240-L253,
 * https://github.com/jupyterlab/jupyterlab/blob/aceec90efae52744fdae75ca73ccaf0118e7ad7d/packages/application/src/lab.ts#L29,
 * https://github.com/jupyterlab/jupyterlab/blob/aceec90efae52744fdae75ca73ccaf0118e7ad7d/packages/application/src/shell.ts#L646
 */
const TIME_TO_APP_RESTORED_MARK = 'timeToAppRestored';

const SM_NAMESPACE = 'AWSSageMakerUI';

const positiveValueOrNull = (value: number) => {
  return value > 0 ? value : null;
};

const reportClientPerformance = (logger: ILogger, app: JupyterFrontEnd): void => {
  const resources = window?.performance.getEntriesByType('resource');
  let metricsToReport = {};
  if (Array.isArray(resources) && resources.length > 0) {
    resources.forEach((entry) => {
      const { duration, requestStart, responseStart, startTime } = entry as PerformanceResourceTiming;

      // If Timing-Allow-Origin is not included in cross-origin response,
      // we won't have access to timing information for this resource
      // see: https://www.w3.org/TR/resource-timing/#cross-origin-resources
      //
      // OR if timing.duration is empty, this resource was served from browser cache

      if (requestStart && duration) {
        metricsToReport = {
          ...metricsToReport,
          TimeToFirstByteMS: Math.round(responseStart - startTime),
        };
      }
    });
  }

  // log immediately available performance metrics
  let redirectCount = null;
  let redirectTime = null;
  let timeToDOMContentLoaded = null;
  let timeToFirstByte = null;
  let timeToOnLoad = null;

  const navigationEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming; // Navigation Timing Level 2 specification, in experimental stage
  if (!navigationEntry) {
    const timing = performance.timing; // deprecated Web API PerformanceTiming, but it has good browser compatibility
    redirectCount = performance.navigation.redirectCount; // deprecated Web API PerformanceNavigation, but it has good browser compatibility
    redirectTime = timing.redirectEnd - timing.redirectStart;
    timeToDOMContentLoaded = timing.domContentLoadedEventEnd - timing.navigationStart;
    timeToFirstByte = timing.responseStart - timing.navigationStart;
    timeToOnLoad = timing.loadEventEnd - timing.navigationStart;
  } else {
    redirectCount = navigationEntry.redirectCount;
    redirectTime = navigationEntry.redirectEnd - navigationEntry.redirectStart;
    timeToDOMContentLoaded = Math.round(navigationEntry.domContentLoadedEventEnd);
    timeToFirstByte = Math.round(navigationEntry.responseStart);
    timeToOnLoad = Math.round(navigationEntry.loadEventEnd);
  }

  metricsToReport = {
    ...metricsToReport,
    RedirectCount: redirectCount,
    RedirectTimeMS: redirectTime,
    TimeToDOMContentLoadedMS: timeToDOMContentLoaded,
    TimeToFirstByteMS: timeToFirstByte,
    TimeToOnLoadMS: timeToOnLoad,
  };
  logger.info(metricsToReport);

  // log app loading metrics
  app.started.then(() => {
    logger.info({
      TimeToAppStartedMS: Math.round(measurePerformance(TIME_TO_APP_STARTED_MARK)),
    });
  });

  app.restored.then(() => {
    const timeToAppRestored = positiveValueOrNull(Math.round(measurePerformance(TIME_TO_APP_RESTORED_MARK)));
    logger.info({
      TimeToAppRestoredMS: timeToAppRestored || undefined,
    });
  });
};

/**
 * Mark and measure time from Navigation OriginTime.
 * Note: PerformanceEntry timings can be found in Chrome DevTools Performance tab
 */
const measurePerformance = (markName: string): DOMHighResTimeStamp => {
  const metricName = `${markName}.${SM_NAMESPACE}`;
  performance.mark(metricName);
  // Create PerformanceEntry viewable in Chrome DevTools
  performance.measure(metricName, undefined, metricName);
  return performance.getEntriesByName(metricName, 'measure')[0]?.duration ?? 0;
};

export { reportClientPerformance, measurePerformance };
