import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { pluginIds, JUPYTER_COMMAND_IDS } from '../constants';

const HideShutDownPlugin: JupyterFrontEndPlugin<void> = {
  id: pluginIds.HideShutDownPlugin,
  // Despite we are not directly re-using IMainMenu, this ensures MainMenu
  // plugin is activated before this plugin and shut down command has been
  // added by main menu plugin. Do not remove.
  requires: [IMainMenu],
  autoStart: true,
  activate: (app: JupyterFrontEnd, _: IMainMenu) => {
    // @TODO: Add in logging
    (app.commands as any)._commands.get(JUPYTER_COMMAND_IDS.mainMenu.fileMenu.shutdown).isVisible = () => false;
  },
};

export { HideShutDownPlugin };
