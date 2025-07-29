import { CONFIGS, initConfig, ERROR_MESSAGES } from '../../LibManagementPlugin/config';
import { render } from '@testing-library/react';

// Test config
describe('config', () => {
  it('should have Python configuration', () => {
    expect(CONFIGS).toHaveProperty('Python');
    expect(CONFIGS.Python).toHaveProperty('CondaPackages');
  });

  it('should have the correct initial structure', () => {
    expect(initConfig).toEqual({
      ApplyChangeToSpace: false,
      Python: {
        CondaPackages: {
          Channels: [],
          PackageSpecs: [],
        },
      },
    });
  });

  it('should have ERROR_MESSAGES defined', () => {
    expect(ERROR_MESSAGES).toBeDefined();
    expect(ERROR_MESSAGES).toHaveProperty('CORRUPTED_CONFIG_FILE');
    expect(typeof ERROR_MESSAGES.CORRUPTED_CONFIG_FILE).toBe('function');
  });

  it('should render CORRUPTED_CONFIG_FILE message correctly', () => {
    const testPath = '/test/path.json';
    const { container } = render(ERROR_MESSAGES.CORRUPTED_CONFIG_FILE(testPath));

    const errorMessage = container.textContent;
    expect(errorMessage).toContain('The configuration file /test/path.json is corrupted or invalid');
    expect(errorMessage).toContain('To resolve this issue:');
    expect(errorMessage).toContain('Remove the corrupted file and restart the UI');
    expect(errorMessage).toContain('Fix the file format back to how it was originally');
  });
});
