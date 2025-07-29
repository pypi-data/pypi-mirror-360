import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { GitCloneComponent } from './../GitCloneComponent';
import { il18Strings } from './../../constants/il18Strings';
import { gitCloneRepoMock } from '../../service/__tests__/mock';

const { repoTitle, pathTitle } = il18Strings.GitClone;

describe('GitClonecomponent test suite', () => {
  beforeAll(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });
  const setGitURLMock = jest.fn();
  const setPathMock = jest.fn();
  const setOpenREADMEMock = jest.fn();

  it('should render the component with repos being null', async () => {
    const mockRepos = null;
    const container = render(
      <GitCloneComponent
        gitRepositories={mockRepos}
        setGitURL={setGitURLMock}
        setPath={setPathMock}
        setOpenREADME={setOpenREADMEMock}
      />,
    );

    await screen.findByText(repoTitle);
    expect(screen.getByRole('combobox').value).toEqual('');
    const input = container.getByLabelText(pathTitle) as HTMLInputElement;
    expect(input.value).toBe('');
  });

  it('should render the component with repos more than 1', async () => {
    const mockRepos = gitCloneRepoMock;
    const container = render(
      <GitCloneComponent
        gitRepositories={mockRepos}
        setGitURL={setGitURLMock}
        setPath={setPathMock}
        setOpenREADME={setOpenREADMEMock}
      />,
    );
    jest.useFakeTimers();
    await screen.findByText(repoTitle);
    jest.runAllTimers();
    expect(screen.getByRole('combobox').value).toEqual('');
    const input = container.getByLabelText(pathTitle) as HTMLInputElement;
    expect(input.value).toBe('');
    fireEvent.change(input, { target: { value: '42' } });
    expect(input.value).toBe('42');

    const autoComplete = screen.getByRole('combobox');
    fireEvent.input(autoComplete, { target: { value: 'repo' } });
  });
});
