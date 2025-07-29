import { JupyterFrontEnd } from '@jupyterlab/application';
import { openAndPollSignInWindow } from './../sessionManagerUtils';
import React from 'react';
import { Dialog } from '@jupyterlab/apputils';
import { il18Strings } from './../../constants';
import * as utils from './../../utils/sessionManagerUtils';
import moment from 'moment';

const { signinDialog, renewSessionDialog, saveAndRenewButton, closeButton, signInButton } = il18Strings.SignInSession;

jest.mock('@jupyterlab/application', () => jest.fn as jest.Mock);
jest.mock('@jupyterlab/apputils');

afterEach(() => {
  jest.clearAllMocks();
});

beforeEach(() => {
  jest.clearAllMocks();
});

describe('Test getRedirectURLCookie utils function', function () {
  it('should test the URL cookie value with quotation mark on both sides', function () {
    document.cookie =
      'redirectURL="https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test"';
    const result = utils.getRedirectURLCookie();
    expect(result).toBe(
      'https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test',
    );
  });

  it('should test the URL cookie value with quotation mark on the right', function () {
    document.cookie =
      'redirectURL=https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test"';
    const result = utils.getRedirectURLCookie();
    expect(result).toBe(
      'https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test',
    );
  });

  it('should test the URL cookie value without quotation mark', function () {
    document.cookie =
      'redirectURL=https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test';
    const result = utils.getRedirectURLCookie();
    expect(result).toBe(
      'https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test',
    );
  });

  it('should test the URL cookie value with quotation mark on the left', function () {
    document.cookie =
      'redirectURL="https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test';
    const result = utils.getRedirectURLCookie();
    expect(result).toBe(
      'https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test',
    );
  });
});

// test global functions
describe('Test redirectToSignIn utils function', function () {
  it('should test redirect to aws official site', function () {
    window.open = jest.fn((url?: string, target?: string, features?: string, replace?: boolean) => {
      return jest.fn<Window, []>(() => ({
        ...jest.requireActual('@jupyterlab/services'),
        closed: true,
        close: jest.fn(),
      }))();
    });
    openAndPollSignInWindow('https://aws.amazon.com/', jest.fn(), null);
    expect(window.open).toBeCalled();
    expect(window.open).toBeCalledWith('https://aws.amazon.com/', 'signin window', 'width=800, height=600');
  });

  // @TODO: Debuging this in local - will enable in next cr
  it('should test the polltime', function () {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const spyOn = jest.spyOn(utils, 'openAndPollSignInWindow');

    class WindowMock {
      closed: boolean;
      constructor(closed: boolean) {
        this.closed = closed;
      }
    }
    window.open = jest.fn().mockReturnValue(new WindowMock(true));
    window.setInterval = jest.fn() as jest.Mock;
    window.clearInterval = jest.fn() as jest.Mock;
    const mockFun = jest.fn();
    const url = 'https:/www.amazon.com';
    jest.useFakeTimers();
    openAndPollSignInWindow(url, mockFun, null);
    expect(utils.openAndPollSignInWindow).toHaveBeenCalledTimes(1);
  });

  it('should test the redirect to fetched URL from cookie', function () {
    // different url
    const url = 'https:/www.amazon.com';
    openAndPollSignInWindow(url, jest.fn(), null);
    expect(window.open).toBeCalled();
    expect(window.open).toBeCalledWith(url, 'signin window', 'width=800, height=600');
  });
});

