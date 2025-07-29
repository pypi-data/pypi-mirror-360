import { css } from '@emotion/css';

const increaseZIndex = css`
  &.jp-ThemedContainer {
    z-index: 2;
  }
`;
const gitCloneContainer = css`
  width: 460px;
  input {
    width: 460px;
  }
  .MuiFormControl-root.MuiTextField-root {
    margin-bottom: 20px;
  }
`;

const MarginBottom = css`
  margin-bottom: 20px;
`;

export { gitCloneContainer, MarginBottom, increaseZIndex };
