import { LIBRARY_CONFIG_SCHEMA } from '../../LibManagementPlugin/schema';
import { JSONSchema7 } from 'json-schema';

describe('schema', () => {
  it('should have the correct schema structure', () => {
    // Check top-level schema structure
    expect(LIBRARY_CONFIG_SCHEMA).toBeDefined();
    expect(LIBRARY_CONFIG_SCHEMA.type).toEqual(['object', 'null']);
    expect(LIBRARY_CONFIG_SCHEMA.properties).toBeDefined();

    // Check Python property
    const pythonSchema = LIBRARY_CONFIG_SCHEMA.properties!.Python as JSONSchema7;
    expect(pythonSchema.type).toBe('object');
    expect(pythonSchema.properties).toBeDefined();

    // Check CondaPackages property
    const condaPackages = pythonSchema.properties!.CondaPackages as JSONSchema7;
    expect(condaPackages.type).toEqual(['object', 'null']);
    expect(condaPackages.properties).toBeDefined();

    // Check Channels and PackageSpecs
    const channels = condaPackages.properties!.Channels as JSONSchema7;
    const packageSpecs = condaPackages.properties!.PackageSpecs as JSONSchema7;

    // Verify Channels schema
    expect(channels.type).toEqual(['array', 'null']);
    expect((channels.items as JSONSchema7).type).toBe('string');
    expect((channels.items as JSONSchema7).pattern).toBeDefined();

    // Verify PackageSpecs schema
    expect(packageSpecs.type).toEqual(['array', 'null']);
    expect((packageSpecs.items as JSONSchema7).type).toBe('string');
    expect((packageSpecs.items as JSONSchema7).pattern).toBeDefined();
  });
});
