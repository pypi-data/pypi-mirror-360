import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { pluginIds } from '../../constants';
import { showErrorMessage } from '@jupyterlab/apputils';
import { IDocumentWidgetOpener } from '@jupyterlab/docmanager';
import { ILauncher } from '@jupyterlab/launcher';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';
import { getLoggerForPlugin } from '../../utils/logger';

import { libMgmtIcon } from './config';
import { LibManagementDocumentManager } from './LibraryDocument/LibManagementDocumentManager';
import { LibraryEditorFactory } from './LibraryDocument/LibraryEditorFactory';
import { installPackagesFromConfig } from './PackageInstaller';
import { checkMarkerFile, createMarkerFile } from './markerFile';
import { fetchApiResponse, OPTIONS_TYPE } from '../../service';
import { IS_MAXDOME_ENVIRONMENT_URL } from '../../service/constants';

// Command IDs used by the library management plugin
export enum CommandIDs {
  EDIT_LIBRARY_CONFIG = 'edit-library-config',
}

/**
 * Plugin for managing libraries in SageMaker Studio
 * Provides UI for configuring and installing conda packages/extensions
 */
const LibManagementPlugin: JupyterFrontEndPlugin<void> = {
  id: pluginIds.LibManagementPlugin,
  autoStart: true,
  requires: [ILogger],
  optional: [ILauncher, IDocumentWidgetOpener],
  activate: async (
    app: JupyterFrontEnd,
    baseLogger: ILogger,
    launcher: ILauncher,
    widgetOpener: IDocumentWidgetOpener,
  ) => {
    const logger = getLoggerForPlugin(baseLogger, pluginIds.LibManagementPlugin);
    try {
      const result = await fetchApiResponse(IS_MAXDOME_ENVIRONMENT_URL, OPTIONS_TYPE.GET);
      const data = await result.json();
      if (data.isMaxDomeEnvironment) {
        return; // This will actually prevent plugin activation
      }
    } catch (error) {
      logger.error({ Message: 'Unable to fetch environment' });
      // Do not activate even if we see an exception
      return;
    }
    const { commands, docRegistry } = app;
    // Helper function to create a new terminal session
    const createTerminal = async () => {
      return await app.serviceManager.terminals.startNew();
    };

    // Helper function to display terminal widget in the main area
    const openTerminal = (terminalWidget: TerminalWidget) => {
      app.shell.add(terminalWidget, 'main', { activate: true });
    };

    // Register the library editor factory with JupyterLab
    const factory = new LibraryEditorFactory(
      {
        name: 'library-config-editor',
        fileTypes: ['file'],
        defaultFor: [],
      },
      createTerminal,
      openTerminal,
      logger,
    );
    docRegistry.addWidgetFactory(factory);

    // Document manager for handling library configuration files
    const libManagementDocumentManager = new LibManagementDocumentManager({
      registry: docRegistry,
      manager: app.serviceManager,
      opener: widgetOpener,
    });

    // Automatically install packages from config when JupyterLab is restored
    app.restored.then(async () => {
      try {
        /**
         * API call to check if marker file exists
         * If does not exist then this is the first opening after space restart and installation of packages/extensions is needed
         * If it does exist, then this is not the first opening following restart. No installation should occur
         */
        const markerExists = await checkMarkerFile();
        if (!markerExists) {
          try {
            const contents = await app.serviceManager.contents.get('.libs.json', { content: true });
            if (contents.content) {
              const configData = JSON.parse(contents.content);

              try {
                // Attempt installation
                await installPackagesFromConfig(configData, createTerminal, openTerminal, logger);
              } catch (error) {
                // Installation failure
              }

              // Create marker file once installation process completes
              await createMarkerFile();
            }
          } catch (installErr) {
            // .libs.json doesn't exist, consider 'persistence' complete, and create marker file
            await createMarkerFile();
          }
        }
      } catch (apiErr) {
        // Do nothing
      }
    });

    // Register the command to open the library configuration editor
    const command = CommandIDs.EDIT_LIBRARY_CONFIG;
    commands.addCommand(command, {
      label: 'Environment management',
      icon: (args) => (args['isPalette'] ? undefined : libMgmtIcon),
      execute: async () => {
        try {
          // Open or create the library configuration file
          await libManagementDocumentManager.openOrCreate('.libs.json', 'library-config-editor');
        } catch (err) {
          showErrorMessage('Failed to open Environment Management config', (err as Error).message);
        }
      },
    });

    // Add the command to the launcher if available
    if (launcher) {
      launcher.add({
        command,
        category: 'Other',
        rank: 1,
      });
      logger.info({ Message: 'Successfully loaded Extension Management plugin' });
    }
  },
};

export { LibManagementPlugin };
