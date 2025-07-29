import { ReactWidget } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { Terminal } from '@jupyterlab/services';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';
import { LabIcon, UseSignal, errorIcon } from '@jupyterlab/ui-components';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { SplitPanel } from '@lumino/widgets';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import React from 'react';

import { ERROR_MESSAGES } from './config';
import { LibraryConfigListWidget } from './LibraryConfigList';
import { LibraryConfigPanelWidget } from './LibraryConfigPanel';
import { LIBRARY_CONFIG_SCHEMA } from './schema';

/**
 * Main editor component for library configuration
 * Provides UI for managing conda packages and extensions
 */
export class LibraryConfigEditor extends SplitPanel {
  private _config: ReadonlyJSONObject = {};
  private _context: DocumentRegistry.Context;
  private _updateSpace = false;
  private readonly _createTerminal: () => Promise<Terminal.ITerminalConnection>;
  private readonly _openTerminal: (terminal: TerminalWidget) => void;
  private readonly _logger?: ILogger;

  constructor(
    context: DocumentRegistry.Context,
    createTerminal: () => Promise<Terminal.ITerminalConnection>,
    openTerminal: (terminal: TerminalWidget) => void,
    logger?: ILogger,
  ) {
    super({
      orientation: 'horizontal',
      renderer: SplitPanel.defaultRenderer,
      spacing: 1,
    });
    this._context = context;
    this._createTerminal = createTerminal;
    this._openTerminal = openTerminal;
    this._logger = logger;
    this.onCheckUpdateSpace = this.onCheckUpdateSpace.bind(this);
    this.onChange = this.onChange.bind(this);
    this.onSave = this.onSave.bind(this);
    this._initialize()
      .then(() => {
        this.addClass('jp-SettingsPanel');
        const list = new LibraryConfigListWidget({
          schema: LIBRARY_CONFIG_SCHEMA,
          updateSpace: this._updateSpace,
          onCheckUpdateSpace: this.onCheckUpdateSpace,
          onSave: this.onSave,
        });
        list.handleSelectSourceSignal.connect(() => {
          this.update();
        });
        this.addWidget(list);
        const libManagementPanel = ReactWidget.create(
          <UseSignal signal={list.handleSelectSourceSignal}>
            {() => (
              <LibraryConfigPanelWidget
                schema={LIBRARY_CONFIG_SCHEMA}
                configs={this._config}
                handleSelectTypeSignal={list.handleSelectTypeSignal}
                handleSelectSourceSignal={list.handleSelectSourceSignal}
                onConfigsChange={this.onChange}
                setError={list.setError}
              />
            )}
          </UseSignal>,
        );
        this.addWidget(libManagementPanel);
      })
      .catch((e) => {
        this._logger?.error({
          Message: 'Error loading widget due to corrupt configuration file',
          Error: e as Error,
        });
        this.addWidget(
          ReactWidget.create(
            <div className="jp-PluginList-entry-label">
              <LabIcon.resolveReact icon={errorIcon} iconClass={'jp-Icon'} tag="span" stylesheet="settingsEditor" />
              {ERROR_MESSAGES.CORRUPTED_CONFIG_FILE(this._context.path)}
            </div>,
          ),
        );
      });
  }

  // Updates the "apply to space" setting checkbox
  onCheckUpdateSpace(updateSpace: boolean) {
    this._updateSpace = updateSpace;
    const newConfigs = JSON.parse(JSON.stringify(this._config));
    newConfigs['ApplyChangeToSpace'] = updateSpace;
    this._context.model.fromJSON(newConfigs);
  }

  // Handles configuration changes
  onChange(configs: ReadonlyJSONObject) {
    this._context.model.fromJSON(configs);
    this._config = configs;
    this.update();
  }

  // Saves configuration and installs packages if needed
  async onSave() {
    try {
      await this._context.save();
      this._logger?.info({ Message: 'Saved package configurations' });

      // if checkbox & present configs
      if (this._updateSpace && this._config['Python']) {
        const { installPackagesFromConfig } = await import('./PackageInstaller');
        await installPackagesFromConfig(this._config, this._createTerminal, this._openTerminal, this._logger);
      }
    } catch (error) {
      this._logger?.error({
        Message: 'Error saving packing configurations',
        Error: error as Error,
      });
    }
  }

  // Initializes the editor with configuration data
  private async _initialize() {
    await this._context.ready;

    this._context.model.contentChanged.connect(this.onContentChange, this);
    this._config = this._context.model.toJSON() as ReadonlyJSONObject;
    this._updateSpace = (this._config['ApplyChangeToSpace'] as boolean) ?? false;
  }

  // Updates local config when document content changes
  private onContentChange() {
    this._config = this._context.model.toJSON() as ReadonlyJSONObject;
  }
}
