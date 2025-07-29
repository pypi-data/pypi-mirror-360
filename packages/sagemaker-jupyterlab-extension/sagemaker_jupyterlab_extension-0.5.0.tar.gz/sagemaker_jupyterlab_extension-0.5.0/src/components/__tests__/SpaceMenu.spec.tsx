import React from 'react';
import { render } from '@testing-library/react';
import { SpaceMenu } from '../SpaceMenu';
import { getCookie } from '../../utils/sessionManagerUtils';
import { spaceTestIds } from '../../constants/spaceMenuConstants';
import { il18Strings } from '../../constants/il18Strings';

// Mocking the getCookie function
jest.mock('../../utils/sessionManagerUtils', () => ({
  getCookie: jest.fn(),
}));

const { unknownSpace, unknownUser } = il18Strings.Space;

describe('SpaceMenu Component', () => {
  beforeEach(() => {
    jest.clearAllMocks(); // Reset mock calls before each test
  });

  const cookie = ['studioUserProfileName:John Doe', 'John Doe'];

  test('renders private space header when spaceName is not provided', () => {
    // Mocking the getCookie function to return a user profile name
    getCookie.mockReturnValue(cookie);

    const { getByTestId, getByText } = render(<SpaceMenu spaceName="" />);

    // Assert that the header element is rendered
    const headerElement = getByTestId(spaceTestIds.menu.header);
    expect(headerElement).toBeTruthy();

    // Assert that the user profile name is displayed correctly
    expect(getByText('John Doe / ' + unknownSpace)).toBeTruthy();
  });

  test('renders shared space header when spaceName is provided', () => {
    // Mocking the getCookie function to return a user profile name
    getCookie.mockReturnValue(cookie);

    const { getByTestId, getByText } = render(<SpaceMenu spaceName="Shared Space" />);

    // Assert that the header element is rendered
    const headerElement = getByTestId(spaceTestIds.menu.header);
    expect(headerElement).toBeTruthy();

    // Assert that the user profile name is displayed correctly
    expect(getByText('John Doe / Shared Space')).toBeTruthy();
  });

  test('renders shared space header when spaceName is provided and userProfile cookie is empty', () => {
    // Mocking the getCookie function to return a user profile name
    getCookie.mockReturnValue('');

    const { getByTestId, getByText } = render(<SpaceMenu spaceName="Shared Space" />);

    // Assert that the header element is rendered
    const headerElement = getByTestId(spaceTestIds.menu.header);
    expect(headerElement).toBeTruthy();

    // Assert that the user profile name is displayed correctly
    expect(getByText(unknownUser + ' / Shared Space')).toBeTruthy();
  });
});
