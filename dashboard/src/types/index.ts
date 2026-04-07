export type DisorderKey =
  | 'adhd'
  | 'anxiety'
  | 'autism'
  | 'bipolar'
  | 'cross'
  | 'eating'
  | 'mdd'
  | 'ocd'
  | 'other'
  | 'ptsd'
  | 'scz'
  | 'substance';

export interface Disorder {
  id: DisorderKey;
  name: string;
  fullName: string;
  color: string;
  variantCount: number;
  significantLoci: number;
  sampleSize: number;
  latestStudy: string;
  pmid: string;
  description: string;
}

export interface Variant {
  snpId: string;
  chromosome: number;
  position: number;
  pValue: number;
  negLogP: number;
  effectSize: number;
  standardError: number;
  alleleFreq: number;
  refAllele: string;
  altAllele: string;
  nearestGene: string;
  consequence: string;
}

export interface ManhattanData {
  variants: Variant[];
  disorderId: DisorderKey;
}

export interface QQData {
  observed: number[];
  expected: number[];
  lambdaGC: number;
}

export interface CrossTraitCorrelation {
  disorder1: DisorderKey;
  disorder2: DisorderKey;
  rg: number;
  se: number;
  pValue: number;
}

export interface DatasetSummary {
  totalVariants: number;
  totalDisorders: number;
  totalStudies: number;
  totalSampleSize: number;
  lastUpdated: string;
}

export interface SearchResult {
  snpId: string;
  chromosome: number;
  position: number;
  nearestGene: string;
  disorders: {
    disorderId: DisorderKey;
    pValue: number;
    effectSize: number;
  }[];
}

export interface FilterState {
  pValueThreshold: number;
  chromosome: number | null;
  mafMin: number;
  mafMax: number;
  consequenceTypes: string[];
}

export interface StatsInfo {
  totalVariants: number;
  significantVariants: number;
  suggestiveVariants: number;
  lambdaGC: number;
  meanChiSq: number;
  ldScoreIntercept: number;
  sampleSize: number;
  heritability: number;
}

// Used by API client and plot components
export interface VariantRecord {
  snp: string;
  chr: number;
  bp: number;
  a1: string;
  a2: string;
  effect: number;
  se: number;
  pval: number;
  maf: number;
  nearest_gene?: string;
  [key: string]: any;
}

export interface PlotData {
  traces: any[];
  layout: Record<string, any>;
}
