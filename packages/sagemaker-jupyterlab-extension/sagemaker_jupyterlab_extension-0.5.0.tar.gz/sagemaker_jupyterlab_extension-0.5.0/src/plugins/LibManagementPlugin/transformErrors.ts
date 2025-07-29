import { ErrorTransformer } from '@rjsf/utils';

/**
 * Custom error transformer function to simplify validation error messages
 * Makes error messages more user-friendly in the UI
 *
 * @param errors - Array of validation errors from the form
 * @returns Transformed array of errors with simplified messages
 */
const transformErrors: ErrorTransformer = (errors) => {
  return errors.map((error) => {
    // Replace pattern validation error messages with a simple message
    if (error.name === 'pattern') {
      return {
        ...error,
        message: 'Invalid input',
      };
    }
    return error;
  });
};

export default transformErrors;
