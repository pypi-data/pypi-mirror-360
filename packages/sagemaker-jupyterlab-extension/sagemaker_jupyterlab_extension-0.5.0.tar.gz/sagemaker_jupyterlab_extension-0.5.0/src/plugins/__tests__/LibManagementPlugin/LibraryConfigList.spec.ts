// Mock ReactWidget
jest.mock('@jupyterlab/apputils', () => {
  return {
    ReactWidget: class MockReactWidget {
      node = document.createElement('div');
      addClass = jest.fn();
      update = jest.fn();
    },
  };
});

// Mock Signal
jest.mock('@lumino/signaling', () => ({
  Signal: class MockSignal {
    connect = jest.fn();
    disconnect = jest.fn();
    emit = jest.fn();
  },
}));

// Mock config
jest.mock('../../LibManagementPlugin/config', () => ({
  CONFIGS: {
    Python: {
      CondaPackages: {
        icon: {},
        title: 'Conda Packages',
      },
    },
  },
}));

// Import after mocking
import { LibraryConfigListWidget } from '../../LibManagementPlugin/LibraryConfigList';
import { JSONSchema7 } from 'json-schema';

describe('LibraryConfigListWidget', () => {
  let widget;
  const mockOnCheckUpdateSpace = jest.fn();
  const mockOnSave = jest.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    jest.clearAllMocks();

    // Create a minimal instance with just enough props
    widget = new LibraryConfigListWidget({
      schema: { properties: {} } as JSONSchema7,
      updateSpace: false,
      onCheckUpdateSpace: mockOnCheckUpdateSpace,
      onSave: mockOnSave,
    });

    // Spy on the update method after widget creation
    jest.spyOn(widget, 'update');
  });

  it('should initialize with correct properties and handle errors', () => {
    // Check initialization
    expect(widget['_selectedType']).toBe('Python');
    expect(widget['_selectedSource']).toBe('CondaPackages');
    expect(widget['_updateSpace']).toBe(false);
    expect(widget.handleSelectTypeSignal).toBe(widget['_handleSelectTypeSignal']);
    expect(widget.handleSelectSourceSignal).toBe(widget['_handleSelectSourceSignal']);

    // Test error handling
    expect(widget.hasErrors).toBe(false);
    widget.setError('Python', 'CondaPackages', true);
    expect(widget.hasError('Python', 'CondaPackages')).toBe(true);
    expect(widget.hasErrors).toBe(true);

    // Test unchanged error state
    jest.clearAllMocks();
    widget.setError('Python', 'CondaPackages', true);
    expect(widget.update).not.toHaveBeenCalled();
  });

  it('should handle events and callbacks', async () => {
    // Test onSave without errors
    await widget.onSave();
    expect(mockOnSave).toHaveBeenCalled();

    // Test onSave with errors
    mockOnSave.mockClear();
    widget.setError('Python', 'CondaPackages', true);
    await widget.onSave();
    expect(mockOnSave).not.toHaveBeenCalled();

    // Test _onCheckUpdateSpace
    widget['_onCheckUpdateSpace'](true);
    expect(widget['_updateSpace']).toBe(true);
    expect(mockOnCheckUpdateSpace).toHaveBeenCalledWith(true);
    expect(widget.update).toHaveBeenCalled();
  });

  it('should handle mouse events and config mapping', () => {
    // Test _evtMousedown with valid attributes
    const mockEvent = {
      currentTarget: {
        getAttribute: (attr) => {
          if (attr === 'data-selected-type') return 'Python';
          if (attr === 'data-selected-source') return 'CondaPackages';
          return null;
        },
      },
    };

    widget['_evtMousedown'](mockEvent);
    expect(widget['_handleSelectTypeSignal'].emit).toHaveBeenCalledWith('Python');
    expect(widget['_handleSelectSourceSignal'].emit).toHaveBeenCalledWith('CondaPackages');

    // Test _evtMousedown with missing attributes
    jest.clearAllMocks();
    widget['_evtMousedown']({ currentTarget: { getAttribute: () => null } });
    expect(widget['_handleSelectTypeSignal'].emit).not.toHaveBeenCalled();

    // Test mapConfig
    const result = widget.mapConfig('Python', 'CondaPackages', { title: 'Test Title' } as JSONSchema7);
    expect(result.props['data-selected-type']).toBe('Python');
    expect(result.props.className).toContain('jp-PluginList-entry');
  });
});
