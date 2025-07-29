import { HideShutDownPlugin } from './plugins';
import { SessionManagementPlugin } from './plugins';
import { ResourceUsagePlugin } from './plugins';
import { GitClonePlugin } from './plugins';
import { PerformanceMeteringPlugin, SpaceMenuPlugin } from './plugins';
import { CloneRepositoryPlugin } from './plugins';
import { LibManagementPlugin } from './plugins';

export default [
  HideShutDownPlugin,
  SessionManagementPlugin,
  ResourceUsagePlugin,
  GitClonePlugin,
  PerformanceMeteringPlugin,
  SpaceMenuPlugin,
  CloneRepositoryPlugin,
  LibManagementPlugin,
];
