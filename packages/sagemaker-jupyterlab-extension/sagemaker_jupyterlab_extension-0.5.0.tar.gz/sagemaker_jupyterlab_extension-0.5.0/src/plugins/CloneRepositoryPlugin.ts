import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { IRouter, JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { pluginIds } from '../constants';
import { getLoggerForPlugin } from '../utils/logger';
import { executeCloneRepository } from '../utils/projectCloneUtils';

/**
 * Plugin to clone a projects git repository
 */
const CloneRepositoryPlugin: JupyterFrontEndPlugin<void> = {
  id: pluginIds.ProjectsCloneRepositoryPlugin,
  requires: [IRouter, ILogger, IDefaultFileBrowser],
  autoStart: true,
  activate: async (
    app: JupyterFrontEnd,
    router: IRouter,
    baseLogger: ILogger,
    defaultFileBrowser: IDefaultFileBrowser,
  ) => {
    const { commands, serviceManager } = app;
    const contents = serviceManager.contents;
    const commandName = 'projects:clone-repository';
    const logger = getLoggerForPlugin(baseLogger, pluginIds.ProjectsCloneRepositoryPlugin);

    commands.addCommand(commandName, {
      execute: () => executeCloneRepository(router, app, logger, contents, defaultFileBrowser),
    });

    router.register({
      command: commandName,
      pattern: new RegExp('[?]command=clone-repository'),
      rank: 10, // arbitrary ranking to lift this pattern
    });
  },
};

export { CloneRepositoryPlugin };
