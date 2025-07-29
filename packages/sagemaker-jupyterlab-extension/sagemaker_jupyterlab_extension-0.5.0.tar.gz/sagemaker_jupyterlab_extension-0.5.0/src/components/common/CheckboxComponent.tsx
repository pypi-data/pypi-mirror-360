import React, { useState } from 'react';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';

interface CheckboxComponentProps {
  label: string;
  id: string;
  handleChange: (value: boolean) => void;
  checked?: boolean;
}
const CheckboxComponent: React.FunctionComponent<CheckboxComponentProps> = ({ label, id, handleChange, ...props }) => {
  const [checked, setChecked] = useState(true);

  const onChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setChecked(event.target.checked);
    handleChange(event.target.checked);
  };

  return (
    <>
      <FormControlLabel
        control={
          <Checkbox
            data-testid="checkbox-field"
            inputProps={{ 'aria-label': 'controlled' }}
            checked={checked}
            onChange={onChange}
            id={id}
            {...props}
          />
        }
        label={label}
      />
    </>
  );
};

export { CheckboxComponent };
