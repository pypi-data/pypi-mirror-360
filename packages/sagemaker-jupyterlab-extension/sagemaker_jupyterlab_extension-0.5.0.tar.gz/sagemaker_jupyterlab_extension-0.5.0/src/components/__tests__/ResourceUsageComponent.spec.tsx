import React from 'react';
import { il18Strings } from './../../constants/il18Strings';
import { render, screen, fireEvent } from '@testing-library/react';
import { instanceMetricsMock, instanceMetricsMockForHigherStorageUse } from './../../service/__tests__/mock';
import { ResourceUsageComponent } from './../ResourceUsageComponent';

const { instanceMemoryProgressBarTitle } = il18Strings.ResourceUsage;

describe('ResourceUsageComponent test suite', () => {
  it('should render Title and the progress bar on the footer', async () => {
    const onClickHandlerMock = jest.fn();
    const mockData = instanceMetricsMock;

    render(<ResourceUsageComponent onClickHandler={onClickHandlerMock} instanceMetricsResponse={mockData} />);
    expect(screen.getAllByText(instanceMemoryProgressBarTitle).length).toEqual(1);
    expect(screen.getAllByRole('progressbar').length).toEqual(1);
  });

  it('should test the onClick handler and open the plugin rendering the metrics for all the resource', async () => {
    const onClickHandlerMock = jest.fn();
    const mockData = instanceMetricsMock;

    render(<ResourceUsageComponent onClickHandler={onClickHandlerMock} instanceMetricsResponse={mockData} />);
    await screen.findByText(instanceMemoryProgressBarTitle);
    const clickHandler = screen.getByTestId('resource-usage-widget-click-handler');
    fireEvent.click(clickHandler);
    expect(onClickHandlerMock).toHaveBeenCalled();
    expect(screen.getAllByRole('progressbar').length).toEqual(4);
  });

  it('should test when there is no metrics data from API and is rendering a loading Linear Progress bar', async () => {
    const onClickHandlerMock = jest.fn();
    const mockData = null;

    render(<ResourceUsageComponent onClickHandler={onClickHandlerMock} instanceMetricsResponse={mockData} />);
    await screen.findByText(instanceMemoryProgressBarTitle);
    expect(screen.getAllByText(instanceMemoryProgressBarTitle).length).toEqual(1);
    expect(screen.getAllByRole('progressbar').length).toEqual(1);
    expect(screen.getAllByRole('progressbar')[0].children.length).toEqual(2);

    const clickHandler = screen.getByTestId('resource-usage-widget-click-handler');
    fireEvent.click(clickHandler);
    expect(onClickHandlerMock).toHaveBeenCalled();
    expect(screen.getAllByRole('progressbar').length).toEqual(4);
    fireEvent.click(clickHandler);
    expect(screen.getAllByRole('progressbar').length).toEqual(1);
  });

  it('should test useEffect for for higher storage usage mock being passed', async () => {
    const onClickHandlerMock = jest.fn();
    const mockData = instanceMetricsMockForHigherStorageUse;

    render(<ResourceUsageComponent onClickHandler={onClickHandlerMock} instanceMetricsResponse={mockData} />);
    await screen.findByText(instanceMemoryProgressBarTitle);
    const clickHandler = screen.getByTestId('resource-usage-widget-click-handler');
    fireEvent.click(clickHandler);
    expect(onClickHandlerMock).toHaveBeenCalled();
    expect(screen.getAllByRole('progressbar').length).toEqual(4);
    expect(screen.getAllByRole('container')[2].outerHTML.includes('Storage: 96.00%')).toEqual(true);
  });
});
