// Mock UI components before importing LibraryConfigEditor
jest.mock('@jupyterlab/ui-components', () => ({
  LabIcon: class {
    name: string;
    svgstr: string;
    constructor(options: { name: string; svgstr: string }) {
      this.name = options.name;
      this.svgstr = options.svgstr;
    }
    static resolveReact = jest.fn(() => 'mock-icon');
  },
  UseSignal: jest.fn(({ children }) => children()),
  errorIcon: {},
}));

// Mock config before importing LibraryConfigEditor
jest.mock('../../LibManagementPlugin/config', () => ({
  libMgmtIcon: { name: 'mock-icon' },
  CONFIGS: {
    Python: {
      CondaPackages: {
        title: 'Python - Conda Packages/Extensions',
        additionalDescription: [],
      },
    },
  },
}));

// Mock PackageInstaller
jest.mock('../../LibManagementPlugin/PackageInstaller', () => ({
  installPackagesFromConfig: jest.fn().mockResolvedValue(undefined),
}));

// Now import the class and dependencies
import { LibraryConfigEditor } from '../../LibManagementPlugin/LibraryConfigEditor';
import { installPackagesFromConfig } from '../../LibManagementPlugin/PackageInstaller';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';

// Mock SplitPanel
jest.mock('@lumino/widgets', () => ({
  SplitPanel: class {
    addClass = jest.fn();
    addWidget = jest.fn();
    update = jest.fn();
  },
}));

// Mock other dependencies
jest.mock('@jupyterlab/apputils', () => ({
  ReactWidget: {
    create: jest.fn(() => ({})),
  },
}));

jest.mock('../../LibManagementPlugin/LibraryConfigList', () => ({
  LibraryConfigListWidget: jest.fn().mockImplementation(() => ({
    handleSelectSourceSignal: {
      connect: jest.fn(),
    },
    handleSelectTypeSignal: {},
    setError: jest.fn(),
  })),
}));

jest.mock('../../LibManagementPlugin/schema', () => ({
  LIBRARY_CONFIG_SCHEMA: {},
}));

describe('LibraryConfigEditor', () => {
  let editor;
  let mockContext;
  const mockCreateTerminal = jest.fn();
  const mockOpenTerminal = jest.fn();
  const mockLogger = { info: jest.fn(), error: jest.fn(), debug: jest.fn() } as unknown as ILogger;

  beforeEach(() => {
    jest.clearAllMocks();

    // Create a mock context
    mockContext = {
      ready: Promise.resolve(),
      path: 'test.json',
      model: {
        contentChanged: {
          connect: jest.fn(),
        },
        toJSON: jest.fn().mockReturnValue({
          ApplyChangeToSpace: false,
        }),
        fromJSON: jest.fn(),
      },
      save: jest.fn().mockResolvedValue(undefined),
    };

    // Create a LibraryConfigEditor instance
    editor = new LibraryConfigEditor(mockContext, mockCreateTerminal, mockOpenTerminal, mockLogger);

    // Set up initial state
    editor['_config'] = {};
  });

  describe('onCheckUpdateSpace', () => {
    it('should update _updateSpace and model', () => {
      // Call onCheckUpdateSpace with true
      editor.onCheckUpdateSpace(true);

      // Check that _updateSpace was updated
      expect(editor['_updateSpace']).toBe(true);

      // Check that model.fromJSON was called with updated config
      expect(mockContext.model.fromJSON).toHaveBeenCalledWith({
        ApplyChangeToSpace: true,
      });
    });
  });

  describe('onChange', () => {
    it('should update model and _config', () => {
      const newConfigs = { test: 'value', nested: { prop: 'value' } };

      // Call onChange with new configs
      editor.onChange(newConfigs);

      // Check that model.fromJSON was called with new configs
      expect(mockContext.model.fromJSON).toHaveBeenCalledWith(newConfigs);

      // Check that _config was updated
      expect(editor['_config']).toBe(newConfigs);

      // Check that update was called
      expect(editor.update).toHaveBeenCalled();
    });
  });

  describe('onSave', () => {
    it('should save context', async () => {
      // Call onSave
      await editor.onSave();

      // Check that context.save was called
      expect(mockContext.save).toHaveBeenCalled();
    });

    it('should not install packages when _updateSpace is false', async () => {
      // Set _updateSpace to false
      editor['_updateSpace'] = false;
      editor['_config'] = { Python: { CondaPackages: { PackageSpecs: ['numpy'] } } };

      // Call onSave
      await editor.onSave();

      // Check that installPackagesFromConfig was not called
      expect(installPackagesFromConfig).not.toHaveBeenCalled();
    });

    it('should install packages when _updateSpace is true and Python config exists', async () => {
      // Set _updateSpace to true and add Python config
      editor['_updateSpace'] = true;
      editor['_config'] = { Python: { CondaPackages: { PackageSpecs: ['numpy'] } } };

      // Call onSave
      await editor.onSave();

      // Check that installPackagesFromConfig was called with correct parameters
      expect(installPackagesFromConfig).toHaveBeenCalledWith(
        editor['_config'],
        mockCreateTerminal,
        mockOpenTerminal,
        mockLogger,
      );
    });
  });
});
