import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { DOMUtils } from '@jupyterlab/apputils';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { pluginIds } from '../constants';
import { SpaceMenuWidget } from '../widgets/SpaceMenuWidget';
import { getLoggerForPlugin } from '../utils/logger';

const SpaceMenuPlugin: JupyterFrontEndPlugin<void> = {
  id: pluginIds.SpaceMenuPlugin,
  requires: [ILogger],
  autoStart: true,
  activate: async (app: JupyterFrontEnd, baseLogger: ILogger) => {
    const spaceMenuWidget = new SpaceMenuWidget();
    spaceMenuWidget.id = DOMUtils.createDomID();
    const logger = getLoggerForPlugin(baseLogger, pluginIds.SpaceMenuPlugin);

    // Add the widget to the top area
    app.shell.add(spaceMenuWidget, 'top', { rank: 1000 });
    if (window && window.panorama) {
      window.panorama('trackCustomEvent', {
        eventType: 'render',
        eventDetail: 'Space-Plugin',
        eventContext: 'JupyterLab',
        timestamp: Date.now(),
      });
    }
    logger.info({ Message: 'Successfully loaded Space plugin' });
  },
};

export { SpaceMenuPlugin };
