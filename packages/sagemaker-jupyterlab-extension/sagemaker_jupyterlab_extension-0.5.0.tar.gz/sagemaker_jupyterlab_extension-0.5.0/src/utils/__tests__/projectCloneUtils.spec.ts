import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { IRouter, JupyterFrontEnd } from '@jupyterlab/application';
import { MainAreaWidget } from '@jupyterlab/apputils';
import { FilterFileBrowserModel, IDefaultFileBrowser } from '@jupyterlab/filebrowser';
import { Contents, ContentsManager } from '@jupyterlab/services';
import { ITerminal } from '@jupyterlab/terminal';
import { CommandRegistry } from '@lumino/commands';
import { projectsListMock } from '../../service/__tests__/mock';
import { fetchApiResponse } from '../../service/index';
import { executeCloneRepository, getProjectsList, openDefaultFile, validCloneUrl } from '../projectCloneUtils';

jest.mock('@jupyterlab/apputils', () => ({
  ...jest.requireActual('@jupyterlab/apputils'),
  showErrorMessage: jest.fn(),
}));

jest.mock('../../service/index', () => ({
  ...jest.requireActual('../../service/index'),
  fetchApiResponse: jest.fn(),
}));

const fetchApiResponseMock = fetchApiResponse as jest.Mock;

