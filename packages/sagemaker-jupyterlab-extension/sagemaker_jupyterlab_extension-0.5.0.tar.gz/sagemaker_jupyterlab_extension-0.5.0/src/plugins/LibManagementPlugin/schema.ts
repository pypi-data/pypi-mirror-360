import { JSONSchema7 } from 'json-schema';

// Regex pattern for valid conda package and channel names
const VALID_NAME_PATTERN = '^[a-zA-Z0-9._:/=<>!~^*,|-]+$';

// JSON schema for conda package specifications
const CONDA_PACKAGE_SPECIFICATION_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: VALID_NAME_PATTERN,
};

// JSON schema for conda channels
const CONDA_CHANNEL_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: VALID_NAME_PATTERN,
};

/**
 * JSON schema for the entire library configuration file
 * Defines the structure and validation rules for .libs.json
 */
export const LIBRARY_CONFIG_SCHEMA: JSONSchema7 = {
  title: 'Library management configuration',
  description: 'Library management configuration',
  type: ['object', 'null'],
  properties: {
    Python: {
      type: 'object',
      title: 'Python',
      properties: {
        CondaPackages: {
          title: 'Conda Packages/Extensions',
          type: ['object', 'null'],
          properties: {
            Channels: {
              title: 'Package Channels',
              type: ['array', 'null'],
              items: CONDA_CHANNEL_SCHEMA,
            },
            PackageSpecs: {
              title: 'Package Specifications',
              type: ['array', 'null'],
              items: CONDA_PACKAGE_SPECIFICATION_SCHEMA,
            },
          },
        },
      },
    },
  },
};
