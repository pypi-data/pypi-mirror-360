import { JupyterFrontEnd } from '@jupyterlab/application';
import { HideShutDownPlugin } from './../HideShutDownPlugin';
import { JUPYTER_COMMAND_IDS } from '../../constants';

describe('HideShutDownPlugin suite', () => {
  const defaultHideShutdownCommandSettings = {
    isVisible: () => true,
  };

  const app = {
    commands: {
      addCommand: jest.fn(),
      _commands: {
        get: (key: string) => {
          if (key === JUPYTER_COMMAND_IDS.mainMenu.fileMenu.shutdown) {
            return defaultHideShutdownCommandSettings;
          }
        },
      },
    },
  } as unknown as JupyterFrontEnd;

  it('should test the plugin', async () => {
    await HideShutDownPlugin.activate(app);
    expect(defaultHideShutdownCommandSettings.isVisible()).toBe(false);
  });
});
