import { JupyterFrontEnd } from '@jupyterlab/application';
import { ResourceUsagePlugin } from './../ResourceUsagePlugin';
import { IStatusBar } from '@jupyterlab/statusbar';

jest.mock('@jupyterlab/statusbar', () => jest.fn as jest.Mock);
// jest.mock('@material-ui/core', () => jest.fn as jest.Mock);

describe('ResourceUsagePlugin suite', () => {
  it('should test the activate', async () => {
    const mockRegisterStatusItem = jest.fn();
    const app: JupyterFrontEnd = {};
    const statusBar: IStatusBar = {
      registerStatusItem: mockRegisterStatusItem,
      dispose: jest.fn(),
    } as IStatusBar;
    await ResourceUsagePlugin.activate(app, statusBar);

    expect(mockRegisterStatusItem).toHaveBeenCalledTimes(1);
  });
});
