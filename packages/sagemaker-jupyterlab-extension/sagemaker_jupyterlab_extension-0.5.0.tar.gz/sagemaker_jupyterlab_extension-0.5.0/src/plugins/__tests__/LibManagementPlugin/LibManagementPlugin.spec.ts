import { fetchApiResponse } from '../../../service';
import * as loggerModule from '../../../utils/logger';

// Only mock the dependencies
jest.mock('../../../service');
jest.mock('../../../utils/logger');

// Import the actual module (not mocked)
import { CommandIDs, LibManagementPlugin } from '../../LibManagementPlugin';
import { pluginIds } from '../../../constants';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';

describe('LibManagementPlugin', () => {
  describe('CommandIDs', () => {
    it('should define correct command IDs', () => {
      expect(CommandIDs.EDIT_LIBRARY_CONFIG).toBe('edit-library-config');
    });

    it('should have correct plugin ID in constants', () => {
      expect(pluginIds.LibManagementPlugin).toBe('@amzn/sagemaker-jupyterlab-extensions:libmanagement');
    });
  });

  describe('Plugin activation', () => {
    let mockApp;
    let mockLauncher;
    let mockWidgetOpener;
    let mockBaseLogger: ILogger;
    let mockPluginLogger: ILogger;

    beforeEach(() => {
      jest.clearAllMocks();

      // Setup base logger mock
      mockBaseLogger = {
        error: jest.fn().mockResolvedValue(undefined),
        info: jest.fn().mockResolvedValue(undefined),
        child: jest.fn(),
        fatal: jest.fn().mockResolvedValue(undefined),
        warn: jest.fn().mockResolvedValue(undefined),
        debug: jest.fn().mockResolvedValue(undefined),
        trace: jest.fn().mockResolvedValue(undefined),
      };

      // Setup plugin logger mock
      mockPluginLogger = {
        error: jest.fn().mockResolvedValue(undefined),
        info: jest.fn().mockResolvedValue(undefined),
        child: jest.fn(),
        fatal: jest.fn().mockResolvedValue(undefined),
        warn: jest.fn().mockResolvedValue(undefined),
        debug: jest.fn().mockResolvedValue(undefined),
        trace: jest.fn().mockResolvedValue(undefined),
      };

      // Mock getLoggerForPlugin
      jest.spyOn(loggerModule, 'getLoggerForPlugin').mockReturnValue(mockPluginLogger);

      // Create mock app
      mockApp = {
        commands: {
          addCommand: jest.fn(),
        },
        docRegistry: {
          addFileType: jest.fn(),
          addWidgetFactory: jest.fn(),
        },
        serviceManager: {
          terminals: {
            startNew: jest.fn(),
          },
          contents: {
            get: jest.fn(),
          },
        },
        shell: {
          add: jest.fn(),
        },
        restored: Promise.resolve(),
      };

      // Create mock launcher
      mockLauncher = {
        add: jest.fn(),
      };

      // Create mock widget opener
      mockWidgetOpener = {};

      // Default success response for fetchApiResponse
      (fetchApiResponse as jest.Mock).mockResolvedValue({
        json: () => Promise.resolve({ isMaxDomeEnvironment: false }),
      });
    });

    it('should handle API error gracefully', async () => {
      // Mock API call to fail
      (fetchApiResponse as jest.Mock).mockRejectedValue(new Error('API Error'));

      await LibManagementPlugin.activate(mockApp, mockBaseLogger, mockLauncher, mockWidgetOpener);

      expect(mockPluginLogger.error).toHaveBeenCalledWith({
        Message: 'Unable to fetch environment',
      });
      expect(mockApp.commands.addCommand).not.toHaveBeenCalled();
    });

    it('should activate plugin successfully', async () => {
      await LibManagementPlugin.activate(mockApp, mockBaseLogger, mockLauncher, mockWidgetOpener);

      expect(mockApp.docRegistry.addWidgetFactory).toHaveBeenCalled();
      expect(mockApp.commands.addCommand).toHaveBeenCalled();
      expect(mockLauncher.add).toHaveBeenCalled();
    });
  });
});
