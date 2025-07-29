import { Contents, ContentsManager } from '@jupyterlab/services';
import { showErrorMessage } from '@jupyterlab/apputils';
import {
  validCloneUrl,
  openDefaultFile,
  dirExists,
  checkCloneDirectoryStatus,
  CloneDirectoryStatus,
  AdditionalGitCloneOptions,
  handleAdditionalCloneOptions,
  getRepoName,
  gitCloneInTerminal,
} from './../gitCloneUtils';
import { JUPYTER_COMMAND_IDS } from '../../constants';
import { CommandRegistry } from '@lumino/commands';
import { il18Strings } from './../../constants/il18Strings';

jest.mock('./../gitCloneUtils', () => ({
  ...jest.requireActual('./../gitCloneUtils'),
  dirExists: jest.fn(),
}));
const dirExistsMock = dirExists as jest.Mock;

jest.mock('@jupyterlab/apputils', () => ({
  ...jest.requireActual('@jupyterlab/apputils'),
  showErrorMessage: jest.fn(),
}));
const showErrorMessageMock = showErrorMessage as jest.Mock;

const mockLocalPath = 'test-clone-path';
const mockRepoPath = 'test-clone-path/test-repo-path';
const mockURL = 'test-repo-url';
const mockContentsModel: Contents.IModel = {
  name: 'bar',
  path: 'foo/bar',
  type: 'directory',
  created: 'yesterday',
  last_modified: 'today',
  writable: false,
  mimetype: '',
  content: [],
  format: 'json',
};

const { errors } = il18Strings.GitClone;

