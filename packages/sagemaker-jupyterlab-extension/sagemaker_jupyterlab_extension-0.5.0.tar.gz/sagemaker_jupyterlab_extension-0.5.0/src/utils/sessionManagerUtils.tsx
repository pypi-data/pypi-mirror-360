import React from 'react';
import { ConnectionLost, JupyterFrontEnd } from '@jupyterlab/application';
import {
  COOKIE_KEYS,
  COOKIE_VALUES,
  POLL_TIME_MILLIS,
  WIDTH,
  HEIGHT,
  TIME_INTERVAL_MILLIS,
} from './../constants/sessionManagementConstants';
import { Dialog } from '@jupyterlab/apputils';
import moment from 'moment';
import { il18Strings } from './../constants';

class DismissTime {
  public _dismissTime = 0;
  public _count = 0;

  public setDismissTime(time: number) {
    if (time) {
      this._dismissTime = time;
      this._count = 1;
    }
  }

  public getDismissTime() {
    return this._dismissTime;
  }
}

const isSessionExpiredSSOMode = (expiryTimeCookie: number | null, isSSOMode: boolean): boolean => {
  return expiryTimeCookie === -1 && isSSOMode;
};

const isSessionExpiredIAMMode = (remainTime: number, isSSOMode: boolean): boolean => {
  return remainTime <= 0 && !isSSOMode;
};

const isSSOMode = (): boolean => {
  const authModeCookieMatches = getCookie(COOKIE_KEYS.authMode);
  return authModeCookieMatches && authModeCookieMatches[1] && authModeCookieMatches[1] === COOKIE_VALUES.authMode.sso;
};

/**
 * Get cookie value by given key name from browser
 * @param name - key name of the cookie field you want to get value for
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const getCookie = (name: string): any => {
  return document.cookie.match('\\b' + name + '="?([^;]*)"?\\b');
};

/**
 * get cookie value of EXPIRY_TIME
 * @param name
 */
const getExpiryTimeCookie = (): number | null => {
  const expiryTimeCookieMatches = getCookie(COOKIE_KEYS.expiryTime);
  const ssoExpiryTimeCookieMatches = getCookie(COOKIE_KEYS.ssoExpiryTimestamp);
  if (isSSOMode() && ssoExpiryTimeCookieMatches) {
    return Number(ssoExpiryTimeCookieMatches[1]);
  } else if (expiryTimeCookieMatches) {
    return Number(expiryTimeCookieMatches[1]);
  } else {
    return null;
  }
};

const isSessionExpired = (isSSOMode: boolean, expiryTimeCookieValue: number, remainTime: number) => {
  return isSessionExpiredSSOMode(expiryTimeCookieValue, isSSOMode) || isSessionExpiredIAMMode(remainTime, isSSOMode);
};

const updateConnectionLostHandler = (app: JupyterFrontEnd, isSessionExpired: boolean) => {
  isSessionExpired
    ? app.serviceManager?.connectionFailure.disconnect(ConnectionLost)
    : app.serviceManager?.connectionFailure.connect(ConnectionLost);
};

/**
 * get cookie value of REDIRECT_URL
 * use two different getCookie functions because the return values for cookie missing are different.
 * @param name
 */ //@TODO try add in type to be string | undefined rather than any
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const getRedirectURLCookie = (): any | undefined => {
  const refactorUrlCookieMatches = getCookie(COOKIE_KEYS.redirectURL);

  let redirectURL;
  try {
    redirectURL = new URL(refactorUrlCookieMatches ? refactorUrlCookieMatches[1] : undefined);
    if (redirectURL.protocol === 'http:' || redirectURL.protocol === 'https:') {
      return redirectURL.toString();
    }
  } catch (e) {
    return undefined;
  }

  return undefined;
};

/**
 * redirect To SignIn Page
 * When we get URL value from RedirectURL cookie, the function will popup a window to automatically log in
 * and close the window and reset the alarm after successfully logging in.
 * When we didn't get URL value, open a popup window of aws main page for user to log in
 * @param url
 */
