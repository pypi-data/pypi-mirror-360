import { DocumentRegistry, DocumentWidget } from '@jupyterlab/docregistry';
import { Terminal } from '@jupyterlab/services';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';

import { LibraryConfigEditor } from '../LibraryConfigEditor';
import { libMgmtIcon } from '../config';

/**
 * Document widget for the library configuration editor
 * Wraps the LibraryConfigEditor in a DocumentWidget for JupyterLab integration
 */
export class LibraryDocumentWidget extends DocumentWidget<LibraryConfigEditor> {
  constructor(
    context: DocumentRegistry.Context,
    createTerminal: () => Promise<Terminal.ITerminalConnection>,
    openTerminal: (terminal: TerminalWidget) => void,
    logger?: ILogger,
  ) {
    const content = new LibraryConfigEditor(context, createTerminal, openTerminal, logger);
    super({ content, context });
    this.title.icon = libMgmtIcon;
  }
}
