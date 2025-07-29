// size of new login window
const WIDTH = 800;
const HEIGHT = 600;

const COOKIE_KEYS = {
  // Name of the key of expiry time cookie
  expiryTime: 'expiryTime',

  // Name of the key of expiry time cookie to use when authMode=Sso
  // This is used to support backward compatability where LLAPS will pass ssoExpiryTimestamp along with expiryTime
  // This way, if the SSO customer don’t update their app, they will not see the Session expiring soon dialog (the same experience as before ),
  // but if they update their app, they will see the `new Session expiring soon` dialog with just the SAVE button
  ssoExpiryTimestamp: 'ssoExpiryTimestamp',

  // Name of the key of auth mode cookie
  authMode: 'authMode',

  // Name of the key of redirect url cookie
  redirectURL: 'redirectURL',
};

const COOKIE_VALUES = {
  authMode: {
    sso: 'Sso',
  },
};

const TIME_INTERVAL_MILLIS = {
  fiveMinuteIntervalMilliseconds: 5 * 60 * 1000,
  fifteenMinuteIntervalMilliseconds: 15 * 60 * 1000,
};

const POLL_TIME_MILLIS = {
  // The interval at which cookies are regularly polled to determine if session has expired or not
  regularPollTimeMilliseconds: 500,

  // The interval at which the signin window is polled to check if session has been refreshed
  loginWindowPollTimeMilliseconds: 100,

  // The maximum milliseconds between poll requests
  pollingMaxFrequency: 2 * 60 * 1000,
};

export { HEIGHT, WIDTH, COOKIE_KEYS, COOKIE_VALUES, TIME_INTERVAL_MILLIS, POLL_TIME_MILLIS };