export const openAndPollSignInWindow = (url: string, sessions: any) => {
  const prevCookieTime = getExpiryTimeCookie();
  const signInWindow = window.open(url, 'signin window', 'width=' + WIDTH + ', height=' + HEIGHT);
  let signInWindowAutoClosed = false;
  // Validate if the signin window has successfully extended the expiry time
  const pollTimer = window.setInterval(() => {
    if (signInWindow && signInWindow.closed && !signInWindowAutoClosed) {
      window.clearInterval(pollTimer);
      return;
    }
    // if the current expiryTime cookie value has been updated and larger than
    // the previous expiryTime cookie value then the signin window has successfully logged in
    // In case of SSO mode when the signin window has successfully logged in expiryTime is set
    // to undefined so getExpiryTimeCookie() would return NaN.
    const currCookieTime = getExpiryTimeCookie();
    if (currCookieTime !== null && prevCookieTime !== null) {
      if (currCookieTime > prevCookieTime || isNaN(currCookieTime)) {
        window.clearInterval(pollTimer);
        signInWindow && signInWindow.close();
        signInWindowAutoClosed = true;

        // Reconnect kernels for all sessions
        for (const session of sessions) {
          const kernel = session.kernel;
          kernel.reconnect();
        }
        Dialog.tracker.forEach((dialog: { reject: () => any }) => dialog.reject());
      }
    }
  }, POLL_TIME_MILLIS.loginWindowPollTimeMilliseconds);
};

/**
 * Next set of functions only for the display of the react component
 * @returns the dialog content, buttons and laucnhes the dialog
 */
const getSignInDialogContentAndLaunch = async () => {
  const { SignInSession } = il18Strings;
  const { signinDialog } = SignInSession;
  const redirectURL = getRedirectURLCookie();
  const buttons = redirectURL
    ? [Dialog.okButton({ label: SignInSession.signInButton })]
    : [Dialog.cancelButton({ label: SignInSession.closeButton })];
  const body = redirectURL ? (
    <div data-testid={'session-signin-log-out'}>{signinDialog.loggedOutBody}</div>
  ) : (
    <div data-testid={'session-signin-restart'}>{signinDialog.restartSessionBody}</div>
  );
  const confirmDialog = new Dialog({
    title: signinDialog.title,
    body: body,
    buttons: buttons,
    hasClose: false,
  });
  const sigInDialogResult = await confirmDialog.launch();
  return {
    sigInDialogResult,
    confirmDialog,
  };
};

/*
 * To activate and launch Session already expired flow
 */
const activateSignInComponent = async (app: JupyterFrontEnd, sessions: any, startSessionPolling: () => void) => {
  const { SignInSession } = il18Strings;
  const redirectURL = getRedirectURLCookie();
  Dialog.tracker.forEach((dialog: { reject: () => any }) => dialog.reject());

  // prevent the Server Connection Error dialog from showing up again until session is renewed
  updateConnectionLostHandler(app, true);
  const { sigInDialogResult, confirmDialog } = await getSignInDialogContentAndLaunch(); // this just launches the dialog
  if (sigInDialogResult && sigInDialogResult.button) {
    startSessionPolling();
    if (redirectURL) {
      openAndPollSignInWindow(getRedirectURLCookie(), sessions);
    } else {
      // Handle the event when user click on 'close' (when redirect url is not defined)
      if (sigInDialogResult && sigInDialogResult.button.label === SignInSession.closeButton) {
        const expiryTimecookie = getExpiryTimeCookie();
        const expTimeEpoch = expiryTimecookie && expiryTimecookie / 1000;
        const timeRemaining = expTimeEpoch && moment.unix(expTimeEpoch).diff(moment());
        if (
          timeRemaining !== null &&
          timeRemaining &&
          timeRemaining > TIME_INTERVAL_MILLIS.fiveMinuteIntervalMilliseconds
        ) {
          confirmDialog.dispose();
          setTimeout(async () => {
            await getSignInDialogContentAndLaunch();
          }, TIME_INTERVAL_MILLIS.fiveMinuteIntervalMilliseconds);
        }
      } else {
        confirmDialog.dispose();
        openAndPollSignInWindow(getRedirectURLCookie(), sessions);
      }
    }
  }
};

