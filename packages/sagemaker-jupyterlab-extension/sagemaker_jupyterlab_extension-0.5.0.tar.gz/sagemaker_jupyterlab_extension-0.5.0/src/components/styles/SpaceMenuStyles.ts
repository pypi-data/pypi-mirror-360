import { css } from '@emotion/css';

const SpaceMenuHeader = css`
  margin: -6px 0;
  padding: 0 var(--jp-size-2);
  height: 10;
  border-radius: var(--jp-radius-small);
  font-size: var(--jp-size-3);
  display: flex;
  justify-content: center;
  align-items: center;

  & > p {
    display: inline-block;
    user-select: none;
    color: var(--jp-color-root-light-800);
  }

  & > svg {
    padding: 0 var(--jp-size-2);
  }
`;

export default {
  SpaceMenuHeader,
};
