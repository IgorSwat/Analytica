interface BasicData {
  length: number;
  columns: string[];
  data: string[][];
}

export interface DataVisualization extends DataNormalization {
  types: number[];               // Feature types
  states: boolean[];             // Feature states
  selection: string;
  error: boolean;                // if input range is incorrect
}

export interface DataNormalization extends BasicData {
  numericMethod: string;
}

export interface PcaData extends BasicData {
  variances: number[];
  noComponents: number;
  error: boolean;
}

export interface ClusterData extends BasicData {
  clustering_method: string;
  n_clusters: number;
  eps: number;
  min_samples: number;
  linkage: string;

  silhouette: number;
  davies_bouldin: number;
  quality: number;
}