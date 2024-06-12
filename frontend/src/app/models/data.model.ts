export interface DataNormalization {
  length: number;
  columns: string[];
  data: string[][];
  error: boolean;
}

export interface DataVisualization extends DataNormalization {
  types: number[],             // Feature types
  states: boolean[]            // Feature states
}

export interface PcaInfo {
  columns: string[],
  loads1: number[],
  loads2: number[],
  selections: boolean[]
}

export interface ClusterInfo {
  columns: string[],
  loads1: number[],
  loads2: number[],
}