describe('Test activateSignInComponent for when the session has already expired and we need to allow the user to sign back in', () => {
  const sessions = {};
  const app = {
    commands: {
      addCommand: jest.fn(),
    },
  } as unknown as JupyterFrontEnd;

  // Cookie expired no redirect url
  it('Should call the openAndPollSignInWindow', async () => {
    jest.spyOn(utils, 'openAndPollSignInWindow');

    document.cookie = 'expiryTime=1692393309000';
    document.cookie =
      'redirectURL="https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test"';
    window.open = jest.fn((url?: string, target?: string, features?: string, replace?: boolean) => {
      return jest.fn<Window, []>(() => ({
        ...jest.requireActual('@jupyterlab/services'),
        closed: true,
        close: jest.fn(),
      }))();
    });
    const mockCloseButton = Dialog.cancelButton({ label: closeButton });
    const mockLaunch = jest.fn(() => ({
      button: {
        label: closeButton,
      },
    }));

    const expectedBody = <div data-testid={'session-signin-log-out'}>{signinDialog.loggedOutBody}</div>;
    Dialog.prototype.launch = mockLaunch;
    Dialog.prototype.buttons = [mockCloseButton];
    await utils.activateSignInComponent(app, sessions as any, jest.fn());
    expect(mockLaunch).toHaveBeenCalledTimes(1);
    expect(Dialog).toHaveBeenCalledWith({
      title: signinDialog.title,
      body: expectedBody,
      buttons: [mockCloseButton],
      hasClose: false,
    });
    await utils.activateSignInComponent(app, sessions as any, jest.fn());
    expect(utils.openAndPollSignInWindow).toHaveBeenCalledTimes(2);
  });

  // cookied expired and no redirect url - click signin button
  it('should launch the dialog with the signin button with the redirect url present in the cookie and signin button is clicked', async () => {
    document.cookie = 'expiryTime=1692393309000';
    document.cookie = 'redirectURL=undefined';
    window.open = jest.fn((url?: string, target?: string, features?: string, replace?: boolean) => {
      return jest.fn<Window, []>(() => ({
        ...jest.requireActual('@jupyterlab/services'),
        closed: true,
        close: jest.fn(),
      }))();
    });
    jest.spyOn(utils, 'openAndPollSignInWindow');

    const mockCloseButton = Dialog.cancelButton({ label: signInButton });
    const mockLaunch = jest.fn(() => ({
      button: {
        label: signInButton,
      },
    }));
    const mockStopSessionPolling = jest.fn();
    const expectedBody = <div data-testid={'session-signin-restart'}>{signinDialog.restartSessionBody}</div>;
    Dialog.prototype.launch = mockLaunch;
    Dialog.prototype.buttons = [mockCloseButton];

    await utils.activateSignInComponent(app, sessions as any, mockStopSessionPolling);
    expect(mockLaunch).toHaveBeenCalledTimes(1);
    expect(Dialog).toHaveBeenCalledWith({
      title: signinDialog.title,
      body: expectedBody,
      buttons: [mockCloseButton],
      hasClose: false,
    });
    const mockCancelButtonClick = jest.fn() as jest.Mock;
    Dialog.cancelButton.click = mockCancelButtonClick;
    Dialog.cancelButton.click();
    expect(mockCancelButtonClick).toHaveBeenCalledTimes(1);
  });

  // cookied expired and no redirect URL and click close button
  it('should launch the dialog with the signin button with No redirect url in the cookie and close button is clicked', async () => {
    document.cookie = 'expiryTime=1692393309000';
    document.cookie = 'redirectURL=undefined';
    const mockCloseButton = Dialog.cancelButton({ label: closeButton });
    const mockLaunch = jest.fn(() => ({
      button: {
        label: closeButton,
      },
    }));
    const mockStopSessionPolling = jest.fn();
    const expectedBody = <div data-testid={'session-signin-restart'}>{signinDialog.restartSessionBody}</div>;
    Dialog.prototype.launch = mockLaunch;
    Dialog.prototype.buttons = [mockCloseButton];
    jest.useFakeTimers();
    await utils.activateSignInComponent(app, sessions as any, mockStopSessionPolling);
    expect(mockLaunch).toHaveBeenCalledTimes(1);
    expect(Dialog).toHaveBeenCalledWith({
      title: signinDialog.title,
      body: expectedBody,
      buttons: [mockCloseButton],
      hasClose: false,
    });
    const mockCancelButton = jest.fn() as jest.Mock;
    Dialog.cancelButton.click = mockCancelButton;
    Dialog.cancelButton.click();
    expect(mockCancelButton).toHaveBeenCalledTimes(1);
    jest.runAllTimers();
  });

  it('should launch the dialog with the signin button with No redirect url in the cookie and close button is clicked', async () => {
    const currentTime = moment()
      .add(3 * 60 * 1000)
      .valueOf();
    document.cookie = `expiryTime=${currentTime}`;
    document.cookie = 'redirectURL=undefined';
    const mockCloseButton = Dialog.cancelButton({ label: closeButton });
    const mockLaunch = jest.fn(() => ({
      button: {
        label: closeButton,
      },
    }));
    const mockStopSessionPolling = jest.fn();
    const expectedBody = <div data-testid={'session-signin-restart'}>{signinDialog.restartSessionBody}</div>;
    Dialog.prototype.launch = mockLaunch;
    Dialog.prototype.buttons = [mockCloseButton];
    jest.useFakeTimers();
    await utils.activateSignInComponent(app, sessions as any, mockStopSessionPolling);
    expect(mockLaunch).toHaveBeenCalledTimes(1);
    expect(Dialog).toHaveBeenCalledWith({
      title: signinDialog.title,
      body: expectedBody,
      buttons: [mockCloseButton],
      hasClose: false,
    });
    const mockCancelButton = jest.fn() as jest.Mock;
    Dialog.cancelButton.click = mockCancelButton;
    Dialog.cancelButton.click();
    expect(mockCancelButton).toHaveBeenCalledTimes(1);
    jest.runAllTimers();
  });
});

