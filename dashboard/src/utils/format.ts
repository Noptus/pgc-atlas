export function formatPValue(p: number): string {
  if (p === 0) return '< 1e-300';
  if (p < 1e-4) return p.toExponential(2);
  return p.toPrecision(3);
}

export function formatNumber(n: number): string {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)}B`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
  return n.toLocaleString();
}

export function formatPosition(chr: number, pos: number): string {
  return `chr${chr}:${pos.toLocaleString()}`;
}

export function negLog10(p: number): number {
  if (p === 0) return 300;
  return -Math.log10(p);
}

export function formatEffectSize(beta: number): string {
  const sign = beta > 0 ? '+' : '';
  return `${sign}${beta.toFixed(4)}`;
}

export function chromosomeLabel(chr: number): string {
  if (chr === 23) return 'X';
  if (chr === 24) return 'Y';
  return chr.toString();
}

// Chromosome sizes in base pairs (GRCh38)
export const CHROMOSOME_SIZES: Record<number, number> = {
  1: 248956422,
  2: 242193529,
  3: 198295559,
  4: 190214555,
  5: 181538259,
  6: 170805979,
  7: 159345973,
  8: 145138636,
  9: 138394717,
  10: 133797422,
  11: 135086622,
  12: 133275309,
  13: 114364328,
  14: 107043718,
  15: 101991189,
  16: 90338345,
  17: 83257441,
  18: 80373285,
  19: 58617616,
  20: 64444167,
  21: 46709983,
  22: 50818468,
};

export function getCumulativeOffset(chr: number): number {
  let offset = 0;
  for (let i = 1; i < chr; i++) {
    offset += CHROMOSOME_SIZES[i] || 0;
  }
  return offset;
}
