import { Notification } from '@jupyterlab/apputils';
import { Terminal } from '@jupyterlab/services';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { recordMetric } from './metrics';

import { createCommandPromise } from './CommandMonitor';

/**
 * Installs packages from configuration data
 *
 * @param configData - The configuration data containing package information
 * @param createTerminal - Function to create a terminal
 * @param openTerminal - Function to open a terminal widget
 * @param logger - Optional logger for recording events
 * @returns Promise that resolves when installation is complete
 */
export async function installPackagesFromConfig(
  configData: ReadonlyJSONObject,
  createTerminal: () => Promise<Terminal.ITerminalConnection>,
  openTerminal: (terminalWidget: TerminalWidget) => void,
  logger?: ILogger,
): Promise<any> {
  const startTime = Date.now();

  if (!configData.Python) {
    return;
  }

  const pythonConfig = configData.Python as ReadonlyJSONObject;
  if (!pythonConfig.CondaPackages) {
    return;
  }
  const condaConfig = pythonConfig.CondaPackages as ReadonlyJSONObject;
  const packages = condaConfig.PackageSpecs as string[];
  const channels = condaConfig.Channels as string[];

  if (packages.length > 0) {
    logger?.info({ Message: 'Installing packages and extensions from config' });
    const terminal = await createTerminal();
    const terminalWidget = new TerminalWidget(terminal);
    terminalWidget.id = 'installLab' + new Date().getMilliseconds();
    terminalWidget.title.closable = true;

    // Build conda install command with channels and packages
    const command = `micromamba install --freeze-installed -y ${channels
      .map((channel) => `-c "${channel}"`)
      .join(' ')} ${packages.map((p) => `"${p}"`).join(' ')}`;

    let warningNotificationId: string | undefined;
    let terminalOpened = false;
    const installPromise = createCommandPromise(terminal, [command], logger);

    Notification.promise(installPromise, {
      pending: {
        message: 'Installing packages and extensions from saved configuration...',
        options: {
          actions: [
            {
              label: 'View in terminal',
              callback: () => {
                if (terminal.isDisposed) {
                  Notification.error('Terminal is disposed');
                } else {
                  terminalOpened = true;
                  openTerminal(terminalWidget);
                  warningNotificationId = Notification.warning(
                    'Closing the terminal will terminate the installation process. This terminal will automatically close once installation complete.',
                    {
                      autoClose: false,
                      actions: [],
                    },
                  );
                }
              },
            },
          ],
          autoClose: false,
        },
      },
      success: {
        message: (result) => {
          const { alreadyInstalled, output } = result as { alreadyInstalled: boolean; output: string };
          const latency = Date.now() - startTime;

          recordMetric('Package Installation', {
            latency,
            success: 1,
            error: 0,
            output: output,
          });

          if (alreadyInstalled) {
            return 'All packages and extensions already installed';
          }
          return 'Installation completed. Restart the kernel for updated libraries. Restart the server for updated extensions.';
        },
        options: {
          actions: [
            {
              label: 'Restart Server',
              callback: () => {
                createTerminal().then((term) => {
                  const restartTerminalWidget = new TerminalWidget(term);
                  restartTerminalWidget.id = 'restartServer' + new Date().getMilliseconds();
                  restartTerminalWidget.title.closable = true;
                  openTerminal(restartTerminalWidget);
                  term.send({ type: 'stdin', content: ['restart-jupyter-server\n'] });
                });
              },
            },
          ],
          autoClose: false,
        },
      },
      error: {
        message: (error) => {
          const latency = Date.now() - startTime;
          recordMetric('Package Installation', {
            latency,
            success: 0,
            error: 1,
            output: (error as Error).message,
          });
          return 'Failed to install packages/extensions. Check error logs in terminal.';
        },
        options: {
          actions: [
            {
              label: 'View in terminal',
              callback: () => {
                if (terminal.isDisposed) {
                  Notification.error('Terminal is disposed');
                } else {
                  openTerminal(terminalWidget);
                }
              },
            },
          ],
          autoClose: false,
        },
      },
    });

    // Handle cleanup and ensure notifications appear even when terminal is opened
    installPromise
      .then((result) => {
        if (terminalOpened) {
          const { alreadyInstalled } = result;
          const message = alreadyInstalled
            ? 'All packages and extensions already installed'
            : 'Installation completed. Restart the kernel for updated libraries. Restart the server for updated extensions.';
          Notification.success(message, {
            actions: alreadyInstalled
              ? []
              : [
                  {
                    label: 'Restart Server',
                    callback: () => {
                      createTerminal().then((term) => {
                        const restartTerminalWidget = new TerminalWidget(term);
                        restartTerminalWidget.id = 'restartServer' + new Date().getMilliseconds();
                        restartTerminalWidget.title.closable = true;
                        openTerminal(restartTerminalWidget);
                        term.send({ type: 'stdin', content: ['restart-jupyter-server\n'] });
                      });
                    },
                  },
                ],
            autoClose: false,
          });
        }
      })
      .catch((error) => {
        if (terminalOpened) {
          Notification.error('Failed to install packages/extensions. Check error logs in terminal.', {
            autoClose: false,
            actions: [],
          });
        }
      })
      .finally(() => {
        if (warningNotificationId) {
          Notification.dismiss(warningNotificationId);
        }
      });

    // Return the installation promise so caller can wait for completion
    return installPromise;
  }
}
