import { css } from '@emotion/css';

const TextInputBase = () => css`
  .MuiFormHelperText-root.Mui-error::before {
    display: inline-block;
    vertical-align: middle;
    background-size: 1rem 1rem;
    height: var(--text-input-error-icon-height);
    width: var(--text-input-error-icon-width);
    background-image: var(--text-input-helper-text-alert-icon);
    background-repeat: no-repeat;
    content: ' ';
  }
`;

const inputField = css`
  .MuiInputBase-input MuiInput-input {
    width: 400px;
    margin-bottom: 20px;
  }
`;

export { TextInputBase, inputField };
