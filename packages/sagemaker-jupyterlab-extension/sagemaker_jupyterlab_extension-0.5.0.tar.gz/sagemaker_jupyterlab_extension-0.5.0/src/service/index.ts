import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';
import { SUCCESS_RESPONSE_STATUS } from './constants';

enum OPTIONS_TYPE {
  POST = 'POST',
  GET = 'GET',
}

type OptionsType = OPTIONS_TYPE;

/**
 * Function call to make API calls for the plugin
 */
const fetchApiResponse = async (endpoint: string, type: OptionsType) => {
  // @TODO: add in logger
  const settings = ServerConnection.makeSettings();
  const requestUrl = URLExt.join(settings.baseUrl, endpoint);
  try {
    const response = await ServerConnection.makeRequest(requestUrl, { method: type }, settings);
    if (!SUCCESS_RESPONSE_STATUS.includes(response.status)) {
      throw new Error('Unable to fetch data');
    }
    return response;
  } catch (error: any) {
    throw Error(error);
    // @TODO: add in logger
    // const { current: logger } = rootLoggerContainer;
    // if (logger) {
    //   logger.warn({
    //     schema: ClientSchemas.ClientError,
    //     message: ClientErrorMessage.InstanceTypeNetworkError,
    //     error,
    //   });
    // }
  }
};

export { fetchApiResponse, OPTIONS_TYPE };
