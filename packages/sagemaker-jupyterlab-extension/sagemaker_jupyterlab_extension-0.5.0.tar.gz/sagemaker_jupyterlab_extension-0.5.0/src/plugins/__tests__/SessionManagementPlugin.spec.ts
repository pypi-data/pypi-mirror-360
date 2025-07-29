import { JupyterFrontEnd } from '@jupyterlab/application';
import { SessionManagementPlugin, checkIfCookieIsExpired, generatePollingObject } from './../SessionManagementPlugin';
import * as utils from './../../utils/sessionManagerUtils';
import moment from 'moment';

jest.mock('@jupyterlab/application', () => jest.fn as jest.Mock);
jest.mock('@jupyterlab/apputils');
jest.mock('@jupyterlab/docregistry', () => jest.fn as jest.Mock);
jest.mock('@jupyterlab/services', () => jest.fn as jest.Mock);
jest.mock('@jupyterlab/docmanager', () => jest.fn as jest.Mock);
jest.mock('@lumino/polling', jest.Mock);

beforeEach(() => {
  jest.clearAllMocks();
});

const generateCookieValue = () => {
  return moment()
    .add(5 * 60 * 10000)
    .valueOf();
};

describe('SessionManagementPlugin suite', () => {
  const app = {
    serviceManager: {
      sessions: {} as any,
      connectionFailure: {
        disconnect: jest.fn(),
        connect: jest.fn(),
      },
    },
  } as JupyterFrontEnd;

  const sessionManagerMock = app.serviceManager.sessions;
  const saveAllFilesCallbackMock = jest.fn();
  const stopSessionPollingMock = jest.fn();
  const startSessionPollingMock = jest.fn();
  const setDismissTimeValueMock = jest.fn();
  const getDismissTimeValueMock = jest.fn();

  it('Should call generatePollingObject to create a new poll start polling activate is called', async () => {
    const pollingObjectMock = generatePollingObject(
      app,
      sessionManagerMock,
      saveAllFilesCallbackMock,
      stopSessionPollingMock,
      startSessionPollingMock,
      setDismissTimeValueMock,
      getDismissTimeValueMock,
    );
    expect(pollingObjectMock.dispose).toBeDefined();
    await SessionManagementPlugin.activate(app);
    pollingObjectMock.start();
    expect(pollingObjectMock.start).toHaveBeenCalledTimes(1);
  });

  it('should test calling the function checkIfCookieIsExpired when expiry cookie is null ', () => {
    jest.spyOn(utils, 'updateConnectionLostHandler');
    checkIfCookieIsExpired(
      app,
      sessionManagerMock,
      saveAllFilesCallbackMock,
      stopSessionPollingMock,
      startSessionPollingMock,
      setDismissTimeValueMock,
      getDismissTimeValueMock,
    );
    expect(utils.updateConnectionLostHandler).toHaveBeenCalledTimes(1);
  });

  // cookie expired - authMode Sso and redicectURL
  it('should test calling the function checkIfCookieIsExpired when cookie is not expired ', () => {
    const cookieValue = generateCookieValue();
    document.cookie = `expiryTime=${cookieValue}`;
    document.cookie = 'authMode=Sso';
    document.cookie =
      'redirectURL="https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test"';
    jest.spyOn(utils, 'activateRenewSessionComponent');
    checkIfCookieIsExpired(
      app,
      sessionManagerMock,
      saveAllFilesCallbackMock,
      stopSessionPollingMock,
      startSessionPollingMock,
      setDismissTimeValueMock,
      getDismissTimeValueMock,
    );
    expect(utils.updateConnectionLostHandler).toHaveBeenCalledTimes(1);
  });

  it('should test calling the function checkIfCookieIsExpired when cookie is expired ', () => {
    const cookieValue = 1692309600000;
    document.cookie = `expiryTime=${cookieValue}`;
    document.cookie = 'authMode=Iam';
    document.cookie =
      'redirectURL="https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test"';
    jest.spyOn(utils, 'activateSignInComponent');
    checkIfCookieIsExpired(
      app,
      sessionManagerMock,
      saveAllFilesCallbackMock,
      stopSessionPollingMock,
      startSessionPollingMock,
      setDismissTimeValueMock,
      getDismissTimeValueMock,
    );
    expect(utils.activateSignInComponent).toHaveBeenCalledTimes(1);
  });

  it('should test calling the function checkIfCookieIsExpired and there is less than 12 mins remaining for cookie expiry', () => {
    const cookieValue = moment()
      .add(12 * 60 * 1000)
      .valueOf();
    document.cookie = `expiryTime=${cookieValue}`;
    document.cookie = 'authMode=Iam';
    document.cookie =
      'redirectURL="https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test"';
    jest.spyOn(utils, 'activateRenewSessionComponent');
    checkIfCookieIsExpired(
      app,
      sessionManagerMock,
      saveAllFilesCallbackMock,
      stopSessionPollingMock,
      startSessionPollingMock,
      setDismissTimeValueMock,
      getDismissTimeValueMock,
    );
    expect(utils.activateRenewSessionComponent).toHaveBeenCalledTimes(1);
    expect(stopSessionPollingMock).toHaveBeenCalledTimes(1);
  });
});
