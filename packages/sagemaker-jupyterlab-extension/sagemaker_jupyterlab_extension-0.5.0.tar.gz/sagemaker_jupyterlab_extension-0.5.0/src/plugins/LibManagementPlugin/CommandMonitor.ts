import { Terminal } from '@jupyterlab/services';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';

/**
 * Status of command execution
 */
enum CommandStatus {
  RUNNING,
  SUCCESS,
  FAILURE,
}

const PRINT_EXIT_CODE_COMMAND = 'echo "EXIT_CODE: $?"';
const PRINT_EXIT_CODE = 'EXIT_CODE:';
const PRINT_EXIT_CODE_ZERO = 'EXIT_CODE: 0';
const PACKAGES_ALREADY_INSTALLED = 'All requested packages already installed';

/**
 * Creates a promise that resolves when commands complete successfully
 * Monitors terminal output to detect command completion and status
 */
export function createCommandPromise(
  terminal: Terminal.ITerminalConnection,
  commands: string[],
  logger?: ILogger,
): Promise<{ alreadyInstalled: boolean; output: string }> {
  let status = CommandStatus.RUNNING;
  let executingCommands = commands.length;
  let alreadyInstalled = false;
  let intervalId: number;
  let accumulatedOutput = '';

  // Monitors terminal output for command completion and exit codes
  function terminalMonitor(terminal: Terminal.ITerminalConnection, message: Terminal.IMessage) {
    if (message.type === 'stdout' && message.content) {
      message.content.forEach((content) => {
        if (status === CommandStatus.RUNNING && typeof content === 'string') {
          // Save stdout for logs
          const cleanContent = content
            // eslint-disable-next-line no-control-regex
            .replace(/\x1B\[[?0-9;]*[a-zA-Z]/g, '')
            .replace(/\r/g, '')
            .trim();
          if (cleanContent) {
            accumulatedOutput += cleanContent + '\n';
          }

          // Check for result of command
          if (content.includes(PACKAGES_ALREADY_INSTALLED)) {
            alreadyInstalled = true;
          }
          if (!content.includes(PRINT_EXIT_CODE_COMMAND) && content.includes(PRINT_EXIT_CODE)) {
            if (content.includes(PRINT_EXIT_CODE_ZERO)) {
              executingCommands--;
              if (!executingCommands) {
                status = CommandStatus.SUCCESS;
                logger?.info({ Message: 'Successfully installed packages and extensions' });
              }
            } else {
              // If any command returns non 0 exit code, stop monitoring and set the status to FAILED
              status = CommandStatus.FAILURE;
              terminal.messageReceived.disconnect(terminalMonitor);
              logger?.error({ Message: 'Failed to install packages and extensions' });
            }
          }
        } else {
          // memory leak prevention
          status = CommandStatus.FAILURE;
          terminal.messageReceived.disconnect(terminalMonitor);
        }
      });
    }
  }
  terminal.messageReceived.connect(terminalMonitor);

  // Join commands with exit code checks
  let command = commands.join(`;${PRINT_EXIT_CODE_COMMAND};`);

  command += `;${PRINT_EXIT_CODE_COMMAND}\n;`;
  terminal.send({ type: 'stdin', content: [command] });

  // Return promise that resolves when commands complete
  return new Promise<{ alreadyInstalled: boolean; output: string }>((resolve, reject) => {
    intervalId = window.setInterval(() => {
      if (status === CommandStatus.SUCCESS) {
        clearInterval(intervalId);
        terminal.messageReceived.disconnect(terminalMonitor);
        try {
          terminal.shutdown().catch(() => {
            /* ignore shutdown errors */
          });
        } catch {
          // ignore any shutdown errors
        }
        resolve({ alreadyInstalled, output: accumulatedOutput });
      } else if (status === CommandStatus.FAILURE) {
        clearInterval(intervalId);
        terminal.messageReceived.disconnect(terminalMonitor);
        try {
          terminal.shutdown().catch(() => {
            /* ignore shutdown errors */
          });
        } catch {
          // ignore any shutdown errors
        }
        reject(new Error(accumulatedOutput));
      }
    }, 1000);
  });
}
