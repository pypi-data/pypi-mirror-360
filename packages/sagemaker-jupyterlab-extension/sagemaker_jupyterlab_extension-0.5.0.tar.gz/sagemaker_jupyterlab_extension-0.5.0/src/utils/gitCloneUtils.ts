import { PathExt, URLExt } from '@jupyterlab/coreutils';
import { ContentsManager } from '@jupyterlab/services';
import { Dialog, showErrorMessage, MainAreaWidget } from '@jupyterlab/apputils';
import { il18Strings } from './../constants/il18Strings';
import { FilterFileBrowserModel } from '@jupyterlab/filebrowser';
import { JUPYTER_COMMAND_IDS } from '../constants';
import { ITerminal } from '@jupyterlab/terminal';
import { CommandRegistry } from '@lumino/commands';

enum CloneDirectoryStatus {
  CanClone,
  NotExist,
  AlreadyCloned,
}

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

interface AdditionalGitCloneOptions {
  repoPath: string;
  openREADME: boolean;
  findEnvironment: boolean;
}

const strHasLength = (str: unknown): str is string => typeof str === 'string' && str.length > 0;

const validCloneUrl = (URL: string): boolean => {
  return /^(https:\/\/|git)([:/@.~\-_a-zA-Z0-9])+$/.test(URL);
};

const getRepoName = (URL: string): string => {
  const parsedURL = URLExt.parse(URL);
  return PathExt.basename(parsedURL.pathname, '.git');
};

const openDefaultFile = async (path: string, contents: ContentsManager, commands: CommandRegistry) => {
  const files = await contents.get(path);
  if (files.type === 'directory') {
    const defaultFile = DEFAULT_FILES.find((file) => files.content.some((item: any) => item.name === file.name));

    if (defaultFile) {
      await commands.execute(JUPYTER_COMMAND_IDS.openDocManager, {
        path: PathExt.join(path, defaultFile.name),
        factory: defaultFile.factory,
      });
    }
  }
};

const handleAdditionalCloneOptions = async (
  commands: CommandRegistry,
  contents: ContentsManager,
  options: AdditionalGitCloneOptions,
) => {
  const { repoPath, openREADME } = options;
  await commands.execute(JUPYTER_COMMAND_IDS.goToPath, {
    path: repoPath,
  });
  if (openREADME === true) {
    try {
      // removed studioLogger
      await openDefaultFile(repoPath, contents, commands);
    } catch (error) {
      // studioLogger.error({
      //   schema: ClientSchemas.ClientError,
      //   message: ClientErrorMessage.OpenREADMEError + `: No README found at ${repoPath}` as ClientErrorMessage,
      //   error,
      // });
      // throw error;
    }
  }
};

// removed the passed from here - studioLogger ?: ILogger
const dirExists = async (path: string, contents: ContentsManager) => {
  let result;
  try {
    result = await contents.get(path);
  } catch (error) {
    // studioLogger.error({
    //   schema: ClientSchemas.ClientError,
    //   message: ClientErrorMessage.ValidRepoPathError + `: ${path} is an Invalid path ` as ClientErrorMessage,
    //   error: error,
    // });
    return false;
  }
  if (result.type === 'directory') {
    return true;
  }
  return false;
};

const checkCloneDirectoryStatus = async (
  contents: ContentsManager,
  clonePath: string,
  repoUrl: string,
  repoPath: string,
  // studioLogger?: ILogger
) => {
  const { errors } = il18Strings.GitClone;
  // removing passing studioLogger to the dirExists function
  const dExists = await dirExists(clonePath, contents);
  if (!dExists) {
    await showErrorMessage(errors.directoryNotExistTitle, {
      message: errors.directoryNotExistBody + clonePath,
    });
    return CloneDirectoryStatus.NotExist;
  }
  // removed: studioLogger being passed
  const alreadyExists = await dirExists(repoPath, contents);
  if (alreadyExists) {
    await showErrorMessage(errors.localGitCloneExistTitle, {
      message: errors.localGitCloneExistBody + repoUrl,
    });
    return CloneDirectoryStatus.AlreadyCloned;
  }
  return CloneDirectoryStatus.CanClone;
};

// Clone Git Repo and handle additional options
const gitCloneInTerminal = async (
  commands: CommandRegistry,
  contents: ContentsManager,
  additionalCloneOptions: AdditionalGitCloneOptions,
  fileBrowserModel: FilterFileBrowserModel,
  fullPath: string,
  URL: string,
  // studioLogger: ILogger,
) => {
  const { errors } = il18Strings.GitClone;
  const main = (await commands.execute(JUPYTER_COMMAND_IDS.createTerminal)) as MainAreaWidget<ITerminal.ITerminal>;
  let content = '';
  if (fullPath) {
    content += `cd ${fullPath} && `;
  }

  content += `git clone ${URL} && exit\r`;

  try {
    const terminal = main.content;

    terminal.session.send({
      type: 'stdin',
      content: [content],
    });
    terminal.session.connectionStatusChanged.connect(async (status) => {
      if (status.connectionStatus === 'disconnected') {
        try {
          await handleAdditionalCloneOptions(commands, contents, additionalCloneOptions);
        } catch (error) {
          await showErrorMessage(errors.failedOptions, errors.failedOptionsBody, [
            Dialog.warnButton({ label: 'DISMISS' }),
          ]);
        }
      }
    });

    await fileBrowserModel.refresh();
  } catch (error) {
    main.dispose();
    await showErrorMessage(errors.generalCloneErrorTitle, {
      message: errors.generalCloneErrorBody + error,
    });
  }
};

export {
  strHasLength,
  validCloneUrl,
  getRepoName,
  CloneDirectoryStatus,
  checkCloneDirectoryStatus,
  gitCloneInTerminal,
  AdditionalGitCloneOptions,
  handleAdditionalCloneOptions,
  openDefaultFile,
  dirExists,
};
