import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { RESOURCE_PLUGIN_ID, pluginIds } from '../constants';
import { IStatusBar } from '@jupyterlab/statusbar';
import { ResourceUsageWidget } from '../widgets/ResourceUsageWidget';

const ResourceUsagePlugin: JupyterFrontEndPlugin<void> = {
  id: pluginIds.ResourceUsagePlugin,
  // @TODO: update the type
  requires: [IStatusBar as any],
  autoStart: true,
  activate: async (app: JupyterFrontEnd, statusBar: IStatusBar) => {
    const resourceUsageWidget = new ResourceUsageWidget();

    statusBar.registerStatusItem(RESOURCE_PLUGIN_ID, {
      // @TODO: update the type
      item: resourceUsageWidget as any,
      align: 'left',
      isActive: () => true,
      rank: 100,
    });
  },
};

export { ResourceUsagePlugin };
