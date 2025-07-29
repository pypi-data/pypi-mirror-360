import { ServerConnection } from '@jupyterlab/services';
import { INSTANCE_METRICS_URL } from '../constants';
import { OPTIONS_TYPE, fetchApiResponse } from './../index';
import { instanceMetricsMock } from './mock';

jest.mock('@jupyterlab/coreutils', jest.Mock);
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

describe('Service API calls test suite', () => {
  beforeAll(() => {
    jest.useFakeTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  it('Should test the fetchAPIResponse and return a response', async () => {
    const mockServerConnection = ServerConnection.makeRequest as jest.Mock;
    const ResponseMock = jest.fn((status, data) => ({
      status,
      ok: 200 <= status && status < 300 && Number.isInteger(status),
      json: () => {
        return Promise.resolve(data);
      },
    }));

    mockServerConnection.mockImplementation(async () => {
      return ResponseMock(200, instanceMetricsMock);
    });
    jest.useFakeTimers();
    try {
      await fetchApiResponse(INSTANCE_METRICS_URL, OPTIONS_TYPE.GET).then((response) => {
        expect(ResponseMock).toHaveBeenCalledTimes(1);
        expect(ResponseMock).toHaveBeenCalledWith(200, instanceMetricsMock);
      });
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error);
    }
  });

  it('Should test the fetchAPIResponse and throw an error', async () => {
    const mockServerConnection = ServerConnection.makeRequest as jest.Mock;
    const ResponseMock = jest.fn((status, data) => ({
      status,
      ok: 200 <= status && status < 300 && Number.isInteger(status),
      json: () => {
        return null;
      },
    }));
    mockServerConnection.mockImplementation(async () => {
      return ResponseMock(500, null);
    });
    jest.useFakeTimers();
    try {
      await fetchApiResponse(INSTANCE_METRICS_URL, OPTIONS_TYPE.GET);
      expect(ResponseMock).toHaveBeenCalledTimes(1);
      expect(ResponseMock).toHaveBeenCalledWith(500, null);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error);
    }
  });
});
