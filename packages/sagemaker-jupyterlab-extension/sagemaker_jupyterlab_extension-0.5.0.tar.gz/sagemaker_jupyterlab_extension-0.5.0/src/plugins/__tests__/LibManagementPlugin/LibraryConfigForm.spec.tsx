import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LibraryConfigFormWidget } from '../../LibManagementPlugin/LibraryConfigForm';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { JSONSchema7 } from 'json-schema';

// Mock dependencies
jest.mock('@jupyterlab/ui-components', () => ({
  FormComponent: ({ onChange }) => (
    <div data-testid="mock-form-component">
      <button onClick={() => onChange({ formData: { test: 'value' }, errors: [] })}>Submit No Errors</button>
      <button onClick={() => onChange({ formData: { test: 'error' }, errors: ['error'] })}>Submit With Errors</button>
    </div>
  ),
}));

jest.mock('@jupyterlab/translation', () => ({
  nullTranslator: {},
}));

jest.mock('@rjsf/validator-ajv8', () => ({}));

// Mock the config import
jest.mock('../../LibManagementPlugin/config', () => ({
  CONFIGS: {
    Python: {
      CondaPackages: {
        title: 'Python - Conda Packages/Extensions',
        additionalDescription: [<div key="test-desc">Test Description</div>],
      },
    },
  },
}));

describe('LibraryConfigFormWidget', () => {
  const mockOnChange = jest.fn();
  const mockHasError = jest.fn();
  let configModule;

  // Common props used in multiple tests
  const baseProps = {
    schema: { type: 'string' } as JSONSchema7,
    config: {} as ReadonlyJSONObject,
    onChange: mockOnChange,
    hasError: mockHasError,
    selectedType: 'Python',
    selectedSource: 'CondaPackages',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Import the mocked module
    configModule = jest.requireMock('../../LibManagementPlugin/config');
  });

  it('should render with title and description', () => {
    render(<LibraryConfigFormWidget {...baseProps} />);

    // Check that the title and description are rendered
    expect(screen.getByText('Python - Conda Packages/Extensions')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByTestId('mock-form-component')).toBeInTheDocument();
  });

  it('should render FormComponent for object schema', () => {
    const objectProps = {
      ...baseProps,
      schema: {
        type: ['object'],
        properties: {
          prop1: { type: 'string' },
          prop2: { type: 'number' },
        },
      } as JSONSchema7,
    };

    render(<LibraryConfigFormWidget {...objectProps} />);

    // For object schema, we should have multiple form components
    const formComponents = screen.getAllByTestId('mock-form-component');
    expect(formComponents.length).toBeGreaterThan(1);
  });

  it('should handle form changes with and without errors', () => {
    render(<LibraryConfigFormWidget {...baseProps} />);

    // Test form change without errors
    fireEvent.click(screen.getByText('Submit No Errors'));
    expect(mockHasError).toHaveBeenCalledWith(false);
    expect(mockOnChange).toHaveBeenCalledWith({ test: 'value' });

    // Clear mocks
    jest.clearAllMocks();

    // Test form change with errors
    fireEvent.click(screen.getByText('Submit With Errors'));
    expect(mockHasError).toHaveBeenCalledWith(true);
    expect(mockOnChange).toHaveBeenCalledWith({ test: 'error' });
  });

  it('should handle additionalDescription edge cases', () => {
    // Save original config
    const originalConfig = { ...configModule.CONFIGS };

    // Test with empty additionalDescription
    configModule.CONFIGS = {
      Python: {
        CondaPackages: {
          ...originalConfig.Python.CondaPackages,
          additionalDescription: [],
        },
      },
    };

    render(<LibraryConfigFormWidget {...baseProps} />);
    expect(screen.queryByText('Test Description')).not.toBeInTheDocument();

    // Test with undefined additionalDescription
    configModule.CONFIGS = {
      Python: {
        CondaPackages: {
          ...originalConfig.Python.CondaPackages,
          additionalDescription: undefined,
        },
      },
    };

    render(<LibraryConfigFormWidget {...baseProps} />);
    expect(screen.queryByText('Test Description')).not.toBeInTheDocument();

    // Restore original CONFIGS
    configModule.CONFIGS = originalConfig;
  });
});
