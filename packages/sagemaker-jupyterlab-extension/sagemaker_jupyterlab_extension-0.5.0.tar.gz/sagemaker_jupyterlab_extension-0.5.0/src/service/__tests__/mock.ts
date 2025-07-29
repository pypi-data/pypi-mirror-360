import { GitCloneRepositoriesResponse } from '../../constants/gitCloneConstants';
import { ProjectsListResponse } from '../../constants/projectCloneConstants';
import { InstanceMetricsResponse } from '../../constants/resourceUsageConstants';

const instanceMetricsMock: InstanceMetricsResponse = {
  metrics: {
    memory: {
      rss_in_bytes: 5326798848,
      total_in_bytes: 16287559680,
      memory_percentage: 34.8,
    },
    cpu: {
      cpu_count: 8,
      cpu_percentage: 0.0,
    },
    storage: {
      free_space_in_bytes: 418265493504,
      used_space_in_bytes: 109974339584,
      total_space_in_bytes: 528342487040,
    },
  },
};

const instanceMetricsMockForHigherStorageUse: InstanceMetricsResponse = {
  metrics: {
    memory: {
      rss_in_bytes: 5326798848,
      total_in_bytes: 16287559680,
      memory_percentage: 34.8,
    },
    cpu: {
      cpu_count: 8,
      cpu_percentage: 0.0,
    },
    storage: {
      free_space_in_bytes: 429496729,
      used_space_in_bytes: 1030792151,
      total_space_in_bytes: 1073741824,
    },
  },
};

const gitCloneRepoMock: GitCloneRepositoriesResponse = {
  GitCodeRepositories: ['repo1', 'repo2', 'repo3'],
};

const projectsListMock: ProjectsListResponse = {
  projectsList: ['project1', 'project2', 'project3'],
};

export { gitCloneRepoMock, instanceMetricsMock, instanceMetricsMockForHigherStorageUse, projectsListMock };
