import { Terminal } from '@jupyterlab/services';
import { createCommandPromise } from '../../LibManagementPlugin/CommandMonitor';

describe('CommandMonitor', () => {
  let mockTerminal: any;
  let mockSend: jest.Mock;
  let mockConnect: jest.Mock;
  let mockDisconnect: jest.Mock;
  let mockShutdown: jest.Mock;

  beforeEach(() => {
    jest.useFakeTimers();
    mockConnect = jest.fn();
    mockDisconnect = jest.fn();
    mockSend = jest.fn();
    mockShutdown = jest.fn().mockResolvedValue(undefined);

    mockTerminal = {
      messageReceived: {
        connect: mockConnect,
        disconnect: mockDisconnect,
      },
      send: mockSend,
      shutdown: mockShutdown,
    };
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should send commands to terminal', () => {
    const commands = ['npm install', 'pip install'];
    createCommandPromise(mockTerminal as unknown as Terminal.ITerminalConnection, commands);

    expect(mockConnect).toHaveBeenCalled();
    expect(mockSend).toHaveBeenCalledWith({
      type: 'stdin',
      content: ['npm install;echo "EXIT_CODE: $?";pip install;echo "EXIT_CODE: $?"\n;'],
    });
  });

  it('should resolve when all commands succeed', async () => {
    const commands = ['npm install'];
    const promise = createCommandPromise(mockTerminal as unknown as Terminal.ITerminalConnection, commands);
    const monitorFn = mockConnect.mock.calls[0][0];

    // Simulate successful command execution
    monitorFn(mockTerminal, {
      type: 'stdout',
      content: ['echo "EXIT_CODE: $?"'],
    });
    monitorFn(mockTerminal, {
      type: 'stdout',
      content: ['EXIT_CODE: 0'],
    });

    jest.advanceTimersByTime(1000);

    const result = await promise;
    expect(result.alreadyInstalled).toBe(false);
    expect(typeof result.output).toBe('string');
    expect(mockDisconnect).toHaveBeenCalled();
    expect(mockShutdown).toHaveBeenCalled();
  });

  it('should detect already installed packages', async () => {
    const commands = ['npm install'];
    const promise = createCommandPromise(mockTerminal as unknown as Terminal.ITerminalConnection, commands);
    const monitorFn = mockConnect.mock.calls[0][0];

    // Simulate already installed message and successful execution
    monitorFn(mockTerminal, {
      type: 'stdout',
      content: ['All requested packages already installed'],
    });
    monitorFn(mockTerminal, {
      type: 'stdout',
      content: ['EXIT_CODE: 0'],
    });

    jest.advanceTimersByTime(1000);

    const result = await promise;
    expect(result.alreadyInstalled).toBe(true);
    expect(typeof result.output).toBe('string');
  });

  it('should reject when a command fails', async () => {
    const commands = ['npm install'];
    const promise = createCommandPromise(mockTerminal as unknown as Terminal.ITerminalConnection, commands);
    const monitorFn = mockConnect.mock.calls[0][0];

    // Simulate failed command execution
    monitorFn(mockTerminal, {
      type: 'stdout',
      content: ['EXIT_CODE: 1'],
    });

    jest.advanceTimersByTime(1000);

    await expect(promise).rejects.toThrow();
    expect(mockDisconnect).toHaveBeenCalled();
  });
});
