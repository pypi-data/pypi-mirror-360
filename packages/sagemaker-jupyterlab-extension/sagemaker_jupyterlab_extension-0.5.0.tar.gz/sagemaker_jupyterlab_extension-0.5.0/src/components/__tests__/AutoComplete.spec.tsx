import React from 'react';
import { AutoComplete } from './../common/AutoComplete';
import { screen, render, fireEvent, cleanup } from '@testing-library/react';

describe('AutoComplete Test suite', () => {
  afterEach(cleanup);

  it('should render the dropdown options', () => {
    const onChangeMock = jest.fn();
    const reposMock = [
      { label: 'repo1', value: 'repo1' },
      { label: 'repo2', value: 'repo2' },
      { label: 'repo3', value: 'repo3' },
    ];
    const loadingMock = false;
    render(
      <AutoComplete
        data-testid="autocomplete-field-container"
        label={'Git repositories'}
        disabled={loadingMock}
        options={reposMock}
        value={''}
        handleChange={onChangeMock}
        freeSolo={true}
      />,
    );
    const autoComplete = screen.getByRole('combobox');
    fireEvent.input(autoComplete, { target: { value: 'repo' } });
    expect(screen.getAllByRole('option').length).toBe(3);
  });

  it('should select a single option', () => {
    const onChangeMock = jest.fn();
    const reposMock = [
      { label: 'repo1', value: 'repo1' },
      { label: 'repo2', value: 'repo2' },
      { label: 'repo3', value: 'repo3' },
    ];
    const loadingMock = false;
    render(
      <AutoComplete
        data-testid="autocomplete-field-container"
        label={'Git repositories'}
        disabled={loadingMock}
        options={reposMock}
        value={''}
        handleChange={onChangeMock}
        freeSolo={true}
      />,
    );
    const autoComplete = screen.getByRole('combobox');
    fireEvent.input(autoComplete, { target: { value: 'repo1' } });
    expect(screen.getAllByRole('option').length).toBe(1);
    fireEvent.keyDown(autoComplete, { key: 'Enter' });
    expect(autoComplete.value).toBe('repo1');
  });
});
