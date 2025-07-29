import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { SpaceMenu } from '../components/SpaceMenu';
import { OPTIONS_TYPE, fetchApiResponse } from '../service';
import { SAGEMAKER_CONTEXT_URL } from '../service/constants';

class SpaceMenuWidget extends ReactWidget {
  private spaceName: string;

  constructor() {
    super();
    this.spaceName = '';
    this.getSpaceName();
  }

  getSpaceName = async () => {
    await fetchApiResponse(SAGEMAKER_CONTEXT_URL, OPTIONS_TYPE.GET).then((result: any) => {
      result &&
        result.json().then((data: any) => {
          this.spaceName = data ? data?.spaceName : null;
          this.update();
        });
    });
  };

  render() {
    return <SpaceMenu spaceName={this.spaceName} />;
  }
}

export { SpaceMenuWidget };
