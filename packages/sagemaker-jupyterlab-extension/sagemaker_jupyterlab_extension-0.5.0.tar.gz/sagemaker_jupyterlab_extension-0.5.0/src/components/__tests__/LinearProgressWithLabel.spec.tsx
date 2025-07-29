import React from 'react';
import { LinearProgressWithLabel } from './../common/LinearProgressWithLabel';
import * as resourceUsageStyles from './../../widgets/styles/resourceUsageStyle';
import { il18Strings } from './../../constants/il18Strings';
import { render, screen } from '@testing-library/react';

describe('LinearProgressWithLabel', () => {
  it('should render LinearProgressWithLabel and match the snapshot', async () => {
    const { cpuMetricTitle } = il18Strings.ResourceUsage;
    render(
      <LinearProgressWithLabel
        value={10}
        singleProgressBarStyle={resourceUsageStyles.SingleProgressBarStyle}
        displayValue={'10%'}
        label={cpuMetricTitle}
        labelClassName={resourceUsageStyles.SingleMetricLabel}
        conatinerClassName={resourceUsageStyles.SingleMetricContainer}
      />,
    );
    await screen.findByRole('container');
    await screen.findByRole('progressbar');

    expect(screen.getAllByRole('progressbar').length).toEqual(1);
    expect(screen.getAllByRole('container').length).toEqual(1);
  });
});
