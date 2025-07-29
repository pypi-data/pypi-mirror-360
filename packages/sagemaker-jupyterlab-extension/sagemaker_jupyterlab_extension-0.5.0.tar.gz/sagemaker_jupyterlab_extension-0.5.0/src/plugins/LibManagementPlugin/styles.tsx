import React from 'react';

/**
 * Common styles used across the LibManagementPlugin
 * Uses JupyterLab theme variables for consistent appearance
 */
export const styles = {
  errorText: {
    color: 'var(--jp-error-color0)',
  },
  linkColor: {
    color: 'var(--jp-content-link-color)',
  },
  importantNote: {
    marginTop: '10px',
    fontWeight: 'bold',
  },
  pluginListEntry: {
    paddingTop: '8px',
    marginTop: '10px',
  },
};

// Styled link component with proper target and rel attributes
export const StyledLink: React.FC<{ href: string; children: React.ReactNode }> = ({ href, children }) => (
  <a target="_blank" style={styles.linkColor} rel="noopener noreferrer" href={href}>
    {children}
  </a>
);

// Component for displaying error messages with consistent styling
export const ErrorText: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span style={styles.errorText} className="jp-PluginList-entry-label-text">
    {children}
  </span>
);

// Component for displaying important notes with emphasis
export const ImportantNote: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={styles.importantNote}>{children}</div>
);
