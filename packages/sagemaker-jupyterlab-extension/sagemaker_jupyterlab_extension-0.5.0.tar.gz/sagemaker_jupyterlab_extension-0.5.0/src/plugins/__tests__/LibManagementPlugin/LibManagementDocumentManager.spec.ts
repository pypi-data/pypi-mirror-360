import { initConfig } from '../../LibManagementPlugin/config';
import { LibManagementDocumentManager } from '../../LibManagementPlugin/LibraryDocument/LibManagementDocumentManager';

// Create a testable subclass that overrides _openOrReveal
class TestableLibManagementDocumentManager extends LibManagementDocumentManager {
  openOrRevealCalled = false;
  openOrRevealPath = '';
  openOrRevealWidgetName = '';

  protected async _openOrReveal(path: string, widgetName: string): Promise<any> {
    this.openOrRevealCalled = true;
    this.openOrRevealPath = path;
    this.openOrRevealWidgetName = widgetName;
    return Promise.resolve({});
  }
}

// Mock DocumentManager
jest.mock('@jupyterlab/docmanager', () => ({
  DocumentManager: class {
    services: any;
    registry: any;
    manager: any;
    opener: any;
    autosave = true;

    constructor(options: any) {
      this.services = options.services;
      this.registry = options.registry;
      this.manager = options.manager;
      this.opener = options.opener;
    }

    openOrReveal(path: string, widgetName: string) {
      return Promise.resolve({ path, widgetName });
    }
  },
}));

describe('LibManagementDocumentManager', () => {
  // Mock services
  const mockGet = jest.fn();
  const mockSave = jest.fn();
  let manager;

  beforeEach(() => {
    jest.clearAllMocks();

    // Create an instance with minimal options
    manager = new TestableLibManagementDocumentManager({
      registry: {},
      services: { contents: { get: mockGet, save: mockSave } },
      manager: {},
      opener: {},
    } as any);
  });

  it('should initialize with autosave disabled and handle exist method', async () => {
    // Check initialization
    expect(manager.autosave).toBe(false);

    // Test exist with file present
    mockGet.mockResolvedValue({});
    expect(await manager.exist('test.json')).toBe(true);
    expect(mockGet).toHaveBeenCalledWith('test.json');

    // Test exist with 404 error
    mockGet.mockRejectedValue({ response: { status: 404 } });
    expect(await manager.exist('missing.json')).toBe(false);

    // Test exist with other error
    const error = new Error('Network error');
    mockGet.mockRejectedValue(error);
    await expect(manager.exist('error.json')).rejects.toThrow('Network error');
  });

  it('should handle openOrCreate for existing and new files', async () => {
    // Test opening existing file
    mockGet.mockResolvedValue({});
    await manager.openOrCreate('existing.json', 'editor');
    expect(mockSave).not.toHaveBeenCalled();
    expect(manager.openOrRevealCalled).toBe(true);
    expect(manager.openOrRevealPath).toBe('existing.json');
    expect(manager.openOrRevealWidgetName).toBe('editor');

    // Reset for next test
    jest.clearAllMocks();
    manager.openOrRevealCalled = false;

    // Test creating new file
    mockGet.mockRejectedValue({ response: { status: 404 } });
    const fixedTimestamp = '2023-01-01T00:00:00Z';
    jest.spyOn(Date.prototype, 'toISOString').mockReturnValue(fixedTimestamp);

    await manager.openOrCreate('new.json', 'editor');
    expect(mockSave).toHaveBeenCalledWith(
      'new.json',
      expect.objectContaining({
        content: JSON.stringify(initConfig),
        path: 'new.json',
        created: fixedTimestamp,
        last_modified: fixedTimestamp,
      }),
    );
    expect(manager.openOrRevealCalled).toBe(true);

    // Test default widget name
    jest.clearAllMocks();
    manager.openOrRevealCalled = false;
    mockGet.mockResolvedValue({});

    await manager.openOrCreate('test.json');
    expect(manager.openOrRevealWidgetName).toBe('default');

    // Test error handling
    jest.clearAllMocks();
    const networkError = new Error('Network error');
    mockGet.mockRejectedValue(networkError);

    await expect(manager.openOrCreate('error.json')).rejects.toThrow('Network error');
    expect(mockSave).not.toHaveBeenCalled();

    jest.restoreAllMocks();
  });
});
