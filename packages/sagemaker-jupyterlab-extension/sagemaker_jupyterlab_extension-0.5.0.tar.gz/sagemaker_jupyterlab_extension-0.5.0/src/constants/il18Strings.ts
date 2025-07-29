export const il18Strings = {
  SignInSession: {
    closeButton: 'Close',
    signInButton: 'Sign In',
    saveButton: 'Save',
    saveAndRenewButton: 'Save and renew session',
    signinDialog: {
      title: 'Please sign in again',
      restartSessionBody:
        'You were logged out of your account. You are not able to perform actions in your workplace at this time. Please start a new session.',
      loggedOutBody: "You were logged out of your account. Choose 'Sign In' to continue using this workplace.",
    },
    sessionExpiredDialog: {
      title: 'Session Expired please signin',
    },
    renewSessionDialog: {
      title: 'Session expiring soon',
      defaultBodyText: 'If your session expires, you could lose unsaved changes.',
      renewSessionBody:
        'To renew the session, log out from Studio App via "File" -> "Log Out" and then "Sign out" from AWS IAM Identity Center (successor to AWS SSO) user portal.',
      saveAllChanges: 'Do you want to save all changes now?',
      renewSessionNow: 'Do you want to renew your session now?',
      remindText: 'Remind me in 5 minutes',
      soonExpiringSessionBody: 'This session will expire soon.',
      contDownTimerMessage: 'This session will expire ',
      fromNow: 'from now.',
      loseUnsavedChanges: 'If your session expires, you could lose unsaved changes.',
    },
  },
  ResourceUsage: {
    cpuMetricTitle: 'CPU:',
    memoryMetricTitle: 'MEM:',
    storageMetricTitle: 'Storage:',
    instanceMemoryProgressBarTitle: 'Instance MEM',
    instanceMetricsTitle: 'Instance',
    stoargeSpaceLimitDialog: {
      title: 'Free up storage space',
    },
  },
  GitClone: {
    dialogTitle: 'Clone Git Repository',
    repoTitle: 'Git repositories URL(.git):',
    pathTitle: 'Project directory to clone into:',
    afterCloningTitle: 'After cloning',
    openReadMeFilesLabel: 'Open README files.',
    cancelButton: 'Cancel',
    cloneButton: 'Clone',
    errors: {
      directoryNotExistTitle: 'Destination directory doesn’t exist.',
      directoryNotExistBody:
        'The destination directory doesn’t exist. Create this directory and then try cloning the repository again. directory: ',
      localGitCloneExistTitle: 'Repository clone already exists in project.',
      localGitCloneExistBody:
        'It looks like the Git repository has already been cloned into the given directory. Click Dismiss to navigate to your existing clone. repositoy: ',
      noURLErrorTitle: 'Missing valid URL.',
      noURLErrorBody: 'No URL listed to clone the repository. Please input a valid URL ending with ".git".',
      generalCloneErrorTitle: 'Unable to clone repository to project.',
      generalCloneErrorBody:
        'Something went wrong when trying to clone the repository to your project. Please try again later. ',
      failedOptions: 'Failed to handle additional options.',
      failedOptionsBody: 'Something went wrong when trying to open README file within the repo.',
      invalidCloneUrlTitle: 'Invalid URL provided',
      invalidCloneUrlBody: 'The URL provided is not valid. Please input a valid URL to clone.',
    },
  },
  Space: {
    privateSpaceHeader: 'Personal Studio',
    unknownUser: 'Unknown User',
    unknownSpace: 'Unknown Space',
  },
  ProjectsCloneRepo: {
    errorDialog: {
      errorTitle: 'Unable to clone repository',
      defaultErrorMessage: 'Something went wrong when cloning the repository.',
      invalidRequestErrorMessage: 'A request to clone the reposioty is invalid.',
      invalidProjectName: 'Invalid project name: Project does not exist.',
      invalidCloneUrlBody: 'The URL provided is not valid. Please input a valid URL to clone.',
    },
  },
};
