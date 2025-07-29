import { LibraryDocumentWidget } from '../../LibManagementPlugin/LibraryDocument/LibraryDocumentWidget';
import { LibraryConfigEditor } from '../../LibManagementPlugin/LibraryConfigEditor';
import { libMgmtIcon } from '../../LibManagementPlugin/config';

// Mock dependencies
jest.mock('../../LibManagementPlugin/LibraryConfigEditor', () => ({
  LibraryConfigEditor: jest.fn().mockImplementation(() => ({
    id: 'mock-editor',
  })),
}));

jest.mock('../../LibManagementPlugin/config', () => ({
  libMgmtIcon: { name: 'mock-icon' },
}));

jest.mock('@jupyterlab/docregistry', () => ({
  DocumentWidget: class {
    title = { icon: null };
    content;
    context;
    constructor(options) {
      this.content = options.content;
      this.context = options.context;
    }
  },
}));

describe('LibraryDocumentWidget', () => {
  it('should initialize with correct content and icon', () => {
    // Create mock dependencies
    const mockContext = { path: 'test.json' };
    const mockCreateTerminal = jest.fn();
    const mockOpenTerminal = jest.fn();

    // Create the widget
    const widget = new LibraryDocumentWidget(mockContext as any, mockCreateTerminal, mockOpenTerminal, undefined);

    // Check that LibraryConfigEditor was created with correct parameters
    expect(LibraryConfigEditor).toHaveBeenCalledWith(mockContext, mockCreateTerminal, mockOpenTerminal, undefined);

    // Check that content was set
    expect(widget.content).toBeDefined();

    // Check that icon was set
    expect(widget.title.icon).toBe(libMgmtIcon);
  });
});