describe('Git Clone Utils', () => {
  it('validCloneUrl should return true for a URL with valid chars', () => {
    const repoUrls = [
      'https://github.com/aws/amazon-sagemaker-examples.git',
      'git@testgithub.com/repotest',
      'https://github.com/aws/amazon-sagemaker-examples',
      'https://username:password@github.com/repo/test.git',
    ];
    repoUrls.forEach((repoUrl) => expect(validCloneUrl(repoUrl)).toBe(true));
  });

  it('validCloneUrl should return false for a URL with invalid chars', () => {
    const repoUrls = [
      'https://github .com/aws/amazon-sagemaker-examples.git',
      'git@testgithub .com/repotest',
      'http://hub.com/aws/amazon-sagemaker-examples',
      'https://us@#ername@github.com/repo/test.git',
    ];
    repoUrls.forEach((repoUrl) => expect(validCloneUrl(repoUrl)).toBe(false));
  });

  xit('openDefaultFile should find and open README.md', async () => {
    const mockGet = jest.fn(() =>
      Promise.resolve({
        type: 'directory',
        content: [{ name: 'README.md' }, { name: 'random-file.txt' }],
      }),
    ) as jest.Mock;
    const executeCommandMock = jest.fn();
    const mockCommands: Partial<CommandRegistry> = { execute: executeCommandMock };
    const mockContents: Partial<ContentsManager> = { get: mockGet };

    await openDefaultFile('test-path', mockContents as ContentsManager, mockCommands as CommandRegistry);
    expect(executeCommandMock).toHaveBeenCalledTimes(1);
    expect(executeCommandMock).toHaveBeenCalledWith(JUPYTER_COMMAND_IDS.openDocManager, {
      path: 'test-path/README.md',
      factory: 'Markdown Preview',
    });
  });

  it('openDefaultFile should find and open README.ipynb', async () => {
    const mockGet = jest.fn(() =>
      Promise.resolve({
        type: 'directory',
        content: [{ name: 'README.ipynb' }, { name: 'random-file.txt' }],
      }),
    ) as jest.Mock;

    const mockContents: Partial<ContentsManager> = { get: mockGet };
    const executeCommandMock = jest.fn();
    const mockCommands: Partial<CommandRegistry> = { execute: executeCommandMock };

    await openDefaultFile('test-path', mockContents as ContentsManager, mockCommands as CommandRegistry);
    expect(executeCommandMock).toHaveBeenCalledTimes(1);
    expect(executeCommandMock).toHaveBeenCalledWith(JUPYTER_COMMAND_IDS.openDocManager, {
      path: 'test-path/README.ipynb',
      factory: 'Notebook',
    });
  });

  it('checkCloneDirectoryStatus should return CanClone if local directory exists and repo directory does not exist', async () => {
    dirExistsMock.mockImplementation((clonePath: string, _: ContentsManager) =>
      Promise.resolve(clonePath === mockLocalPath),
    );
    //if directory "exists" return mock contents, else throw an error.
    const mockContents: Partial<ContentsManager> = {
      get: jest.fn().mockImplementation((path: string) => {
        if (path === mockLocalPath) {
          return mockContentsModel;
        }
        throw new Error('Path does not exist');
      }),
    };

    const result = await checkCloneDirectoryStatus(
      mockContents as ContentsManager,
      mockLocalPath,
      mockURL,
      mockRepoPath,
    );
    expect(result).toBe(CloneDirectoryStatus.CanClone);
  });

  it('checkCloneDirectoryStatus should return NotExist if local directory does not exist', async () => {
    dirExistsMock.mockReturnValue(Promise.resolve(false));
    const mockContents: Partial<ContentsManager> = {
      get: jest.fn().mockImplementation((path: string) => {
        if (path === mockLocalPath) {
          throw new Error('Path does not exist');
        }
      }),
    };

    const result = await checkCloneDirectoryStatus(
      mockContents as ContentsManager,
      mockLocalPath,
      mockURL,
      mockRepoPath,
    );
    expect(result).toBe(CloneDirectoryStatus.NotExist);
    expect(showErrorMessageMock).toHaveBeenCalledWith(errors.directoryNotExistTitle, {
      message: errors.directoryNotExistBody + mockLocalPath,
    });
  });

  it('checkCloneDirectoryStatus should return AlreadyCloned if repo directory already exists', async () => {
    dirExistsMock.mockReturnValue(Promise.resolve(true));
    // path and repo path exist.
    const mockContents: Partial<ContentsManager> = {
      get: jest.fn().mockImplementation((path: string) => {
        if (path === mockRepoPath || path === mockLocalPath) {
          return mockContentsModel;
        }
        throw new Error('Path does not exist');
      }),
    };

    const result = await checkCloneDirectoryStatus(
      mockContents as ContentsManager,
      mockLocalPath,
      mockURL,
      mockRepoPath,
    );
    expect(result).toBe(CloneDirectoryStatus.AlreadyCloned);
    expect(showErrorMessageMock).toHaveBeenCalledWith(errors.localGitCloneExistTitle, {
      message: errors.localGitCloneExistBody + mockURL,
    });
  });

  it('should test handleAdditionalCloneOptions', async () => {
    const mockGet = jest.fn(() =>
      Promise.resolve({
        type: 'directory',
        content: [{ name: 'README.ipynb' }, { name: 'random-file.txt' }],
      }),
    ) as jest.Mock;

    const optionsMock: AdditionalGitCloneOptions = {
      repoPath: 'test',
      openREADME: true,
    };
    const mockContents: Partial<ContentsManager> = { get: mockGet };
    const executeCommandMock = jest.fn();
    const mockCommands: Partial<CommandRegistry> = { execute: executeCommandMock };

    await handleAdditionalCloneOptions(mockCommands as CommandRegistry, mockContents as ContentsManager, optionsMock);
    expect(executeCommandMock).toHaveBeenCalledTimes(2);
  });

  it('should test the getRepoName', () => {
    const urlMock = 'https://github.com/aws/amazon-sagemaker-examples.git';
    const repoName = getRepoName(urlMock);
    expect(repoName).toEqual('amazon-sagemaker-examples');
  });

  xit('should test gitCloneInTerminal function', async () => {
    const urlMock = 'https://github.com/aws/amazon-sagemaker-examples.git';
    const mockGet = jest.fn(() =>
      Promise.resolve({
        type: 'directory',
        content: [{ name: 'README.ipynb' }, { name: 'random-file.txt' }],
      }),
    ) as jest.Mock;

    const optionsMock: AdditionalGitCloneOptions = {
      repoPath: 'test',
      openREADME: true,
    };
    const mockContents: ContentsManager = { get: mockGet };
    const executeCommandMock = jest.fn();
    const mockCommands: CommandRegistry = { execute: executeCommandMock };
    const mockFactory: IFileBrowserFactory = {
      defaultBrowser: {
        model: jest.fn(),
      },
    };
    const fileBrowserModelMock = mockFactory.defaultBrowser.model;
    await gitCloneInTerminal(mockCommands, mockContents, optionsMock, fileBrowserModelMock, 'test', urlMock);
  });
});
