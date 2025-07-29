// Mock dependencies for LibraryDocumentWidget
jest.mock('../../LibManagementPlugin/LibraryDocument/LibraryDocumentWidget', () => {
  return {
    LibraryDocumentWidget: jest.fn().mockImplementation(() => ({})),
  };
});

import { LibraryEditorFactory } from '../../LibManagementPlugin/LibraryDocument/LibraryEditorFactory';
import { LibraryDocumentWidget } from '../../LibManagementPlugin/LibraryDocument/LibraryDocumentWidget';

// Test LibraryEditorFactory
describe('LibraryEditorFactory', () => {
  const mockCreateTerminal = jest.fn();
  const mockOpenTerminal = jest.fn();
  let factory: LibraryEditorFactory;

  beforeEach(() => {
    jest.clearAllMocks();

    factory = new LibraryEditorFactory(
      {
        name: 'test-factory',
        fileTypes: ['json'],
        defaultFor: [],
      },
      mockCreateTerminal,
      mockOpenTerminal,
      undefined,
    );
  });

  it('should create a new widget with the correct parameters', () => {
    const mockContext = { path: 'test.json' };

    // Access the protected method using type assertion
    (factory as any).createNewWidget(mockContext);

    expect(LibraryDocumentWidget).toHaveBeenCalledWith(mockContext, mockCreateTerminal, mockOpenTerminal, undefined);
  });
});
