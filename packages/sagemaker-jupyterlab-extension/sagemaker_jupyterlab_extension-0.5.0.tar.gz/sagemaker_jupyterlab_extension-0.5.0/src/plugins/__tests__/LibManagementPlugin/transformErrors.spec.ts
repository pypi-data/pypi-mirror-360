import transformErrors from '../../LibManagementPlugin/transformErrors';

// Define a simple interface that matches the structure of errors used by the transformer
interface ErrorLike {
  name: string;
  property: string;
  message: string;
  schemaPath: string;
  stack: string;
  params: Record<string, any>;
}

describe('transformErrors', () => {
  it('should replace pattern error messages with "Invalid input"', () => {
    // Create a mock error object for pattern validation
    const patternError: ErrorLike = {
      name: 'pattern',
      property: '.test',
      message: 'must match pattern "^[a-zA-Z0-9._:/=<>!~^*,|-]+$"',
      schemaPath: '#/pattern',
      stack: '.test must match pattern "^[a-zA-Z0-9._:/=<>!~^*,|-]+$"',
      params: { pattern: '^[a-zA-Z0-9._:/=<>!~^*,|-]+$' },
    };

    // Create another error that should not be modified
    const otherError: ErrorLike = {
      name: 'required',
      property: '.test',
      message: 'is a required property',
      schemaPath: '#/required',
      stack: '.test is a required property',
      params: { missingProperty: 'test' },
    };

    // Run the transformer on an array with both errors
    const result = transformErrors([patternError, otherError]);

    // Check that the pattern error message was replaced
    expect(result[0].message).toBe('Invalid input');

    // Check that the other error message was not modified
    expect(result[1].message).toBe('is a required property');

    // Check that other properties of the pattern error were preserved
    expect(result[0].name).toBe('pattern');
    expect(result[0].property).toBe('.test');
    expect(result[0].schemaPath).toBe('#/pattern');
  });

  it('should return unmodified errors for non-pattern errors', () => {
    // Create a non-pattern error
    const typeError: ErrorLike = {
      name: 'type',
      property: '.test',
      message: 'should be string',
      schemaPath: '#/type',
      stack: '.test should be string',
      params: { type: 'string' },
    };

    // Run the transformer
    const result = transformErrors([typeError]);

    // Check that the error was not modified
    expect(result[0]).toEqual(typeError);
  });

  it('should handle empty error array', () => {
    // Run the transformer with an empty array
    const result = transformErrors([]);

    // Check that an empty array is returned
    expect(result).toEqual([]);
  });
});
