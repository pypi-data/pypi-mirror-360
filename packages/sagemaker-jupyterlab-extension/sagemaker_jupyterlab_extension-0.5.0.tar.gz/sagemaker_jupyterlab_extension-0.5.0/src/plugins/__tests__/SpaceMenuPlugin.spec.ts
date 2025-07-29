import { JupyterFrontEnd } from '@jupyterlab/application';
import { SpaceMenuPlugin } from '../SpaceMenuPlugin';
import { SpaceMenuWidget } from '../../widgets/SpaceMenuWidget';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { LogArguments } from '@amzn/sagemaker-jupyterlab-extension-common/lib/types';

const mockLogger: ILogger = {
  error: jest.fn(),
  info: jest.fn(),
  child: jest.fn(() => mockLogger),
  fatal: function (logArguments: LogArguments): Promise<void> {
    throw new Error('Function not implemented.');
  },
  warn: function (logArguments: LogArguments): Promise<void> {
    throw new Error('Function not implemented.');
  },
  debug: function (logArguments: LogArguments): Promise<void> {
    throw new Error('Function not implemented.');
  },
  trace: function (logArguments: LogArguments): Promise<void> {
    throw new Error('Function not implemented.');
  },
};

const mockApp: JupyterFrontEnd = {
  shell: {
    add: jest.fn(),
  },
};

describe('SpaceMenuPlugin suite', () => {
  it('should test the activate', async () => {
    // Call the activate function of the plugin
    await SpaceMenuPlugin.activate(mockApp, mockLogger);

    // Assert that the SpaceMenuWidget is added to the shell
    expect(mockApp.shell.add).toHaveBeenCalledWith(expect.any(SpaceMenuWidget), 'top', { rank: 1000 });
  });
});