/**
 * Function to generate the content for renewing the session
 * @returns the dialog content, buttons and laucnhes the dialog
 */
const getRenewDialogContentAndLaunch = async () => {
  const { SignInSession } = il18Strings;
  const { renewSessionDialog } = il18Strings.SignInSession;
  const redirectUrlCookieValue = getRedirectURLCookie();

  const expiryCookieValue = getExpiryTimeCookie();
  const replacementText = expiryCookieValue && moment.unix(expiryCookieValue / 1000).fromNow();
  const countDownTimerMessage = `${renewSessionDialog.contDownTimerMessage}${replacementText}.`;
  const mainText = `${isSSOMode() ? renewSessionDialog.soonExpiringSessionBody : countDownTimerMessage}`;

  const SSOMessage = renewSessionDialog.renewSessionBody;
  const body = isSSOMode() ? (
    <>
      <div data-testid={'session-renew-lose-unsaved-changes'}>
        {mainText} {renewSessionDialog.loseUnsavedChanges} {renewSessionDialog.saveAllChanges}
      </div>
      <div>{SSOMessage}</div>
    </>
  ) : (
    <div data-testid={'session-renew-now'}>
      <p>{mainText}</p>
      <p>{renewSessionDialog.renewSessionNow}</p>
    </div>
  );
  const buttons = [
    Dialog.okButton({ label: renewSessionDialog.remindText }),
    redirectUrlCookieValue && Dialog.okButton({ label: SignInSession.saveAndRenewButton }),
  ];
  const confirmDialog = new Dialog({
    title: renewSessionDialog.title,
    body: body,
    buttons: buttons,
    hasClose: false,
  });
  const renewSessionDialogResult = await confirmDialog.launch();
  return {
    renewSessionDialogResult,
    confirmDialog,
  };
};

/*
 * To activate and launch the Session renewal flow
 */
const activateRenewSessionComponent = async (
  app: JupyterFrontEnd,
  sessions: any,
  saveAllFilesCallback: () => void,
  startSessionPolling: () => void,
  setDismissTimeValue: (value: any) => void,
) => {
  const { SignInSession } = il18Strings;
  const { renewSessionDialog } = il18Strings.SignInSession;
  const { renewSessionDialogResult, confirmDialog } = await getRenewDialogContentAndLaunch();
  if (renewSessionDialogResult && renewSessionDialogResult.button.label === renewSessionDialog.remindText) {
    const dismissTimeObject = new DismissTime();
    if (dismissTimeObject._count === 0) {
      dismissTimeObject.setDismissTime(Date.now());
      setDismissTimeValue(dismissTimeObject._dismissTime);
    } else {
      dismissTimeObject.getDismissTime();
    }
    // Close the Dialog and start polling again
    confirmDialog.dispose();
    startSessionPolling();
  } else if (renewSessionDialogResult && renewSessionDialogResult.button.label === SignInSession.saveAndRenewButton) {
    confirmDialog.dispose();
    // Callback when user click the renew button. Should save all files and pop the login window.
    saveAllFilesCallback();
    startSessionPolling();
    if (!isSSOMode()) {
      openAndPollSignInWindow(getRedirectURLCookie(), sessions);
    }
  }
};

export {
  getRedirectURLCookie,
  getExpiryTimeCookie,
  getCookie,
  isSSOMode,
  isSessionExpiredIAMMode,
  isSessionExpiredSSOMode,
  isSessionExpired,
  updateConnectionLostHandler,
  getSignInDialogContentAndLaunch,
  activateSignInComponent,
  getRenewDialogContentAndLaunch,
  activateRenewSessionComponent,
};
