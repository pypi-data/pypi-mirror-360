/**
 * Urls
 */
const INSTANCE_METRICS_URL = 'aws/sagemaker/api/instance/metrics';
const GIT_REPOSITORIES_URL = 'aws/sagemaker/api/git/list-repositories';
const SAGEMAKER_CONTEXT_URL = 'aws/sagemaker/api/context';
const PROJECTS_LIST_URL = 'aws/sagemaker/api/projects/list-projects';
const IS_MAXDOME_ENVIRONMENT_URL = 'aws/sagemaker/api/is-md-environment';

/**
 * Other Constants
 */
const METRICS_FETCH_INTERVAL_IN_MILLISECONDS = 5000;

/**
 * API calls constants
 */
const SUCCESS_RESPONSE_STATUS = [200, 201];

export {
  INSTANCE_METRICS_URL,
  GIT_REPOSITORIES_URL,
  METRICS_FETCH_INTERVAL_IN_MILLISECONDS,
  SUCCESS_RESPONSE_STATUS,
  SAGEMAKER_CONTEXT_URL,
  PROJECTS_LIST_URL,
  IS_MAXDOME_ENVIRONMENT_URL,
};
