import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { pluginIds } from '../../constants';
import { ILogger, logSchemas } from '@amzn/sagemaker-jupyterlab-extension-common';
import { getLoggerForPlugin } from '../../utils/logger';
import { reportClientPerformance } from './utils';

const PerformanceMeteringPlugin: JupyterFrontEndPlugin<void> = {
  id: pluginIds.PerformanceMeteringPlugin,
  requires: [ILogger],
  autoStart: true,
  activate: (app: JupyterFrontEnd, logger: ILogger) => {
    const performanceMetricsLogger = getLoggerForPlugin(
      logger,
      pluginIds.PerformanceMeteringPlugin,
      logSchemas.performance,
    );

    reportClientPerformance(performanceMetricsLogger, app);
  },
};

export { PerformanceMeteringPlugin };
