import { Button, LabIcon, ReactWidget, errorIcon } from '@jupyterlab/ui-components';
import { ISignal, Signal } from '@lumino/signaling';
import { JSONSchema7 } from 'json-schema';
import React, { ChangeEvent } from 'react';

import { CONFIGS } from './config';
import { ErrorText, styles } from './styles';

/**
 * Widget that displays the list of configurable library types
 * Provides navigation and selection UI for the library configuration
 */
export class LibraryConfigListWidget extends ReactWidget {
  private _selectedType = 'Python';
  private _selectedSource = 'CondaPackages';
  private _updateSpace: boolean;
  private _onCheckUpdateSpace: (updateSpace: boolean) => void;
  private _onSave: () => Promise<void>;
  private _schema: JSONSchema7;
  private _handleSelectTypeSignal = new Signal<this, string>(this);
  private _handleSelectSourceSignal = new Signal<this, string>(this);
  private _errors: { [type: string]: { [source: string]: boolean } };
  private _isSaving = false;

  constructor(options: LibraryConfigListWidgetOptions) {
    super();
    this.addClass('jp-PluginList');
    this._updateSpace = options.updateSpace;
    this._onCheckUpdateSpace = (updateSpace: boolean) => {
      this._updateSpace = updateSpace;
      options.onCheckUpdateSpace(updateSpace);
      this.update();
    };
    this._onSave = options.onSave;
    this._schema = options.schema;
    this._evtMousedown = this._evtMousedown.bind(this);
    this._onSave = this._onSave.bind(this);
    this.setError = this.setError.bind(this);
    this._errors = {};
  }

  // Signal emitted when a type is selected
  get handleSelectTypeSignal(): ISignal<this, string> {
    return this._handleSelectTypeSignal;
  }

  // Signal emitted when a source is selected
  get handleSelectSourceSignal(): ISignal<this, string> {
    return this._handleSelectSourceSignal;
  }

  // Creates a UI element for a configuration item
  mapConfig(type: string, source: string, schema: JSONSchema7): JSX.Element {
    const title = schema.title;
    const configMetadata = CONFIGS[type][source];
    return (
      <div
        onClick={this._evtMousedown}
        className={`${
          type === this._selectedType && source === this._selectedSource
            ? 'jp-mod-selected jp-PluginList-entry'
            : 'jp-PluginList-entry'
        } ${this.hasError(type, source) ? 'jp-ErrorPlugin' : ''}`}
        data-selected-type={type}
        data-selected-source={source}
      >
        <div className="jp-PluginList-entry-label" role="tab">
          <div className="jp-SelectedIndicator" />
          <LabIcon.resolveReact
            icon={configMetadata.icon}
            iconClass={'jp-Icon'}
            tag="span"
            stylesheet="settingsEditor"
          />
          <span className="jp-PluginList-entry-label-text">{title}</span>
        </div>
      </div>
    );
  }

  // Renders the configuration list UI
  protected render() {
    let configs: JSX.Element[] = [];
    if (this._schema.properties) {
      const properties = this._schema.properties;
      configs = Object.keys(properties).map((typeKey) => {
        const sourceConfig = (properties[typeKey] as JSONSchema7).properties;
        const sourceList = sourceConfig
          ? Object.keys(sourceConfig).map((sourceKey) =>
              this.mapConfig(typeKey, sourceKey, sourceConfig[sourceKey] as JSONSchema7),
            )
          : [];
        return (
          <div key={typeKey}>
            <h1 className="jp-PluginList-header">{typeKey}</h1>
            <ul>{sourceList}</ul>
          </div>
        );
      });
    }
    return (
      <div className="jp-PluginList-wrapper">
        <div className="jp-SettingsHeader">
          <h3>{'Environment Management'}</h3>
        </div>
        {configs}
        <div className="jp-PluginList-entry" style={styles.pluginListEntry}>
          <div className="jp-PluginList-entry">
            <div className="jp-PluginList-entry-label">
              <input
                type="checkbox"
                className="jp-mod-styled jp-pluginmanager-Disclaimer-checkbox"
                checked={this._updateSpace}
                onChange={(event: ChangeEvent<HTMLInputElement>) => this._onCheckUpdateSpace(event.target.checked)}
              />
              <span>Install in current session</span>
            </div>
          </div>
          <div className="jp-PluginList-entry">
            <Button
              className="jp-mod-styled jp-mod-reject jp-ArrayOperationsButton"
              disabled={this._isSaving || this.hasErrors}
              onClick={() => this.onSave()}
            >
              {this._isSaving ? 'Saving...' : 'Save all changes'}
            </Button>
          </div>
          {this.hasErrors && (
            <div className="jp-PluginList-entry">
              <div className="jp-PluginList-entry-label">
                <LabIcon.resolveReact icon={errorIcon} iconClass={'jp-Icon'} tag="span" stylesheet="settingsEditor" />
                <ErrorText>You must resolve all errors to save</ErrorText>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Handles selection of configuration items
  private _evtMousedown(event: React.MouseEvent<HTMLDivElement>): void {
    const target = event.currentTarget;
    const type = target.getAttribute('data-selected-type');
    const source = target.getAttribute('data-selected-source');

    if (!type || !source) {
      return;
    }

    this._selectedType = type;
    this._handleSelectTypeSignal.emit(type);
    this._selectedSource = source;
    this._handleSelectSourceSignal.emit(source);
    this.update();
  }

  // Saves configuration if no errors exist
  private async onSave(): Promise<void> {
    if (this.hasErrors || this._isSaving) {
      this.update();
      return;
    }
    this._isSaving = true;
    this.update(); // Re-render to disable save button
    try {
      await this._onSave();
    } finally {
      this._isSaving = false;
      this.update(); // Re-render to enable save button
    }
  }

  // Checks if a specific configuration has an error
  private hasError(type: string, source: string): boolean {
    return this._errors[type] ? this._errors[type][source] : false;
  }

  // Checks if any configuration has errors
  get hasErrors(): boolean {
    for (const type in this._errors) {
      for (const source in this._errors[type]) {
        if (this._errors[type][source]) {
          return true;
        }
      }
    }
    return false;
  }

  // Sets error state for a specific configuration
  setError(type: string, source: string, error: boolean) {
    if (!this._errors[type]) {
      this._errors[type] = {};
    }
    if (this._errors[type][source] !== error) {
      this._errors[type][source] = error;
      this.update();
    } else {
      this._errors[type][source] = error;
    }
  }
}

// Options for creating a LibraryConfigListWidget
export interface LibraryConfigListWidgetOptions {
  updateSpace: boolean;
  onCheckUpdateSpace: (updateSpace: boolean) => void;
  onSave: () => Promise<void>;
  schema: JSONSchema7;
}
