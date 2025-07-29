import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';
import { pluginIds } from '../constants';
//@TODO: need to revisit importing core libraries to improve performance
import moment from 'moment';
import {
  getExpiryTimeCookie,
  updateConnectionLostHandler,
  activateSignInComponent,
  activateRenewSessionComponent,
  isSSOMode,
  isSessionExpired,
} from './../utils/sessionManagerUtils';
import { POLL_TIME_MILLIS, TIME_INTERVAL_MILLIS } from '../constants/sessionManagementConstants';
import { Poll } from '@lumino/polling';
import { Widget } from '@lumino/widgets';
import { each } from '@lumino/algorithm';
import { DocumentRegistry, TextModelFactory } from '@jupyterlab/docregistry';
import { ServiceManager } from '@jupyterlab/services';
import { DocumentManager } from '@jupyterlab/docmanager';

const checkIfCookieIsExpired = (
  app: JupyterFrontEnd,
  sessionsManager: any,
  saveAllFilesCallback: () => void,
  stopSessionPolling: () => void,
  startSessionPolling: () => void,
  setDismissTimeValue: (value: number) => void,
  getDismissTimeValue: () => undefined | number,
) => {
  const expiryTimeCookieValue = getExpiryTimeCookie();
  const dismissTime = getDismissTimeValue();
  const dismissedPlus5mins = dismissTime && dismissTime + TIME_INTERVAL_MILLIS.fiveMinuteIntervalMilliseconds;
  if (expiryTimeCookieValue === null) {
    // Session is not expired, dont show any dialog
    updateConnectionLostHandler(app, false);
  } else {
    const expiryTime = moment.unix(expiryTimeCookieValue / 1000); // unix timestamp in seconds
    const remainingTime = expiryTime.diff(moment());
    const currentTime = Date.now();
    if (isSessionExpired(isSSOMode(), expiryTimeCookieValue, remainingTime)) {
      // session expired, first dismiss all other dialogs, including Server Connection Error dialog
      stopSessionPolling();
      activateSignInComponent(app, sessionsManager, startSessionPolling);
    } else if (
      remainingTime <= TIME_INTERVAL_MILLIS.fifteenMinuteIntervalMilliseconds &&
      (dismissTime === undefined || (dismissedPlus5mins && currentTime > dismissedPlus5mins))
    ) {
      // session not expired 15 mins or less remains, show Server Connection Error dialog
      // Stop polling once the dialog rendered to let th user take an action
      // else the dialog will never close
      stopSessionPolling();
      activateRenewSessionComponent(
        app,
        (sessionsManager as any)._sessions,
        saveAllFilesCallback,
        startSessionPolling,
        setDismissTimeValue,
      );
      updateConnectionLostHandler(app, false);
    } else {
      // session is not expired, show Server Connection Error dialog
      updateConnectionLostHandler(app, false);
    }
  }
};

const generatePollingObject = (
  app: JupyterFrontEnd,
  sessionsManager: any,
  saveAllFilesCallback: () => void,
  stopSessionPolling: () => void,
  startSessionPolling: () => void,
  setDismissTimeValue: (value: number) => void,
  getDismissTimeValue: () => number | undefined,
) => {
  return new Poll({
    auto: true,
    factory: async () => {
      return checkIfCookieIsExpired(
        app,
        sessionsManager,
        saveAllFilesCallback,
        stopSessionPolling,
        startSessionPolling,
        setDismissTimeValue,
        getDismissTimeValue,
      );
    },
    frequency: {
      interval: POLL_TIME_MILLIS.regularPollTimeMilliseconds,
      backoff: true, // Enable exponential backoff
      max: POLL_TIME_MILLIS.pollingMaxFrequency,
    },
  });
};

/**
 * A plugin for session management used to provide notification for SageMaker JupyterLab users.
 * When the JupyterLab workspace's expiryTime cookie is about to expire, it will popup a notification window in the user interface.
 * Will also allow the user to renew the session when there are 5 mins remaining for it to expire
 */
const SessionManagementPlugin: JupyterFrontEndPlugin<void> = {
  id: pluginIds.SessionManagementPlugin,
  requires: [],
  autoStart: true,
  activate: async (app: JupyterFrontEnd) => {
    // @TODO: Add in logging
    // @TODO: Add in translator in next cr

    // variable to track when the user
    let dismissTime: number | undefined = undefined;

    const setDismissTimeValue = (value: number) => {
      dismissTime = value;
    };

    const getDismissTimeValue = () => {
      return dismissTime;
    };

    /**
     * saveWidget function will save current open notebooks.
     */
    const saveAllFilesCallback = () => {
      const textModelFactory = new TextModelFactory();
      const registry = new DocumentRegistry({ textModelFactory });
      const services = new ServiceManager({});
      const docManager = new DocumentManager({
        registry,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        manager: services as any,
        opener: {
          open: (widget: Widget) => {
            // no-open
          },
          get opened() {
            return {
              connect: () => {
                return false;
              },
              disconnect: () => {
                return false;
              },
            };
          },
        },
      });
      each(app.shell.widgets('main'), (w: Widget) => {
        const context = docManager.contextForWidget(w);
        if (context === undefined) {
          return;
        }
        context
          .save()
          .then(() => context.createCheckpoint())
          .catch((err: { message: string }) => {
            // If the save was canceled by user-action, do nothing.
            if (err.message === 'Cancel') {
              return;
            }
            throw err;
          });
      });
    };

    const sessionsManager = app.serviceManager.sessions;

    const stopSessionPolling = () => {
      myPoll.stop();
    };

    const startSessionPolling = () => {
      myPoll.start();
    };

    const myPoll = generatePollingObject(
      app,
      sessionsManager,
      saveAllFilesCallback,
      stopSessionPolling,
      startSessionPolling,
      setDismissTimeValue,
      getDismissTimeValue,
    );
    startSessionPolling();
  },
};

export { SessionManagementPlugin, generatePollingObject, checkIfCookieIsExpired };
