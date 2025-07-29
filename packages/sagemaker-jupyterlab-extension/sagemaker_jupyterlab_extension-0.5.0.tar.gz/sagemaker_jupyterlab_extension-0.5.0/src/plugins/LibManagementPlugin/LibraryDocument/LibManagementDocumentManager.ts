import { DocumentManager } from '@jupyterlab/docmanager';
import { Contents } from '@jupyterlab/services';

import { initConfig } from '../config';

/**
 * Document manager for library configuration files
 * Extends JupyterLab's DocumentManager with functionality to create config files
 */
export class LibManagementDocumentManager extends DocumentManager {
  constructor(options: DocumentManager.IOptions) {
    super(options);
    this.autosave = false;
  }

  // Checks if a file exists at the given path
  async exist(path: string) {
    try {
      await this.services.contents.get(path);
      return true;
    } catch (err) {
      if (
        err &&
        typeof err === 'object' &&
        'response' in err &&
        err.response &&
        typeof err.response === 'object' &&
        'status' in err.response &&
        err.response.status === 404
      ) {
        return false;
      } else {
        throw err;
      }
    }
  }

  // Add a protected method that can be overridden in tests
  protected async _openOrReveal(path: string, widgetName: string) {
    return super.openOrReveal(path, widgetName);
  }

  // Opens an existing file or creates a new one with default config
  async openOrCreate(path: string, widgetName = 'default') {
    try {
      await this.services.contents.get(path);
    } catch (err) {
      if (
        err &&
        typeof err === 'object' &&
        'response' in err &&
        err.response &&
        typeof err.response === 'object' &&
        'status' in err.response &&
        err.response.status === 404
      ) {
        const currentTimestamp = new Date().toISOString();
        const model: Contents.IModel = {
          created: currentTimestamp,
          last_modified: currentTimestamp,
          mimetype: 'application/json',
          writable: true,
          type: 'file',
          format: 'text',
          name: path,
          path,
          content: JSON.stringify(initConfig),
        };
        await this.services.contents.save(path, model);
      } else {
        throw err;
      }
    }

    return this._openOrReveal(path, widgetName);
  }
}
