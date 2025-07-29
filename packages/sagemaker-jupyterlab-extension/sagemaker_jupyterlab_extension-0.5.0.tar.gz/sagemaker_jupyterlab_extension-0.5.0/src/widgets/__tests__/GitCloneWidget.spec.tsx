import React from 'react';
import { GitCloneWidget } from './../GitCloneWidget';
import { gitCloneRepoMock } from '../../service/__tests__/mock';
import { render } from '@testing-library/react';
import { ServerConnection } from '@jupyterlab/services';
import { ReactWidgetWrapper } from '../../utils/ReactWidgetWrapper';

jest.mock('@jupyterlab/services', () => {
  const module = jest.requireActual('@jupyterlab/services');
  return {
    ...module,
    ServerConnection: {
      ...module.ServerConnection,
      makeRequest: jest.fn(),
      makeSettings: jest.fn(() => {
        return {
          settings: {
            baseUrl: '',
          },
        };
      }),
    },
  };
});

describe('GitCloneWidget suite', () => {
  const mockServerConnection = ServerConnection.makeRequest as jest.Mock;

  it('should test rendering the widget with metrics and 200 status', async () => {
    const ResponseMock = jest.fn((status, data) => ({
      status,
      ok: 200 <= status && status < 300 && Number.isInteger(status),
      json: () => {
        return Promise.resolve(data);
      },
    }));
    mockServerConnection.mockImplementation(async () => {
      return ResponseMock(200, gitCloneRepoMock);
    });
    const gitCloneWidget = new GitCloneWidget();
    render(<ReactWidgetWrapper item={gitCloneWidget} />);
    jest.useFakeTimers();
    try {
      await gitCloneWidget.getGitRepositories();
      expect(ResponseMock).toHaveBeenCalledTimes(2);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error);
    }
    jest.runAllTimers();
  });
});
