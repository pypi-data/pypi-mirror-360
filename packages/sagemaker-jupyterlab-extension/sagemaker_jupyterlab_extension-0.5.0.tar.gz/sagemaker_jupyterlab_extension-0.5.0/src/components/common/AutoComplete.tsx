import * as React from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import * as styles from '../styles/autoCompleteStyles';

interface DropdownItem {
  readonly label: string;
  readonly value: string;
  readonly isDisabled?: boolean;
}

interface AutoCompleteProps {
  options: DropdownItem[];
  label: string;
  handleChange: (item: string | DropdownItem | null) => void;
  disabled?: boolean;
  value: DropdownItem | string | null;
  freeSolo: boolean;
}

const AutoComplete: React.FunctionComponent<AutoCompleteProps> = ({ options, handleChange, label, freeSolo }) => {
  const onChange = (e: React.SyntheticEvent<Element, Event>, newValue: string | DropdownItem | null) => {
    handleChange(newValue);
  };

  return (
    <div className={styles.autoCompleteContainer}>
      <label className={styles.InputLabel(true)}>{label}</label>
      <Autocomplete
        id="autocomplete"
        freeSolo={freeSolo}
        autoSelect
        onChange={(event, newValue) => onChange(event, newValue)}
        onInputChange={(event, newInputValue) => onChange(event, newInputValue)}
        options={options.map((option: DropdownItem) => option.label)}
        renderInput={(params) => <TextField {...params} variant="outlined" size="small" margin="dense" />}
      />
    </div>
  );
};

export { AutoComplete, DropdownItem };
