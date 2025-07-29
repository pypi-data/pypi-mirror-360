import React from 'react';
import LinearProgress from '@mui/material/LinearProgress';

interface LinearProgressWithLabelProps {
  value: number;
  displayValue: string;
  label: string;
  labelClassName: string;
  singleProgressBarStyle: string;
  conatinerClassName: string;
}

const LinearProgressWithLabel: React.FunctionComponent<LinearProgressWithLabelProps> = ({
  value,
  singleProgressBarStyle,
  displayValue,
  label,
  labelClassName,
  conatinerClassName,
}) => {
  return (
    <div role="container" data-testid="linear-progress-bar-container">
      <div className={conatinerClassName}>
        {label && (
          <span className={labelClassName}>
            {label} {displayValue}%
          </span>
        )}
        <LinearProgress
          data-testid="linear-progress-bar"
          className={singleProgressBarStyle}
          variant="determinate"
          value={value}
        />
      </div>
    </div>
  );
};

export { LinearProgressWithLabel };
