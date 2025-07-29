import * as LibManagementPluginExports from '../../LibManagementPlugin';

describe('LibManagementPlugin index', () => {
  it('should export LibManagementPlugin', () => {
    expect(LibManagementPluginExports.LibManagementPlugin).toBeDefined();
    expect(LibManagementPluginExports.CommandIDs).toBeDefined();
  });
});
