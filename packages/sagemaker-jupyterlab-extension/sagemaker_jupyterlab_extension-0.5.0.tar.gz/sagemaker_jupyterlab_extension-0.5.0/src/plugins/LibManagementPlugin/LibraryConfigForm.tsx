import { nullTranslator } from '@jupyterlab/translation';
import { FormComponent } from '@jupyterlab/ui-components';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { IChangeEvent } from '@rjsf/core';
import validatorAjv8 from '@rjsf/validator-ajv8';
import { ValidatorType } from '@rjsf/utils';
import { JSONSchema7, JSONSchema7Definition } from 'json-schema';
import React, { useEffect, useMemo, useRef, useState } from 'react';

import { CONFIGS } from './config';
import transformErrors from './transformErrors';

/**
 * Form widget for configuring library settings
 * Renders JSON schema based forms for package configuration
 */
export const LibraryConfigFormWidget: React.FC<LibraryConfigFormWidgetProps> = ({
  schema,
  config,
  onChange,
  hasError,
  selectedType,
  selectedSource,
}: LibraryConfigFormWidgetProps): JSX.Element => {
  // Handles form changes and validates input
  const _onChange: (e: IChangeEvent<ReadonlyJSONObject>) => void = (e) => {
    hasError(e.errors.length !== 0);
    onChange(e.formData as ReadonlyJSONObject);
  };

  // Retrieves additional description for the selected configuration
  const getDescription: () => JSX.Element = () => {
    const configMetadata = CONFIGS[selectedType][selectedSource];
    return (
      <div className="jp-SettingsHeader-description">
        {configMetadata.additionalDescription && configMetadata.additionalDescription.length > 0 && (
          <div>{configMetadata.additionalDescription}</div>
        )}
      </div>
    );
  };

  // Creates the appropriate form based on schema type
  function createForm() {
    if (Array.isArray(schema.type) && schema.type.includes('object') && schema.properties) {
      return <MultiForm properties={schema.properties} config={config} onChange={onChange} hasError={hasError} />;
    } else {
      return (
        <FormComponent
          schema={schema}
          validator={validatorAjv8 as ValidatorType}
          formData={config}
          onChange={_onChange}
          liveValidate
          tagName="div"
          translator={nullTranslator}
          showErrorList={false}
          transformErrors={transformErrors}
        />
      );
    }
  }

  return (
    <>
      <div className="jp-SettingsHeader">
        <h2 className="jp-SettingsHeader-title">{CONFIGS[selectedType][selectedSource].title}</h2>
        {getDescription()}
      </div>
      {createForm()}
    </>
  );
};

/**
 * Component for handling multiple form sections
 * Used when schema contains multiple property groups
 */
const MultiForm: React.FC<MultiFormProps> = ({
  properties,
  config,
  onChange,
  hasError,
}: MultiFormProps): JSX.Element => {
  const [localConfig, setLocalConfig] = useState<ReadonlyJSONObject>(config ?? {});
  const [errors, setErrors] = useState<{ [key: string]: boolean }>({});
  const isMountingRef = useRef(false);

  useEffect(() => {
    isMountingRef.current = true;
  }, []);

  useEffect(() => {
    // Skip onChange call on page mount
    if (!isMountingRef.current) {
      onChange(localConfig);
    } else {
      isMountingRef.current = false;
    }
  }, [localConfig]);

  useEffect(() => {
    let error = false;
    Object.keys(errors).forEach((key) => (error = error || errors[key]));
    hasError(error);
  }, [errors]);

  const formWidget = useMemo(() => {
    const forms: JSX.Element[] = [];
    Object.keys(properties).map((propertyKey) => {
      const onPartialChange: (e: IChangeEvent<ReadonlyJSONObject>) => void = (e) => {
        setErrors((errors) => {
          return {
            ...errors,
            [propertyKey]: e.errors.length !== 0,
          };
        });

        setLocalConfig((previousConfig) => {
          const newConfig = JSON.parse(JSON.stringify(previousConfig));
          newConfig[propertyKey] = e.formData;
          return newConfig as ReadonlyJSONObject;
        });
      };
      forms.push(
        <FormComponent
          schema={properties[propertyKey] as JSONSchema7}
          validator={validatorAjv8 as ValidatorType}
          formData={config ? (config[propertyKey] as ReadonlyJSONObject) : {}}
          onChange={onPartialChange}
          liveValidate
          tagName="div"
          translator={nullTranslator}
          showErrorList={false}
          transformErrors={transformErrors}
        />,
      );
    });
    return forms;
  }, []);

  return <>{formWidget}</>;
};

// Props for the LibraryConfigFormWidget component
export interface LibraryConfigFormWidgetProps {
  schema: JSONSchema7;
  config: ReadonlyJSONObject;
  onChange: (config: ReadonlyJSONObject) => void;
  hasError: (error: boolean) => void;
  selectedType: string;
  selectedSource: string;
}

// Props for the MultiForm component
interface MultiFormProps {
  properties: {
    [key: string]: JSONSchema7Definition;
  };
  config: ReadonlyJSONObject;
  onChange: (config: ReadonlyJSONObject) => void;
  hasError: (error: boolean) => void;
}