describe('Repo Clone Utils', () => {
  describe('getProjectsList', () => {
    it('should return projects list', async () => {
      fetchApiResponseMock.mockResolvedValue({
        json: async () => projectsListMock,
      });
      const projects = await getProjectsList();

      expect(projects).toEqual(projectsListMock.projectsList);
    });
  });
  describe('openDefaultFile', () => {
    const createMocks = () => {
      const executeCommandMock = jest.fn();
      const mockCommands: Partial<CommandRegistry> = { execute: executeCommandMock };
      const mockApp: Partial<JupyterFrontEnd> = { commands: mockCommands as CommandRegistry };
      const mockGet = jest.fn();
      const mockContents: Partial<ContentsManager> = { get: mockGet };

      return {
        mockApp,
        mockContents,
        executeCommandMock,
        mockGet,
      };
    };

    const verifyCommonAssertions = (executeCommandMock: jest.Mock, testPath: string, repo: string) => {
      expect(executeCommandMock).toHaveBeenCalledTimes(2);
      expect(executeCommandMock).toHaveBeenCalledWith('filebrowser:go-to-path', {
        path: `${testPath}/${repo}`,
      });
    };

    it('should find and open README.md', async () => {
      const { mockApp, mockContents, executeCommandMock, mockGet } = createMocks();
      mockGet.mockResolvedValue({
        type: 'directory',
        content: [{ name: 'README.md' }, { name: 'random-file.txt' }],
      });

      await openDefaultFile('test-path', 'repo', mockApp as JupyterFrontEnd, mockContents as ContentsManager);

      verifyCommonAssertions(executeCommandMock, 'test-path', 'repo');
      expect(executeCommandMock).toHaveBeenCalledWith('docmanager:open', {
        path: 'test-path/repo/README.md',
        factory: 'Markdown Preview',
      });
    });

    it('should find and open README.ipynb', async () => {
      const { mockApp, mockContents, executeCommandMock, mockGet } = createMocks();
      mockGet.mockResolvedValue({
        type: 'directory',
        content: [{ name: 'README.ipynb' }, { name: 'random-file.txt' }],
      });

      await openDefaultFile('test-path', 'repo', mockApp as JupyterFrontEnd, mockContents as ContentsManager);

      verifyCommonAssertions(executeCommandMock, 'test-path', 'repo');
      expect(executeCommandMock).toHaveBeenCalledWith('docmanager:open', {
        path: 'test-path/repo/README.ipynb',
        factory: 'Notebook',
      });
    });
  });

  describe('validCloneUrl', () => {
    const testUrls = (urls: string[], expectedResult: boolean) => {
      urls.forEach((url) => expect(validCloneUrl(url)).toBe(expectedResult));
    };

    it('should return true for valid HTTPS URLs', () => {
      const validHttpsUrls = [
        'https://github.com/user/repo.git',
        'https://github.com/user/repo',
        'https://github.com/org/project.git',
        'https://github.com/org/project',
        'https://gitlab.com/username/project.git',
        'https://gitlab.com/username/project',
        'https://github.enterprise.com/org/repo.git',
        'https://github.enterprise.com/org/repo',
      ];
      testUrls(validHttpsUrls, true);
    });

    it('should return false for SSH URLs', () => {
      const sshUrls = [
        'git@github.com:username/repo.git',
        'git@github.com:username/repo',
        'git@gitlab.com:org/project.git',
        'git@gitlab.com:org/project',
        'ssh://git@github.com/username/repo.git',
        'ssh://git@github.com/username/repo',
        'git://github.com/username/repo.git',
        'git://github.com/username/repo',
      ];
      testUrls(sshUrls, false);
    });

    it('should return false for URLs with invalid characters', () => {
      const invalidUrls = [
        'http://github.com/user/repo',
        'ftp://github.com/user/repo',
        'https://github .com/repo',
        'https://.com/test',
        'https://',
        'not-a-url',
        '',
      ];
      testUrls(invalidUrls, false);
    });

    it('should return false for malformed URLs', () => {
      const malformedUrls = ['', 'not-a-url', 'http://', 'git@', 'https://.com', 'git@github.com'];
      testUrls(malformedUrls, false);
    });

    it('should return false for URLs with invalid protocols', () => {
      const invalidProtocolUrls = ['http://github.com/repo.git', 'svn://github.com/user/repo'];
      testUrls(invalidProtocolUrls, false);
    });
  });

  describe('executeCloneRepository', () => {
    interface MockSetup {
      mockRouter: Partial<IRouter>;
      mockApp: Partial<JupyterFrontEnd>;
      mockLogger: Partial<ILogger>;
      mockContents: Partial<Contents.IManager>;
      mockFileBrowser: Partial<IDefaultFileBrowser>;
      executeCommandMock: jest.Mock;
    }

    const setupMocks = (searchQuery = ''): MockSetup => {
      const mockLocation: Partial<IRouter.ILocation> = { search: searchQuery };
      const mockRouter: Partial<IRouter> = { current: mockLocation as IRouter.ILocation };
      const mockLogger: Partial<ILogger> = {
        error: jest.fn(),
        info: jest.fn(),
      };
      const mockGet = jest.fn(() => Promise.reject());
      const mockContents: Partial<Contents.IManager> = { get: mockGet };
      const mockTerminal: Partial<MainAreaWidget<ITerminal.ITerminal>> = { dispose: jest.fn() };
      const executeCommandMock = jest.fn().mockReturnValue(mockTerminal);
      const mockCommands: Partial<CommandRegistry> = { execute: executeCommandMock };
      const mockApp: Partial<JupyterFrontEnd> = {
        commands: mockCommands as CommandRegistry,
        restored: Promise.resolve(),
      };
      const mockModel: Partial<FilterFileBrowserModel> = { refresh: jest.fn() };
      const mockFileBrowser: Partial<IDefaultFileBrowser> = {
        model: mockModel as FilterFileBrowserModel,
      };

      return {
        mockRouter,
        mockApp,
        mockLogger,
        mockContents,
        mockFileBrowser,
        executeCommandMock,
      };
    };

    const executeTest = async (setup: MockSetup) => {
      fetchApiResponseMock.mockResolvedValue({
        json: async () => projectsListMock,
      });
      await executeCloneRepository(
        setup.mockRouter as IRouter,
        setup.mockApp as JupyterFrontEnd,
        setup.mockLogger as ILogger,
        setup.mockContents as Contents.IManager,
        setup.mockFileBrowser as IDefaultFileBrowser,
      );
    };

    it('should handle case when no repository URL is provided', async () => {
      const setup = setupMocks();
      await executeTest(setup);
      expect(setup.mockLogger.info).not.toHaveBeenCalled();
      expect(setup.mockLogger.error).toHaveBeenCalled();
    });

    it('should handle invalid repository URL from query parameters', async () => {
      const setup = setupMocks('?clone_url=invalid-url');
      await executeTest(setup);
      expect(setup.executeCommandMock).not.toHaveBeenCalled();
      expect(setup.mockLogger.error).toHaveBeenCalled();
    });

    it('should handle invalid project name', async () => {
      const setup = setupMocks(
        '?project_name=fake-project&&repo_name=test-repo&&clone_url=https://github.com/user/repo.git',
      );
      await executeTest(setup);
      expect(setup.executeCommandMock).not.toHaveBeenCalled();
      expect(setup.mockLogger.error).toHaveBeenCalled();
    });

    it('should run with no errors', async () => {
      const setup = setupMocks(
        '?project_name=project1&&repo_name=test-repo&&clone_url=https://github.com/user/repo.git',
      );
      await executeTest(setup);
      expect(setup.mockLogger.error).not.toHaveBeenCalled();
    });
  });
});
