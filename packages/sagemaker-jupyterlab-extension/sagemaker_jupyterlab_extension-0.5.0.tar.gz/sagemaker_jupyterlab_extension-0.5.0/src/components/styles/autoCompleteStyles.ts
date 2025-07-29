import { css } from '@emotion/css';

const InputLabel = (required = false) => css`
  color: var(--jp-color-root-light-800);
  font-weight: 400;
  font-size: var(--jp-ui-font-size1);
  line-height: var(--jp-ui-font-size1);
  margin-bottom: var(--jp-ui-font-size1);
  ${required &&
  `
    &:after {
      content: '*';
      color: var(--jp-error-color1);
    }
  `}
`;

const autoCompleteContainer = css`
  margin-top: 20px;
`;

export { InputLabel, autoCompleteContainer };
