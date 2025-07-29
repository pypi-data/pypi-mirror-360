import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { GitCloneComponent } from '../components/GitCloneComponent';
import { GitCloneRepositoriesResponse } from './../constants/gitCloneConstants';
import { fetchApiResponse, OPTIONS_TYPE } from '../service';
import { GIT_REPOSITORIES_URL } from '../service/constants';
import { DropdownItem } from './../components/common/AutoComplete';

class GitCloneWidget extends ReactWidget {
  private _gitCloneRepositories: GitCloneRepositoriesResponse | null;
  private URL: string;
  private path: string;
  private openREADME: boolean;

  constructor() {
    super();
    this.URL = '';
    this.path = '';
    this.openREADME = true;
    this._gitCloneRepositories = null;
    this.getGitRepositories();
  }

  setGitURL = (value: string | DropdownItem | null) => {
    this.URL = value as string;
  };

  setPath = (value: string) => {
    this.path = value;
  };

  setOpenREADME = (value: boolean) => {
    this.openREADME = value;
  };

  /**
   * Function returns the the values required for the git clone to work as expected
   * when clone is clicked on the dialog
   * @returns URL, path and openREADME
   */
  getValue() {
    return {
      URL: this.URL,
      path: this.path,
      openREADME: this.openREADME,
    };
  }

  /**
   * Fetches and parses instance and kernel metrics
   */
  getGitRepositories = async () => {
    await fetchApiResponse(GIT_REPOSITORIES_URL, OPTIONS_TYPE.GET).then((result: any) => {
      result &&
        result.json().then((data: any) => {
          this._gitCloneRepositories = data ? (data as GitCloneRepositoriesResponse) : null;
          this.update();
        });
    });
  };

  render() {
    return (
      <GitCloneComponent
        gitRepositories={this._gitCloneRepositories}
        setGitURL={this.setGitURL}
        setPath={this.setPath}
        setOpenREADME={this.setOpenREADME}
      />
    );
  }
}

export { GitCloneWidget };
