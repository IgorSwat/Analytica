


export interface DataNormalization {
  length: number;
  columns: string[];
  data: string[][];
  error: boolean;
}

export interface DataVisualization extends DataNormalization {
  types: number[]
}
