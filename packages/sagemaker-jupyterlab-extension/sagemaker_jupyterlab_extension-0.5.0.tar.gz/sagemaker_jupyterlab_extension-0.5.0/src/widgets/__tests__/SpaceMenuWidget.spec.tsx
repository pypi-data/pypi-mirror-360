import { getByTestId, render } from '@testing-library/react';
import { SpaceMenuWidget } from '../SpaceMenuWidget';
import { spaceTestIds } from '../../constants/spaceMenuConstants';

describe('SpaceMenuWidget', () => {
  it('should render spaceMenu', async () => {
    render(new SpaceMenuWidget().render());
    expect(await getByTestId(document.body, spaceTestIds.menu.header)).toBeTruthy();
  });
});
