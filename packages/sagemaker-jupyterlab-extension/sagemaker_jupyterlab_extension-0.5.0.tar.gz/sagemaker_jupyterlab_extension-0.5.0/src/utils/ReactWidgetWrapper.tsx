/**
 * The Wrapper is Helper React Wrapper to test the Widgets for unit test cases
 * Reused from code.amazon.com
 * https://code.amazon.com/packages/LooseLeafJupyterLabExtension/blobs/24a10d089a8369d10e50bd084490caae34061d7a/--/test/utils.tsx#L926
 */
import React from 'react';

interface ReactWidgetWrapperProps {
  item: any;
}

class ReactWidgetWrapper extends React.Component<ReactWidgetWrapperProps> {
  render() {
    return (this.props.item as any).render();
  }
}

export { ReactWidgetWrapper, ReactWidgetWrapperProps };
