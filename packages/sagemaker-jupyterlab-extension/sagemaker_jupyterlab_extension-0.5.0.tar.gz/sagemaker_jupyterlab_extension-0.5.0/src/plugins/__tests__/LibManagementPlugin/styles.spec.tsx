import React from 'react';
import { render } from '@testing-library/react';
import { styles, StyledLink, ErrorText, ImportantNote } from '../../LibManagementPlugin/styles';

describe('styles', () => {
  it('should have the correct style objects', () => {
    expect(styles).toHaveProperty('errorText');
    expect(styles).toHaveProperty('linkColor');
    expect(styles).toHaveProperty('importantNote');
    expect(styles).toHaveProperty('pluginListEntry');

    expect(styles.errorText).toEqual({ color: 'var(--jp-error-color0)' });
    expect(styles.linkColor).toEqual({ color: 'var(--jp-content-link-color)' });
    expect(styles.importantNote).toEqual({ marginTop: '10px', fontWeight: 'bold' });
    expect(styles.pluginListEntry).toEqual({ paddingTop: '8px', marginTop: '10px' });
  });
});

describe('StyledLink', () => {
  it('should render correctly with props', () => {
    const { container } = render(<StyledLink href="https://example.com">Test Link</StyledLink>);

    const link = container.querySelector('a');
    expect(link?.getAttribute('href')).toBe('https://example.com');
    expect(link?.getAttribute('target')).toBe('_blank');
    expect(link?.getAttribute('rel')).toBe('noopener noreferrer');
    expect(link?.textContent).toBe('Test Link');
  });
});

describe('ErrorText', () => {
  it('should render correctly with children', () => {
    const { container } = render(<ErrorText>Error message</ErrorText>);

    const span = container.querySelector('span');
    expect(span?.className).toContain('jp-PluginList-entry-label-text');
    expect(span?.textContent).toBe('Error message');
  });
});

describe('ImportantNote', () => {
  it('should render correctly with children', () => {
    const { container } = render(<ImportantNote>Important information</ImportantNote>);

    const div = container.querySelector('div');
    expect(div?.textContent).toBe('Important information');
  });
});
