import { Terminal } from '@jupyterlab/services';
import { installPackagesFromConfig } from '../../LibManagementPlugin/PackageInstaller';
import { Notification } from '@jupyterlab/apputils';
import { createCommandPromise } from '../../LibManagementPlugin/CommandMonitor';

// Mock dependencies
jest.mock('@jupyterlab/apputils', () => ({
  Notification: {
    promise: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
    dismiss: jest.fn(),
  },
}));

jest.mock('@jupyterlab/terminal', () => {
  return {
    Terminal: jest.fn().mockImplementation((terminal) => ({
      id: '',
      title: { closable: false },
      terminal,
    })),
  };
});

jest.mock('../../LibManagementPlugin/CommandMonitor', () => ({
  createCommandPromise: jest.fn().mockReturnValue(Promise.resolve({ alreadyInstalled: false })),
}));

describe('PackageInstaller', () => {
  // Mock functions
  const mockCreateTerminal = jest.fn();
  const mockOpenTerminal = jest.fn();
  const mockTerminalConnection = {
    isDisposed: false,
    send: jest.fn(),
  } as unknown as Terminal.ITerminalConnection;

  beforeEach(() => {
    jest.clearAllMocks();
    mockCreateTerminal.mockResolvedValue(mockTerminalConnection);
  });

  it('should not install packages when config is invalid', async () => {
    // Test with missing Python config
    await installPackagesFromConfig({}, mockCreateTerminal, mockOpenTerminal);
    expect(mockCreateTerminal).not.toHaveBeenCalled();

    // Test with missing CondaPackages
    await installPackagesFromConfig({ Python: {} }, mockCreateTerminal, mockOpenTerminal);
    expect(mockCreateTerminal).not.toHaveBeenCalled();

    // Test with empty PackageSpecs
    await installPackagesFromConfig(
      {
        Python: {
          CondaPackages: {
            PackageSpecs: [],
            Channels: ['conda-forge'],
          },
        },
      },
      mockCreateTerminal,
      mockOpenTerminal,
    );
    expect(mockCreateTerminal).not.toHaveBeenCalled();
  });

  it('should install packages when valid config is provided', async () => {
    const configData = {
      Python: {
        CondaPackages: {
          PackageSpecs: ['numpy', 'pandas'],
          Channels: ['conda-forge'],
        },
      },
    };

    await installPackagesFromConfig(configData, mockCreateTerminal, mockOpenTerminal);

    expect(mockCreateTerminal).toHaveBeenCalledTimes(1);
    expect(Notification.promise).toHaveBeenCalledTimes(1);

    // Test the "View in terminal" action
    const viewAction = (Notification.promise as jest.Mock).mock.calls[0][1].pending.options.actions[0];
    viewAction.callback();
    expect(mockOpenTerminal).toHaveBeenCalled();
  });

  it('should handle terminal disposal', async () => {
    const configData = {
      Python: {
        CondaPackages: {
          PackageSpecs: ['numpy'],
          Channels: ['conda-forge'],
        },
      },
    };

    // Create a disposed terminal
    const disposedTerminal = { isDisposed: true } as unknown as Terminal.ITerminalConnection;
    mockCreateTerminal.mockResolvedValue(disposedTerminal);

    await installPackagesFromConfig(configData, mockCreateTerminal, mockOpenTerminal);

    // Get the view action callback and execute it
    const viewAction = (Notification.promise as jest.Mock).mock.calls[0][1].pending.options.actions[0];
    viewAction.callback();

    expect(Notification.error).toHaveBeenCalledWith('Terminal is disposed');
    expect(mockOpenTerminal).not.toHaveBeenCalled();
  });

  it('should handle notification success states', async () => {
    const configData = {
      Python: {
        CondaPackages: {
          PackageSpecs: ['numpy'],
          Channels: ['conda-forge'],
        },
      },
    };

    await installPackagesFromConfig(configData, mockCreateTerminal, mockOpenTerminal);
    const successHandler = (Notification.promise as jest.Mock).mock.calls[0][1].success.message;

    // Test with alreadyInstalled = true
    expect(successHandler({ alreadyInstalled: true })).toBe('All packages and extensions already installed');

    // Test with alreadyInstalled = false
    expect(successHandler({ alreadyInstalled: false })).toBe(
      'Installation completed. Restart the kernel for updated libraries. Restart the server for updated extensions.',
    );
  });

  it('should format command correctly', async () => {
    const configData = {
      Python: {
        CondaPackages: {
          PackageSpecs: ['numpy', 'pandas'],
          Channels: ['conda-forge', 'defaults'],
        },
      },
    };

    // Capture the command
    let capturedCommand = '';
    (createCommandPromise as jest.Mock).mockImplementation((terminal, commands) => {
      capturedCommand = commands[0];
      return Promise.resolve({ alreadyInstalled: false });
    });

    await installPackagesFromConfig(configData, mockCreateTerminal, mockOpenTerminal);

    // Verify command format
    expect(capturedCommand).toContain('micromamba install --freeze-installed -y');
    expect(capturedCommand).toContain('-c "conda-forge"');
    expect(capturedCommand).toContain('-c "defaults"');
    expect(capturedCommand).toContain('"numpy"');
    expect(capturedCommand).toContain('"pandas"');
  });
});
