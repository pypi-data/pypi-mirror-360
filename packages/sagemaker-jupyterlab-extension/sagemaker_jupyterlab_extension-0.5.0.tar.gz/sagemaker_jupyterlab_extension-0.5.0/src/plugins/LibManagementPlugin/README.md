# Extension Management Plugin for SageMaker Studio

A JupyterLab extension for managing JupyterLab extensions and conda packages in Amazon SageMaker Studio environments.

## Overview

The Extension Management Plugin provides a user-friendly interface for configuring, installing, and managing JupyterLab extensions and conda packages within SageMaker Studio. It integrates directly with JupyterLab's interface, allowing users to:

- Configure conda packages and channels
- Install extensions with a simple UI
- Track installation progress
- Automatically install extensions on first startup after new JupyterLab application restart

## Architecture

The plugin is structured as a JupyterLab extension that adds a new editor type for the `.libs.json` configuration file. The main components include:

### Component Relationships

```
LibManagementPlugin (entry point)
├── LibManagementDocumentManager
│   └── LibraryEditorFactory
│       └── LibraryDocumentWidget
│           └── LibraryConfigEditor
│               ├── LibraryConfigList
│               ├── LibraryConfigPanel
│               │   └── LibraryConfigForm
│               └── PackageInstaller (on save)
│                   ├── CommandMonitor
│                   └── metrics
├── PackageInstaller (on startup)
│   ├── CommandMonitor
│   └── metrics
└── utils (checkForMarkerFile, createMarkerFile)
```

### Core Components

- **LibManagementPlugin**: Main plugin entry point that registers commands and initializes the extension
- **LibraryConfigEditor**: React-based editor for managing extension configurations
- **PackageInstaller**: Handles the installation of extensions via terminal commands
- **CommandMonitor**: Monitors terminal output to track command execution status

### Document Management

- **LibraryDocumentWidget**: Document widget that wraps the configuration editor
- **LibraryEditorFactory**: Factory for creating extension editor widgets
- **LibManagementDocumentManager**: Manages extension configuration documents

### UI Components

- **LibraryConfigForm**: Form component for editing extension configurations
- **LibraryConfigList**: List component showing available configuration sections
- **LibraryConfigPanel**: Panel component for the main configuration interface

### Utilities

- **schema.ts**: JSON schema definition for the extension configuration format
- **utils.ts**: Utility functions for file operations and environment checks
- **metrics**: Telemetry system for tracking installation success/failure

### Configuration

- **config.tsx**: Central configuration file containing icons, config metadata, help text, and other UI descriptions

## Configuration Format

The plugin uses a JSON configuration format (`.libs.json`) with the following structure:

```json
{
  "Python": {
    "CondaPackages": {
      "Channels": [],
      "PackageSpecs": []
    }
  },
  "ApplyChangeToSpace": false
}
```

- **Channels**: List of conda channels to use for package installation
- **PackageSpecs**: List of conda packages to install (with optional version constraints)
- **ApplyChangeToSpace**: Whether to apply changes to the entire SageMaker Studio space

## Tests

The plugin includes comprehensive unit test coverage for all components:

### Core Functionality Tests

- **LibManagementPlugin.spec.ts**: Tests plugin activation, command registration, and launcher integration
- **CommandMonitor.spec.ts**: Tests terminal command execution monitoring, success/failure detection, and already-installed package detection
- **PackageInstaller.spec.ts**: Tests package installation with various configuration scenarios, terminal handling, and notification management
- **schema.spec.ts**: Validates the JSON schema structure for configuration files

### UI Component Tests

- **LibraryConfigForm.spec.tsx**: Tests form rendering, validation, error handling, and form submission
- **LibraryConfigList.spec.ts**: Tests configuration list rendering and selection functionality
- **LibraryConfigPanel.spec.tsx**: Tests panel rendering and integration with other UI components
- **styles.spec.tsx**: Tests style definitions and theme integration

### Document Management Tests

- **LibManagementDocumentManager.spec.ts**: Tests document creation, opening, and management
- **LibraryDocumentWidget.spec.ts**: Tests document widget initialization and rendering
- **LibraryEditorFactory.spec.ts**: Tests editor factory creation and widget instantiation

### Utility Tests

- **configs.spec.ts**: Tests configuration constants and default values
- **transformErrors.spec.ts**: Tests error transformation and user-friendly error message generation
- **index.spec.ts**: Tests proper module exports