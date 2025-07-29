import { ServerConnection } from '@jupyterlab/services';
import { PageConfig } from '@jupyterlab/coreutils';

// API service for marker file operations
class MarkerFileService {
  private baseUrl: string;
  private settings: ServerConnection.ISettings;

  constructor() {
    this.baseUrl = PageConfig.getBaseUrl();
    this.settings = ServerConnection.makeSettings({ baseUrl: this.baseUrl });
  }

  /**
   * Check if marker file exists
   * @returns Promise<boolean> - true if file exists, false otherwise
   */
  async checkMarkerFile(): Promise<boolean> {
    const url = `${this.baseUrl}aws/sagemaker/api/create-marker-file`;

    const init = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const response = await ServerConnection.makeRequest(url, init, this.settings);

    if (!response.ok) {
      throw new Error(`Failed to check marker file: ${response.statusText}`);
    }

    const result = await response.json();
    return result.exists;
  }

  /**
   * Create marker file
   * @returns Promise<boolean> - true if file was created, false if it already existed
   */
  async createMarkerFile(): Promise<boolean> {
    const url = `${this.baseUrl}aws/sagemaker/api/create-marker-file`;

    const init = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const response = await ServerConnection.makeRequest(url, init, this.settings);

    if (!response.ok) {
      throw new Error(`Failed to create marker file: ${response.statusText}`);
    }

    const result = await response.json();
    return result.created;
  }
}

// Create singleton instance
const markerFileService = new MarkerFileService();

/**
 * Check if marker file exists
 * @returns Promise<boolean> - true if file exists, false otherwise
 */
export async function checkMarkerFile(): Promise<boolean> {
  return await markerFileService.checkMarkerFile();
}

/**
 * Create marker file
 * @returns Promise<boolean> - true if file was created, false if it already existed
 */
export async function createMarkerFile(): Promise<boolean> {
  return await markerFileService.createMarkerFile();
}
