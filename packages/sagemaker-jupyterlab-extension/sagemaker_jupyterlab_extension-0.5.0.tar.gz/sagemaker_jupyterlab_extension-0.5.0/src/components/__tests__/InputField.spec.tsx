import React from 'react';
import { InputField } from './../common/InputField';
import { render, fireEvent, cleanup } from '@testing-library/react';

describe('InputField suite', () => {
  afterEach(cleanup);

  it('should test input field and its onChange handler', async () => {
    const onChangeMock = jest.fn();
    const pathValue = 'test';
    const container = render(
      <InputField
        data-testid="text-field-container"
        error={false}
        id={'path'}
        label={'Project'}
        valuePassed={pathValue}
        helperText={''}
        handleChange={onChangeMock}
      />,
    );
    const input = container.getByLabelText('Project') as HTMLInputElement;
    expect(input.value).toBe('');
    fireEvent.change(input, { target: { value: '42' } });
    expect(input.value).toBe('42');
    expect(onChangeMock.mock.calls).toHaveLength(1);
  });
});
