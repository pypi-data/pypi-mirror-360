import React, { FC, useEffect, useState } from 'react';
import { InputField } from './../components/common/InputField';
import * as styles from './../widgets/styles/gitCloneStyles';
import { GitCloneRepositoriesResponse } from '../constants/gitCloneConstants';
import { AutoComplete, DropdownItem } from './common/AutoComplete';
import { CheckboxComponent } from './common/CheckboxComponent';
import { il18Strings } from './../constants/il18Strings';

type Repo = { value: string; label: string };

const PATH_REGEX = '^([A-Za-z]*|[0-9]*|[/]*|[.]*|[A-Za-z0-9/.]*)$';
interface GitCloneComponentProps {
  gitRepositories: GitCloneRepositoriesResponse | null;
  setGitURL: (value: string | DropdownItem | null) => void;
  setPath: (value: string) => void;
  setOpenREADME: (value: boolean) => void;
}

const GitCloneComponent: FC<GitCloneComponentProps> = ({ gitRepositories, setGitURL, setPath, setOpenREADME }) => {
  const [pathValue, setPathValue] = useState<string>('');
  const [selectedRepo, setSelectedRepo] = useState<DropdownItem | string | null>('');
  const [openREADMEValue, setOpenREADMEValue] = useState<boolean>(true);
  const [repositories, setRepositories] = useState<Repo[]>([]);

  const { repoTitle, pathTitle, openReadMeFilesLabel } = il18Strings.GitClone;
  const handleChange = (value: string) => {
    setPathValue(value);
    setPath(value);
  };

  const handleRepoSelected = (item: string | DropdownItem | null) => {
    setSelectedRepo(item);
    setGitURL(item);
  };

  const handleOpenREADMEChange = (value: boolean) => {
    setOpenREADMEValue(value);
    setOpenREADME(value);
  };

  useEffect(() => {
    if (gitRepositories && gitRepositories.GitCodeRepositories.length >= 0) {
      const repos: Repo[] = [];
      gitRepositories.GitCodeRepositories.length > 0 &&
        gitRepositories.GitCodeRepositories.forEach((repo) => repos.push({ value: repo, label: repo }));
      setRepositories(repos);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gitRepositories]);

  return (
    <div
      className={styles.gitCloneContainer}
      data-testid={'git-clone-container'}
      data-analytics-type="eventContext"
      data-analytics="JupyterLab"
    >
      <AutoComplete
        data-testid="autocomplete-field-container"
        data-analytics-type="eventDetail"
        data-analytics="GitClone-Repo-AutoComplete"
        label={repoTitle}
        options={repositories}
        value={selectedRepo}
        handleChange={handleRepoSelected}
        freeSolo={true}
      />
      <InputField
        data-testid="text-field-container"
        data-analytics-type="eventDetail"
        data-analytics="GitClone-Path-TextField"
        error={false}
        id={'path'}
        label={pathTitle}
        helperText={''}
        valuePassed={pathValue}
        handleChange={handleChange}
        regEx={PATH_REGEX}
      />
      <CheckboxComponent
        data-testid="read-me-field"
        data-analytics-type="eventDetail"
        data-analytics="GitClone-OpenReadMeCheckbox"
        label={openReadMeFilesLabel}
        id={'openReadMe'}
        handleChange={handleOpenREADMEChange}
        checked={openREADMEValue}
      />
    </div>
  );
};

export { GitCloneComponent };
