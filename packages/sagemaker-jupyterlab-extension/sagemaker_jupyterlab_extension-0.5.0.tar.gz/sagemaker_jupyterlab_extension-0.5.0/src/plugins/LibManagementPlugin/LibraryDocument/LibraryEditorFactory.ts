import { ABCWidgetFactory, DocumentRegistry } from '@jupyterlab/docregistry';
import { Terminal } from '@jupyterlab/services';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';

import { LibraryDocumentWidget } from './LibraryDocumentWidget';

// Factory for creating library configuration editor widgets
export class LibraryEditorFactory extends ABCWidgetFactory<LibraryDocumentWidget> {
  private readonly _createTerminal: () => Promise<Terminal.ITerminalConnection>;
  private readonly _openTerminal: (terminal: TerminalWidget) => void;
  private readonly _logger?: ILogger;

  constructor(
    options: DocumentRegistry.IWidgetFactoryOptions<LibraryDocumentWidget>,
    createTerminal: () => Promise<Terminal.ITerminalConnection>,
    openTerminal: (terminal: TerminalWidget) => void,
    logger?: ILogger,
  ) {
    super(options);
    this._createTerminal = createTerminal;
    this._openTerminal = openTerminal;
    this._logger = logger;
  }

  // Creates a new library document widget for the given context
  protected createNewWidget(context: DocumentRegistry.Context) {
    return new LibraryDocumentWidget(context, this._createTerminal, this._openTerminal, this._logger);
  }
}
