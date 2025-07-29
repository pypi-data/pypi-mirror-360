import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { IRouter, JupyterFrontEnd } from '@jupyterlab/application';
import { MainAreaWidget, showErrorMessage } from '@jupyterlab/apputils';
import { PathExt, URLExt } from '@jupyterlab/coreutils';
import { IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { Contents, ContentsManager } from '@jupyterlab/services';

import { ITerminal } from '@jupyterlab/terminal';
import shellEscape from 'shell-escape';
import { il18Strings } from '../constants/il18Strings';
import { fetchApiResponse, OPTIONS_TYPE } from '../service';
import { PROJECTS_LIST_URL } from '../service/constants';

const il18stringsError = il18Strings.ProjectsCloneRepo.errorDialog;

const DEFAULT_FILES = [
  {
    name: 'README.ipynb',
    factory: 'Notebook',
  },
  {
    name: 'README.md',
    factory: 'Markdown Preview',
  },
];

/**
 * Function to clone projects repository
 * @param router
 * @param app
 * @returns
 */
const executeCloneRepository = async (
  router: IRouter,
  app: JupyterFrontEnd,
  logger: ILogger,
  contents: Contents.IManager,
  defaultFileBrowser: IDefaultFileBrowser,
) => {
  const { search } = router.current;
  if (!search) {
    await showErrorMessageAsync(il18stringsError.invalidRequestErrorMessage);
    logger.error({ Error: new Error('Invalid cloning parameters: Query params must be specified') });
    return;
  }
  const fileBrowserModel = defaultFileBrowser.model;
  const {
    is_efs: isEfs,
    project_name: projectName = '',
    repo_name: repoName = '',
    clone_url: cloneUrl = '',
    code_commit: codeCommit,
  } = URLExt.queryStringToObject(search);

  const projectsList = await getProjectsList();

  if (!validCloneUrl(cloneUrl)) {
    await showErrorMessageAsync(il18stringsError.invalidCloneUrlBody);
    logger.error({ Message: 'Invalid cloning parameters: Clone URL is not valid' });
    return;
  }

  if (!projectsList.includes(projectName)) {
    await showErrorMessageAsync(il18stringsError.invalidProjectName);
    logger.error({ Message: 'Invalid project name: Project does not exist' });
    return;
  }

  const homePath = '$HOME';
  const efsPath = PathExt.join(homePath, 'user-default-efs');
  const fullPath = PathExt.join(isEfs === 'true' ? efsPath : homePath, projectName);
  const escapedPath = shellEscape([fullPath.replace('$HOME', '.')]);

  let content = `if ! [[ -d ${escapedPath} ]]; then mkdir ${escapedPath}; fi && cd ${escapedPath} && `;

  if (codeCommit) {
    content +=
      "git config --global credential.https://git-codecommit.*.amazonaws.com.helper '!aws codecommit credential-helper $@' && git config --global credential.https://git-codecommit.*.amazonaws.com.usehttppath true &&";
  }

  content +=
    "git config --global credential.helper 'cache --timeout=3600' && git config --global credential.usehttppath true &&";

  const escapedUrl = shellEscape([cloneUrl]);

  content += `git clone ${escapedUrl} && exit\r`;

  // use app.restored to make sure only call clone command after all the assets are loaded
  app.restored.then(async () => {
    try {
      let openPath = PathExt.join(fullPath, repoName);
      openPath = openPath.replace('$HOME', '.');
      const files = await contents.get(openPath);
      if (files.type === 'directory') {
        openDefaultFile(fullPath, repoName, app, contents as ContentsManager);
        await fileBrowserModel.refresh();
        return;
      }
    } catch (error) {
      logger.info({ Message: 'Directory does not exist, creating directory.' });
    }

    const main = (await app.commands.execute('terminal:create-new')) as MainAreaWidget<ITerminal.ITerminal>;

    try {
      const terminal = main.content;

      terminal.session.send({
        type: 'stdin',
        content: [content],
      });
      app.commands.execute('launcher:create');
      terminal.session.connectionStatusChanged.connect(async (status) => {
        if (status.connectionStatus === 'disconnected') {
          openDefaultFile(fullPath, repoName, app, contents as ContentsManager);
          terminal.session.shutdown();
        }
      });
      await fileBrowserModel.refresh();
    } catch (error) {
      try {
        // Clean up partial clone
        const clonePath = PathExt.join(fullPath, repoName);
        await contents.delete(clonePath);
      } catch (cleanupError) {
        logger.error({ Message: 'Failed to cleanup partial clone' });
      }
      main.dispose();
      const errorMessage = error instanceof Error ? error.message : String(error);
      await showErrorMessageAsync(errorMessage);
    }
  });
};

const getProjectsList = async () => {
  let response;
  try {
    response = await fetchApiResponse(PROJECTS_LIST_URL, OPTIONS_TYPE.GET);
  } catch (error) {
    await showErrorMessageAsync(il18stringsError.defaultErrorMessage);
    throw error;
  }
  const results = await response.json();
  const { projectsList } = results;
  return projectsList;
};

const openDefaultFile = async (path: string, repoName: string, app: JupyterFrontEnd, contents: ContentsManager) => {
  let openPath = PathExt.join(path, repoName);
  openPath = openPath.replace('$HOME', '.');
  app.commands.execute('filebrowser:go-to-path', {
    path: openPath,
  });
  const files = await contents.get(openPath);
  if (files.type === 'directory') {
    const defaultFile = DEFAULT_FILES.find((file) => files.content.some((item: any) => item.name === file.name));
    if (defaultFile) {
      await app.commands.execute('docmanager:open', {
        path: PathExt.join(openPath, defaultFile.name),
        factory: defaultFile.factory,
      });
    }
  }
};

const validCloneUrl = (URL: string): boolean => {
  if (URL === '') {
    return false;
  }
  return /^https:\/\/[-\w.]+\.[A-Za-z]+\/[-\w@/.]+(?:\.git)?\/?(?:#.*)?$/.test(URL);
};

const showErrorMessageAsync = async (message: string) => {
  return showErrorMessage(il18stringsError.errorTitle, {
    message: message,
  });
};

export { executeCloneRepository, getProjectsList, openDefaultFile, validCloneUrl };