describe('Test activateRenewSessionComponent suite', () => {
  const sessions = {};
  const saveAllFilesCallbackMock = jest.fn();
  const startSessionPollingMock = jest.fn();
  const setDismissTimeValueMock = jest.fn();
  const app = {
    commands: {
      addCommand: jest.fn(),
    },
  } as unknown as JupyterFrontEnd;

  // Sso Mode and Redirect url is present and 5 mins remain for session expiry
  it('should launch the dialog to remind the user  click remind me in 5 mins', async () => {
    const currentTime = moment()
      .add(5 * 60 * 1000)
      .valueOf();
    document.cookie = `expiryTime=${currentTime}`;
    document.cookie = '"authMode=Sso"';
    document.cookie =
      'redirectURL="https://console.aws.amazon.com/sagemaker/home?region=us-west-2&notebookState=L2FwaS90ZXJtaW5hbHM%3D#/notebook-instances/openNotebook/pengyey-test"';
    window.open = jest.fn((url?: string, target?: string, features?: string, replace?: boolean) => {
      return jest.fn<Window, []>(() => ({
        ...jest.requireActual('@jupyterlab/services'),
        closed: true,
        close: jest.fn(),
      }))();
    });

    const mockButton = Dialog.okButton({ label: renewSessionDialog.remindText });
    const mockLaunch = jest.fn(() => ({
      button: {
        label: renewSessionDialog.remindText,
        // onclick: jest.fn() as jest.Mock,
      },
    }));
    const expectedDialog = (
      <>
        <div data-testid={'session-renew-lose-unsaved-changes'}>
          {renewSessionDialog.soonExpiringSessionBody} {renewSessionDialog.loseUnsavedChanges}{' '}
          {renewSessionDialog.saveAllChanges}
        </div>
        <div>{renewSessionDialog.renewSessionBody}</div>
      </>
    );

    Dialog.prototype.launch = mockLaunch;
    Dialog.prototype.buttons = [mockButton];

    jest.useFakeTimers();
    await utils.activateRenewSessionComponent(
      app,
      sessions as any,
      saveAllFilesCallbackMock,
      startSessionPollingMock,
      setDismissTimeValueMock,
    );
    expect(mockLaunch).toHaveBeenCalledTimes(1);
    expect(Dialog).toHaveBeenCalledWith({
      title: renewSessionDialog.title,
      body: expectedDialog,
      buttons: [mockButton, undefined],
      hasClose: false,
    });
    const mockbuttonClick = jest.fn() as jest.Mock;
    Dialog.okButton.click = mockbuttonClick;
    Dialog.okButton.click();
    expect(mockbuttonClick).toHaveBeenCalledTimes(1);
    jest.runAllTimers();
  });

  // Iam Mode and with Redirect url is present and 5 mins remain for session expiry
  it('should launch the dialog and allow the user to click remind me in 5 mins', async () => {
    const currentTime = moment()
      .add(5 * 60 * 1000)
      .valueOf();
    document.cookie = `expiryTime=${currentTime}`;
    document.cookie = '"authMode=Iam"';
    document.cookie = document.cookie = 'redirectURL=undefined';
    window.open = jest.fn((url?: string, target?: string, features?: string, replace?: boolean) => {
      return jest.fn<Window, []>(() => ({
        ...jest.requireActual('@jupyterlab/services'),
        closed: true,
        close: jest.fn(),
      }))();
    });
    const mockButton = Dialog.okButton({ label: renewSessionDialog.remindText });
    const mockLaunch = jest.fn(() => ({
      button: {
        label: renewSessionDialog.remindText,
      },
    }));

    Dialog.prototype.launch = mockLaunch;
    Dialog.prototype.buttons = [mockButton];
    const expectedDialog = (
      <div data-testid={'session-renew-now'}>
        <p>This session will expire in 5 minutes.</p>
        <p>Do you want to renew your session now?</p>
      </div>
    );
    jest.useFakeTimers();
    await utils.activateRenewSessionComponent(
      app,
      sessions as any,
      saveAllFilesCallbackMock,
      startSessionPollingMock,
      setDismissTimeValueMock,
    );
    expect(mockLaunch).toHaveBeenCalledTimes(1);
    expect(Dialog).toHaveBeenCalledWith({
      title: renewSessionDialog.title,
      body: expectedDialog,
      buttons: [mockButton, undefined],
      hasClose: false,
    });
    const mockbuttonClick = jest.fn() as jest.Mock;
    Dialog.okButton.click = mockbuttonClick;
    Dialog.okButton.click();
    expect(mockbuttonClick).toHaveBeenCalledTimes(1);
    jest.runAllTimers();
  });

  it('should launch the dialog and allow the user to click save and renew the session button', async () => {
    const currentTime = moment()
      .add(5 * 60 * 1000)
      .valueOf();
    document.cookie = `expiryTime=${currentTime}`;
    document.cookie = '"authMode=Iam"';
    document.cookie = document.cookie = 'redirectURL=undefined';
    window.open = jest.fn((url?: string, target?: string, features?: string, replace?: boolean) => {
      return jest.fn<Window, []>(() => ({
        ...jest.requireActual('@jupyterlab/services'),
        closed: true,
        close: jest.fn(),
      }))();
    });
    const mockButton = Dialog.createButton({ label: saveAndRenewButton });
    const mockLaunch = jest.fn(() => ({
      button: {
        label: saveAndRenewButton,
      },
    }));

    Dialog.prototype.launch = mockLaunch;
    Dialog.prototype.buttons = [mockButton];
    const expectedDialog = (
      <div data-testid={'session-renew-now'}>
        <p>This session will expire in 5 minutes.</p>
        <p>Do you want to renew your session now?</p>
      </div>
    );
    await utils.activateRenewSessionComponent(
      app,
      sessions as any,
      saveAllFilesCallbackMock,
      startSessionPollingMock,
      setDismissTimeValueMock,
    );
    expect(mockLaunch).toHaveBeenCalledTimes(1);
    expect(Dialog).toHaveBeenCalledWith({
      title: renewSessionDialog.title,
      body: expectedDialog,
      buttons: [mockButton, undefined],
      hasClose: false,
    });
    const mockbuttonClick = jest.fn() as jest.Mock;
    Dialog.okButton.click = mockbuttonClick;
    Dialog.okButton.click();
    expect(mockbuttonClick).toHaveBeenCalledTimes(1);
  });
});

describe('Test getExpiryTimeCookie utils function', function () {
  it('should test the cookie value', function () {
    document.cookie = 'expiryTime=16000';
    document.cookie = 'authMode=Sso';

    const result = utils.getExpiryTimeCookie();
    expect(result).toBe(16000);
  });

  it('should test the cookie value when undefined', function () {
    document.cookie = 'expiryTime=undefined';
    const result = utils.getExpiryTimeCookie();
    expect(result).toBe(NaN);
  });
});
