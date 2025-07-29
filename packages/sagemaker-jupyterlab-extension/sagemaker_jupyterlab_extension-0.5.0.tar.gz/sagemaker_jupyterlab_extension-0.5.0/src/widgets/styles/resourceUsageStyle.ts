import { css } from '@emotion/css';

/** JupyterLabs uses an 4px grid */
const Padding = {
  small: '4px',
  medium: '8px',
  mediumLarge: '12px',
  sixteen: '16px',
  large: '20px',
  xl: '24px',
  xxl: '28px',
  xxxl: '32px',
};

const KernelMetricContainer = css`
  border-bottom: solid 1px var(--sm-border-color2);
`;

const MetricsWindowStyle = css`
  background-color: var(--jp-layout-color2);
  border: solid 1px var(--jp-border-color2);
  color: var(--jp-ui-font-color1);
  font-size: var(--jp-ui-font-size1);
  position: fixed;
  bottom: 25px;
`;

const MetricsContainerStyle = css`
  margin: 0 ${Padding.mediumLarge} ${Padding.medium};
`;

const MetricsTitleStyle = css`
  font-weight: bold;
  margin: ${Padding.medium} 0 0 ${Padding.medium};
`;

const MetricsDescriptionStyle = css`
  margin: 0 ${Padding.mediumLarge} 0 ${Padding.sixteen};
`;

const SingleProgressBarStyle = css`
  border-radius: 10px;
  height: 100%;
  width: 30px;
`;

const RemoteStatusContainer = css`
  line-height: 24px;
  padding: 0 5px;

  &:hover {
    background-color: var(--jp-layout-color2);
  }
`;

const SpacerStyle = css`
  padding-left: 4px;
`;

const SingleMetricContainer = css`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin: 6px 12px;
`;

const SingleMetricLabel = css`
  color: var(--jp-ui-font-color1);
  font-size: var(--jp-ui-font-size1);
  padding-right: 5px;
`;

const StatusBarProgressBarContainerStyle = css`
  border-radius: 10px;
  width: 40px;
  margin: 0 0 2px 4px;
  height: 6px !important;
`;

const SingleProgressBarContainerStyle = css`
  border-radius: 10px;
  display: inline-block;
  width: 40px;
  height: 8px;
`;

const ResourceWidgetConatiner = css`
  display: flex;
  align-items: center;
`;

export {
  KernelMetricContainer,
  MetricsContainerStyle,
  MetricsTitleStyle,
  MetricsDescriptionStyle,
  MetricsWindowStyle,
  SingleProgressBarStyle,
  RemoteStatusContainer,
  SpacerStyle,
  StatusBarProgressBarContainerStyle,
  SingleMetricContainer,
  SingleMetricLabel,
  SingleProgressBarContainerStyle,
  ResourceWidgetConatiner,
};
