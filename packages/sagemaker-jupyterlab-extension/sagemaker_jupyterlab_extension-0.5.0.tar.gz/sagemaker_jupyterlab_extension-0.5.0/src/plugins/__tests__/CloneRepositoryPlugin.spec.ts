import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { IRouter, JupyterFrontEnd } from '@jupyterlab/application';
import { FilterFileBrowserModel, IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { Contents } from '@jupyterlab/services';
import { CommandRegistry } from '@lumino/commands';
import { pluginIds } from '../../constants';
import * as projectCloneUtils from '../../utils/projectCloneUtils';
import { CloneRepositoryPlugin } from '../CloneRepositoryPlugin';

jest.mock('../../utils/projectCloneUtils');

describe('CloneRepositoryPlugin', () => {
  let mockRouter: Partial<IRouter>;
  let mockApp: Partial<JupyterFrontEnd>;
  let mockLogger: Partial<ILogger>;
  let mockFileBrowser: Partial<IDefaultFileBrowser>;
  let mockCommands: Partial<CommandRegistry>;
  let mockServiceManager: any;
  let mockContents: Partial<Contents.IManager>;

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Setup mock router
    mockRouter = {
      register: jest.fn(),
    };

    // Setup mock commands
    mockCommands = {
      addCommand: jest.fn(),
    };

    // Setup mock contents manager
    mockContents = {};

    // Setup mock service manager
    mockServiceManager = {
      contents: mockContents,
    };

    // Setup mock app
    mockApp = {
      commands: mockCommands as CommandRegistry,
      serviceManager: mockServiceManager,
    };

    // Setup mock logger
    mockLogger = {
      error: jest.fn(),
      info: jest.fn(),
      child: jest.fn(() => mockLogger),
    };

    // Setup mock file browser
    const mockModel: Partial<FilterFileBrowserModel> = {
      refresh: jest.fn(),
    };
    mockFileBrowser = {
      model: mockModel as FilterFileBrowserModel,
    };
  });

  it('should activate and register command correctly', async () => {
    // Call the activate function
    await CloneRepositoryPlugin.activate(
      mockApp as JupyterFrontEnd,
      mockRouter as IRouter,
      mockLogger as ILogger,
      mockFileBrowser as IDefaultFileBrowser,
    );

    // Verify command was added
    expect(mockCommands.addCommand).toHaveBeenCalledWith('projects:clone-repository', expect.any(Object));

    // Verify router registration
    expect(mockRouter.register).toHaveBeenCalledWith({
      command: 'projects:clone-repository',
      pattern: new RegExp('[?]command=clone-repository'),
      rank: 10,
    });
  });

  it('should execute clone repository command correctly', async () => {
    // Setup spy on executeCloneRepository
    const executeCloneRepositorySpy = jest.spyOn(projectCloneUtils, 'executeCloneRepository');

    // Call the activate function
    await CloneRepositoryPlugin.activate(
      mockApp as JupyterFrontEnd,
      mockRouter as IRouter,
      mockLogger as ILogger,
      mockFileBrowser as IDefaultFileBrowser,
    );

    // Get the command execution function
    const commandExecuteFn = (mockCommands.addCommand as jest.Mock).mock.calls[0][1].execute;

    // Execute the command
    await commandExecuteFn();

    // Verify executeCloneRepository was called with correct parameters
    expect(executeCloneRepositorySpy).toHaveBeenCalledWith(
      mockRouter,
      mockApp,
      expect.any(Object), // logger
      mockContents,
      mockFileBrowser,
    );
  });

  it('should have correct plugin configuration', () => {
    expect(CloneRepositoryPlugin.id).toBe(pluginIds.ProjectsCloneRepositoryPlugin);
    expect(CloneRepositoryPlugin.autoStart).toBe(true);
    expect(CloneRepositoryPlugin.requires).toEqual([IRouter, ILogger, IDefaultFileBrowser]);
  });
});
