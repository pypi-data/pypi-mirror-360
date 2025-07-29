import { ILogger, SchemaDefinition } from '@amzn/sagemaker-jupyterlab-extension-common';

declare global {
  export interface Window {
    panorama: any;
  }
}

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { name, version } = require('../../package.json');

const getLoggerForPlugin = (baseLogger: ILogger, pluginId: string, schema?: SchemaDefinition) =>
  baseLogger.child(
    {
      ExtensionName: name,
      ExtensionVersion: version,
      PluginId: pluginId,
    },
    schema,
  );

export { getLoggerForPlugin };
