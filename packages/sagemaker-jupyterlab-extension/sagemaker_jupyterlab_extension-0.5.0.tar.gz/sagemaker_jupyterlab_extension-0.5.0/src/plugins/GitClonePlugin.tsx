import React from 'react';
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IFileBrowserFactory, IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { pluginIds, ErrorMessages } from '../constants';
import { GitCloneWidget } from '../widgets/GitCloneWidget';
import {
  Dialog,
  showErrorMessage,
  IToolbarWidgetRegistry,
  ReactWidget,
  UseSignal,
  ToolbarButtonComponent,
} from '@jupyterlab/apputils';
import { ITranslator, nullTranslator } from '@jupyterlab/translation';
import { IGitExtension } from '@jupyterlab/git';
import * as styles from '../widgets/styles/gitCloneStyles';
import { il18Strings } from '../constants/il18Strings';
import { getLoggerForPlugin } from '../utils/logger';
import {
  strHasLength,
  validCloneUrl,
  getRepoName,
  checkCloneDirectoryStatus,
  CloneDirectoryStatus,
  gitCloneInTerminal,
  AdditionalGitCloneOptions,
  handleAdditionalCloneOptions,
} from '../utils/gitCloneUtils';
import { IChangedArgs, PathExt } from '@jupyterlab/coreutils';
import { addFileBrowserContextMenu } from '@jupyterlab/git/lib/commandsAndMenu';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { CommandRegistry } from '@lumino/commands';
import { Contents } from '@jupyterlab/services';
import { CommandIDs as GitCommandIDs } from '@jupyterlab/git/lib/tokens';
import { cloneIcon } from '@jupyterlab/git/lib/style/icons';

const { dialogTitle, cancelButton, cloneButton, errors } = il18Strings.GitClone;

/**
 * Function to execute when addCommand is executed for gitClone
 * @param factory
 * @param contents
 * @param commands
 * @returns
 */
const executeGitCloneCommand = async (
  factory: IFileBrowserFactory,
  defaultFileBrowser: IDefaultFileBrowser,
  contents: Contents.IManager,
  commands: CommandRegistry,
  logger: ILogger,
) => {
  const fileBrowserModel = defaultFileBrowser.model;

  // Process args
  let URL = '';
  const cwd = factory?.tracker?.currentWidget?.model.path;
  let path: string = cwd ?? '';
  let openREADME = true;
  let findEnvironment = true;
  let result;
  const dialog = new Dialog({
    title: dialogTitle,
    body: new GitCloneWidget(),
    focusNodeSelector: 'input',
    buttons: [Dialog.cancelButton({ label: cancelButton }), Dialog.okButton({ label: cloneButton })],
    hasClose: false,
  });
  dialog.addClass(styles.increaseZIndex);

  try {
    result = await dialog.launch();
  } catch (error) {
    logger.error({
      Message: ErrorMessages.GitClone.Dialog,
      Error: error as Error,
    });
    return;
  }

  if (!(result.button.accept && result.value)) {
    return;
  }

  ({ URL, path, openREADME, findEnvironment } = result.value as any);

  // Prepare data
  if (!strHasLength(path)) {
    path = './';
  }
  // if URL is invalid display error message and do not continue
  if (!validCloneUrl(URL)) {
    await showErrorMessage(errors.invalidCloneUrlTitle, {
      message: errors.invalidCloneUrlBody,
    });
    return;
  }
  const repoName = getRepoName(URL);
  const repoPath = PathExt.join(path, repoName);
  let cloneDirectoryStatus;
  try {
    // removed studioLogger that is being passed
    cloneDirectoryStatus = await checkCloneDirectoryStatus(contents as any, path, URL, repoPath);
  } catch (error) {
    logger.error({
      Message: ErrorMessages.GitClone.ValidRepoPathError,
      Error: new Error(JSON.stringify(error)),
    });
  }
  // Git clone
  const additionalOptions = { repoPath, openREADME, findEnvironment };
  if (cloneDirectoryStatus === CloneDirectoryStatus.CanClone) {
    // Clone Repo Attempt
    // removed studio logger - need to add in logger
    gitCloneInTerminal(
      commands as any,
      contents as any,
      additionalOptions as AdditionalGitCloneOptions,
      fileBrowserModel,
      path as string,
      URL,
    );
  } else if (cloneDirectoryStatus === CloneDirectoryStatus.AlreadyCloned) {
    // If already cloned, only handle additional options (for example, find&build env or open README)
    handleAdditionalCloneOptions(commands as any, contents as any, additionalOptions as AdditionalGitCloneOptions);
  }
};

/**
 * Plugin to replace the defaukt git clone repo feature
 */
const GitClonePlugin: JupyterFrontEndPlugin<void> = {
  id: pluginIds.GitClonePlugin,
  requires: [IFileBrowserFactory, IDefaultFileBrowser, IGitExtension, IToolbarWidgetRegistry, ILogger, ITranslator],
  autoStart: true,
  activate: async (
    app: JupyterFrontEnd,
    factory: IFileBrowserFactory,
    defaultFileBrowser: IDefaultFileBrowser,
    gitExtension: IGitExtension,
    toolbarRegistry: IToolbarWidgetRegistry,
    baseLogger: ILogger,
    translator: ITranslator,
  ) => {
    const { commands, serviceManager } = app;
    const contents = serviceManager.contents;
    const logger = getLoggerForPlugin(baseLogger, pluginIds.GitClonePlugin);
    translator = translator || nullTranslator;

    // A translation bundle is required for 'addCloneButton' and 'addFileBrowserContextMenu' functions
    const trans = translator.load('sagemaker_studio');

    commands.addCommand(GitCommandIDs.gitClone, {
      label: 'Git Clone Repo',
      caption: '',
      execute: () => executeGitCloneCommand(factory, defaultFileBrowser, contents, commands, logger),
      isEnabled: () => app.serviceManager.terminals.isAvailable(),
    });

    // Add Git clone button to file browser
    toolbarRegistry.addFactory('FileBrowser', 'gitClone', () =>
      ReactWidget.create(
        <UseSignal
          signal={gitExtension.repositoryChanged}
          initialArgs={{
            name: 'pathRepository',
            oldValue: null,
            newValue: gitExtension.pathRepository,
          }}
        >
          {(_, change?: IChangedArgs<string | null>) => (
            <ToolbarButtonComponent
              enabled={change?.newValue === null}
              icon={cloneIcon}
              onClick={() => {
                app.commands.execute(GitCommandIDs.gitClone);
              }}
              tooltip={trans.__('Git Clone')}
            />
          )}
        </UseSignal>,
      ),
    );

    // Add the context menu items for the default file browser
    addFileBrowserContextMenu(gitExtension, defaultFileBrowser, app.serviceManager.contents, app.contextMenu, trans);

    // Added for testing purpose
    logger.info({ Message: 'Successfully loaded Git extension' });
  },
};

export { GitClonePlugin, executeGitCloneCommand };
