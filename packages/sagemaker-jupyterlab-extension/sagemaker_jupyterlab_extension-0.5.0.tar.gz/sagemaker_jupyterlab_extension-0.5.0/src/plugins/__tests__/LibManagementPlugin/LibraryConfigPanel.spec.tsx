import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LibraryConfigPanelWidget } from '../../LibManagementPlugin/LibraryConfigPanel';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { JSONSchema7 } from 'json-schema';
import { LibraryConfigListWidget } from '../../LibManagementPlugin/LibraryConfigList';

// Mock dependencies
jest.mock('../../LibManagementPlugin/LibraryConfigForm', () => ({
  LibraryConfigFormWidget: ({ schema, config, onChange, hasError, selectedType, selectedSource }) => (
    <div data-testid="mock-form-widget">
      <div data-testid="selected-type">{selectedType}</div>
      <div data-testid="selected-source">{selectedSource}</div>
      <button data-testid="change-config-button" onClick={() => onChange({ updated: true })}>
        Change Config
      </button>
      <button data-testid="set-error-button" onClick={() => hasError(true)}>
        Set Error
      </button>
    </div>
  ),
}));

describe('LibraryConfigPanelWidget', () => {
  // Create mock signals
  const mockSelectTypeSignal = {
    connect: jest.fn(),
    disconnect: jest.fn(),
    emit: jest.fn(),
  };

  const mockSelectSourceSignal = {
    connect: jest.fn(),
    disconnect: jest.fn(),
    emit: jest.fn(),
  };

  const mockOnConfigsChange = jest.fn();
  const mockSetError = jest.fn();

  // Common props for tests
  const baseProps = {
    schema: {
      properties: {
        Python: {
          properties: {
            CondaPackages: { type: 'object' },
            NewSource: { type: 'object' },
          },
        },
        NewType: {
          properties: {
            NewSource: { type: 'object' },
          },
        },
      },
    } as JSONSchema7,
    configs: {
      Python: {
        CondaPackages: { test: 'value' },
        NewSource: {},
      },
      NewType: {
        NewSource: {},
      },
    } as ReadonlyJSONObject,
    handleSelectTypeSignal: mockSelectTypeSignal as any,
    handleSelectSourceSignal: mockSelectSourceSignal as any,
    onConfigsChange: mockOnConfigsChange,
    setError: mockSetError,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render with default selected type/source and handle signal connections', () => {
    const { unmount } = render(<LibraryConfigPanelWidget {...baseProps} />);

    // Check initial render
    expect(screen.getByTestId('selected-type')).toHaveTextContent('Python');
    expect(screen.getByTestId('selected-source')).toHaveTextContent('CondaPackages');
    expect(mockSelectTypeSignal.connect).toHaveBeenCalled();
    expect(mockSelectSourceSignal.connect).toHaveBeenCalled();

    // Test signal disconnection on unmount
    unmount();
    expect(mockSelectTypeSignal.disconnect).toHaveBeenCalled();
    expect(mockSelectSourceSignal.disconnect).toHaveBeenCalled();
  });

  it('should update selected type and source when signals emit', () => {
    render(<LibraryConfigPanelWidget {...baseProps} />);

    // Get signal handlers
    const typeHandler = mockSelectTypeSignal.connect.mock.calls[0][0];
    const sourceHandler = mockSelectSourceSignal.connect.mock.calls[0][0];

    // Test type/source updates
    act(() => {
      typeHandler({} as LibraryConfigListWidget, 'NewType');
      sourceHandler({} as LibraryConfigListWidget, 'NewSource');
    });
    expect(screen.getByTestId('selected-type')).toHaveTextContent('NewType');
    expect(screen.getByTestId('selected-source')).toHaveTextContent('NewSource');

    // Test empty type (edge case)
    act(() => {
      typeHandler({} as LibraryConfigListWidget, '');
    });
    expect(screen.getByTestId('mock-form-widget')).toBeInTheDocument();
  });

  it('should handle config changes and errors', () => {
    // Use simpler props for this test
    const simpleProps = {
      ...baseProps,
      configs: {
        Python: {
          CondaPackages: { original: true },
        },
      } as ReadonlyJSONObject,
    };

    render(<LibraryConfigPanelWidget {...simpleProps} />);

    // Test config change
    fireEvent.click(screen.getByTestId('change-config-button'));
    expect(mockOnConfigsChange).toHaveBeenCalledWith({
      Python: {
        CondaPackages: { updated: true },
      },
    });

    // Test error handling
    fireEvent.click(screen.getByTestId('set-error-button'));
    expect(mockSetError).toHaveBeenCalledWith('Python', 'CondaPackages', true);
  });
});
