import { LabIcon } from '@jupyterlab/ui-components';
import React from 'react';

import libraryIconStr from './icons/md-library-icon.svg';
import condaIconStr from './icons/conda-icon.svg';
import { StyledLink, ErrorText, ImportantNote } from './styles';

// Connection types supported by the library management plugin
enum ConnectionType {
  IAM = 'iam',
}

// Icon for the library management plugin
export const libMgmtIcon = new LabIcon({
  name: 'libmgmt:library-management-icon',
  svgstr: libraryIconStr,
});

// Icon for conda packages
export const condaIcon = new LabIcon({
  name: 'libmgmt:conda-icon',
  svgstr: condaIconStr,
});

/**
 * Configuration metadata for different package types
 * Defines UI elements and supported connection types
 */
export const CONFIGS: { [key: string]: { [key: string]: ConfigMetadata } } = {
  Python: {
    CondaPackages: {
      title: 'Python - Conda Packages/Extensions',
      icon: condaIcon,
      supportedConnectionType: [ConnectionType.IAM],
      // https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html
      additionalDescription: [
        <div key="conda-desc-1">
          Use this interface to manage automatic Conda package installations for your environment. Packages specified
          here will be installed each time your space runs.
        </div>,
        <div key="conda-desc-2">
          Enter package names and optional version constraints (e.g., pandas or pandas{'>'}=1.0.0)
        </div>,
        <div key="conda-desc-3">
          For more information on package specification, see&nbsp;
          {link(
            'Conda package specification',
            'https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html',
          )}
        </div>,
        <ImportantNote key="conda-desc-4">Important Notes:</ImportantNote>,
        <div key="conda-desc-5">• Closing the background terminal cancels ongoing installations</div>,
        <div key="conda-desc-6">
          • After package installation, Jupyter server automatically restarts. This restart clears all in-memory
          variables and active sessions
        </div>,
        <div key="conda-desc-7">
          • Removing packages from this interface only prevents future installations. Package uninstallation must be
          done separately
        </div>,
        <div key="conda-desc-8">
          • Channel priorities set here apply only to this interface. Packages installed via notebook or terminal are
          not tracked here
        </div>,
        <div key="conda-desc-9">• Installation requires internet access (except for custom channels)</div>,
      ],
    },
  },
};

/**
 * Metadata interface for configuration items
 * Defines the structure of configuration entries in the UI
 */
export interface ConfigMetadata {
  title: string;
  icon: LabIcon;
  supportedConnectionType: ConnectionType[];
  regex?: string;
  additionalDescription?: JSX.Element[];
}

// Error messages displayed to users
export const ERROR_MESSAGES = {
  CORRUPTED_CONFIG_FILE: (path: string) => (
    <>
      <ErrorText>
        The configuration file {path} is corrupted or invalid.
        <br />
        <br />
        To resolve this issue:
        <br />
        • Remove the corrupted file and restart the UI (you will need to reconfigure preferences), OR
        <br />
        • Fix the file format back to how it was originally
        <br />
        <br />
        Note: Removing the file will reset all saved extension and package configurations.
        <br />
        Please exit and reopen this widget after making changes.
      </ErrorText>
    </>
  ),
};

// Initial configuration structure for new config files
export const initConfig = {
  ApplyChangeToSpace: false,
  Python: {
    CondaPackages: {
      Channels: [],
      PackageSpecs: [],
    },
  },
};

// Helper function to create styled links
function link(linkName: string, href: string) {
  return <StyledLink href={href}>{linkName}</StyledLink>;
}
