import React from 'react';
import { CheckboxComponent } from './../common/CheckboxComponent';
import { render, fireEvent, cleanup } from '@testing-library/react';

describe('CheckboxComponent suite', () => {
  afterEach(cleanup);

  it('should test checkbox field and its onChange handler', async () => {
    const onChangeMock = jest.fn();
    const container = render(
      <CheckboxComponent
        data-testid="text-field-container"
        id={'path'}
        label={'OpenReadME'}
        handleChange={onChangeMock}
      />,
    );
    const checkBox = container.getByLabelText('OpenReadME') as HTMLInputElement;
    expect(checkBox.checked).toBe(true);
    fireEvent.click(checkBox);
    expect(checkBox.checked).toBe(false);
    expect(onChangeMock.mock.calls).toHaveLength(1);
  });
});
