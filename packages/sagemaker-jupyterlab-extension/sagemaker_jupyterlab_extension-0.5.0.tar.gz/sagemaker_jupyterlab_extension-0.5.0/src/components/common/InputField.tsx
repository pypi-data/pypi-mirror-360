import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import * as styles from './../styles/InputFieldStyles';

interface InputFieldProps {
  valuePassed?: string;
  label: string;
  id: string;
  helperText: string;
  error: boolean;
  handleChange: (value: string) => void;
  regEx: any;
}

const InputField: React.FunctionComponent<InputFieldProps> = ({
  label,
  id,
  helperText,
  error,
  handleChange,
  regEx,
  ...props
}) => {
  const [value, setValue] = useState<string>('');
  const [isValid, setIsValid] = useState<boolean>(true);

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setValue(e.target.value);
    const reg = new RegExp(regEx);
    setIsValid(reg.test(e.target.value));
    handleChange(e.target.value);
  };
  return (
    <TextField
      variant="standard"
      className={styles.inputField}
      data-testid="text-field-container"
      error={!isValid}
      id={id}
      label={label}
      helperText={helperText}
      value={value}
      onChange={(e) => onChange(e)}
      {...props}
    />
  );
};

export { InputField };
