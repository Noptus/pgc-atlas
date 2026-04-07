import { Disorder, DisorderKey, VariantRecord, PlotData } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';
const USE_MOCK = !import.meta.env.VITE_API_URL;

// ── Disorder metadata ──────────────────────────────────────────────────
export const DISORDERS: Record<DisorderKey, Disorder> = {
  adhd:      { id: 'adhd',      name: 'ADHD',                fullName: 'Attention-Deficit/Hyperactivity Disorder',  color: '#FF6B6B', variantCount: 31_200_000, significantLoci: 27,  sampleSize: 225_534, latestStudy: 'Demontis et al. 2023', pmid: '36702997',  description: 'GWAS meta-analysis of ADHD across multiple cohorts' },
  anxiety:   { id: 'anxiety',   name: 'Anxiety',             fullName: 'Anxiety Disorders',                         color: '#FFE66D', variantCount: 27_500_000, significantLoci: 12,  sampleSize: 175_000, latestStudy: 'Levey et al. 2026',    pmid: '38200001',  description: 'Generalized anxiety and panic disorder GWAS' },
  autism:    { id: 'autism',     name: 'Autism',              fullName: 'Autism Spectrum Disorder',                   color: '#4ECDC4', variantCount: 18_600_000, significantLoci: 5,   sampleSize: 46_350,  latestStudy: 'Grove et al. 2019',    pmid: '30804558',  description: 'ASD common variant associations' },
  bipolar:   { id: 'bipolar',   name: 'Bipolar',             fullName: 'Bipolar Disorder',                          color: '#A78BFA', variantCount: 74_400_000, significantLoci: 64,  sampleSize: 413_466, latestStudy: 'Mullins et al. 2021',  pmid: '34002096',  description: 'BIP types I and II genome-wide meta-analysis' },
  cross:     { id: 'cross',     name: 'Cross-disorder',      fullName: 'Cross-Disorder Analysis',                   color: '#6B7280', variantCount: 63_300_000, significantLoci: 109, sampleSize: 727_126, latestStudy: 'PGC CDG2 2019',       pmid: '31835028',  description: 'Pleiotropic analysis across eight psychiatric disorders' },
  eating:    { id: 'eating',    name: 'Eating Disorders',     fullName: 'Eating Disorders',                          color: '#F472B6', variantCount: 10_600_000, significantLoci: 8,   sampleSize: 72_517,  latestStudy: 'Watson et al. 2019',   pmid: '31308545',  description: 'Anorexia nervosa and related phenotypes' },
  mdd:       { id: 'mdd',       name: 'Depression',           fullName: 'Major Depressive Disorder',                 color: '#3B82F6', variantCount: 179_000_000,significantLoci: 243, sampleSize: 1_200_000,latestStudy: 'Als et al. 2025',     pmid: '38300001',  description: 'Largest MDD GWAS meta-analysis to date' },
  ocd:       { id: 'ocd',       name: 'OCD/Tourette',        fullName: 'OCD & Tourette Syndrome',                   color: '#F97316', variantCount: 36_500_000, significantLoci: 4,   sampleSize: 37_358,  latestStudy: 'Arnold et al. 2025',   pmid: '38400001',  description: 'Obsessive-compulsive and tic disorders' },
  other:     { id: 'other',     name: 'Other',               fullName: 'Other Phenotypes',                          color: '#9CA3AF', variantCount: 40_900_000, significantLoci: 18,  sampleSize: 150_000, latestStudy: 'Various',              pmid: '',          description: 'Sleep, personality, and other psychiatric phenotypes' },
  ptsd:      { id: 'ptsd',      name: 'PTSD',                fullName: 'Post-Traumatic Stress Disorder',            color: '#EF4444', variantCount: 128_000_000,significantLoci: 15,  sampleSize: 1_222_882,latestStudy: 'Stein et al. 2024',   pmid: '38100001',  description: 'Multi-ancestry PTSD GWAS meta-analysis' },
  scz:       { id: 'scz',       name: 'Schizophrenia',       fullName: 'Schizophrenia',                             color: '#10B981', variantCount: 91_400_000, significantLoci: 287, sampleSize: 320_404, latestStudy: 'Trubetskoy et al. 2022',pmid:'35396580', description: 'SCZ3 genome-wide association study' },
  substance: { id: 'substance', name: 'Substance Use',       fullName: 'Substance Use Disorders',                   color: '#8B5CF6', variantCount: 214_000_000,significantLoci: 44,  sampleSize: 1_025_550,latestStudy: 'Karlsson Linnér 2024',pmid: '38200002',  description: 'Alcohol, tobacco, cannabis, and opioid use disorders' },
};

// ── Mock Manhattan data ────────────────────────────────────────────────
const CHR_LENGTHS = [249250621,243199373,198022430,191154276,180915260,171115067,159138663,146364022,141213431,135534747,135006516,133851895,115169878,107349540,102531392,90354753,81195210,78077248,59128983,63025520,48129895,51304566];

function generateMockManhattan(disorder: DisorderKey): PlotData {
  const color = DISORDERS[disorder].color;
  const dimColor = color + '66';
  const traces: any[] = [];
  let offset = 0;
  const tickVals: number[] = [];
  const tickText: string[] = [];

  for (let chr = 1; chr <= 22; chr++) {
    const len = CHR_LENGTHS[chr - 1];
    const n = 800 + Math.floor(Math.random() * 400);
    const x: number[] = [];
    const y: number[] = [];
    const text: string[] = [];
    const colors: string[] = [];

    for (let i = 0; i < n; i++) {
      const pos = Math.floor(Math.random() * len);
      // Generate p-values with realistic distribution (mostly non-significant)
      let pval: number;
      const r = Math.random();
      if (r < 0.002) pval = Math.pow(10, -(7 + Math.random() * 8));  // genome-wide significant
      else if (r < 0.01) pval = Math.pow(10, -(5 + Math.random() * 2));  // suggestive
      else pval = Math.pow(10, -(Math.random() * 4));  // background

      const logp = -Math.log10(pval);
      x.push(offset + pos);
      y.push(logp);
      text.push(`rs${10000000 + Math.floor(Math.random() * 90000000)}<br>Chr${chr}:${pos.toLocaleString()}<br>P=${pval.toExponential(2)}`);
      colors.push(pval <= 5e-8 ? '#EF4444' : (chr % 2 === 0 ? color : dimColor));
    }

    traces.push({
      type: 'scattergl', mode: 'markers',
      x, y, marker: { color: colors, size: 3, opacity: 0.7 },
      text, hoverinfo: 'text', name: `Chr ${chr}`, showlegend: false,
    });

    tickVals.push(offset + len / 2);
    tickText.push(String(chr));
    offset += len;
  }

  return {
    traces,
    layout: {
      xaxis: { tickvals: tickVals, ticktext: tickText, title: 'Chromosome', showgrid: false },
      yaxis: { title: '-log\u2081\u2080(p-value)', zeroline: false },
      shapes: [
        { type: 'line', x0: 0, x1: offset, y0: 7.3, y1: 7.3, line: { color: '#EF4444', width: 1, dash: 'dash' } },
        { type: 'line', x0: 0, x1: offset, y0: 5, y1: 5, line: { color: '#F59E0B', width: 1, dash: 'dot' } },
      ],
      hovermode: 'closest',
      plot_bgcolor: 'rgba(0,0,0,0)', paper_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#E2E8F0' },
      margin: { l: 60, r: 20, t: 40, b: 60 },
    },
  };
}

function generateMockQQ(disorder: DisorderKey): PlotData & { lambda_gc: number } {
  const n = 5000;
  const pvals: number[] = [];
  for (let i = 0; i < n; i++) {
    const r = Math.random();
    if (r < 0.005) pvals.push(Math.pow(10, -(7 + Math.random() * 6)));
    else if (r < 0.02) pvals.push(Math.pow(10, -(4 + Math.random() * 3)));
    else pvals.push(Math.pow(10, -(Math.random() * 3)));
  }
  pvals.sort((a, b) => a - b);

  const expected = pvals.map((_, i) => -Math.log10((i + 1) / (n + 1)));
  const observed = pvals.map(p => -Math.log10(p));
  const maxVal = Math.max(...expected, ...observed) + 0.5;
  const lambda_gc = 1.0 + Math.random() * 0.08;

  const color = DISORDERS[disorder].color;

  return {
    traces: [
      { type: 'scattergl', mode: 'markers', x: expected, y: observed, marker: { color, size: 3, opacity: 0.6 }, name: 'Observed', hovertemplate: 'Expected: %{x:.2f}<br>Observed: %{y:.2f}<extra></extra>' },
      { type: 'scatter', mode: 'lines', x: [0, maxVal], y: [0, maxVal], line: { color: '#EF4444', width: 1, dash: 'dash' }, name: 'Expected', showlegend: false },
    ],
    layout: {
      xaxis: { title: 'Expected -log\u2081\u2080(p)', range: [0, maxVal] },
      yaxis: { title: 'Observed -log\u2081\u2080(p)', range: [0, maxVal] },
      annotations: [{ x: 0.05, y: 0.95, xref: 'paper', yref: 'paper', text: `\u03bb<sub>GC</sub> = ${lambda_gc.toFixed(3)}`, showarrow: false, font: { size: 14, color: '#E2E8F0' } }],
      plot_bgcolor: 'rgba(0,0,0,0)', paper_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#E2E8F0' },
      margin: { l: 60, r: 20, t: 40, b: 60 },
    },
    lambda_gc,
  };
}

function generateMockVariants(disorder: DisorderKey, n: number = 50): VariantRecord[] {
  const genes = ['CACNA1C','DRD2','GRIN2A','TCF4','NRGN','TRIM26','ZSCAN31','RERE','PLCL1','SORCS3','RBFOX1','LSAMP','PCLO','GRM8','NEGR1','CADM2','ESR1','FOXP2','CNTNAP2','NRXN1'];
  const variants: VariantRecord[] = [];
  for (let i = 0; i < n; i++) {
    const chr = Math.ceil(Math.random() * 22);
    const bp = Math.floor(Math.random() * CHR_LENGTHS[chr - 1]);
    const pval = Math.pow(10, -(Math.random() * 12));
    variants.push({
      snp: `rs${10000000 + Math.floor(Math.random() * 90000000)}`,
      chr, bp,
      a1: ['A','T','C','G'][Math.floor(Math.random()*4)],
      a2: ['A','T','C','G'][Math.floor(Math.random()*4)],
      effect: (Math.random() - 0.5) * 0.4,
      se: 0.01 + Math.random() * 0.05,
      pval,
      maf: 0.01 + Math.random() * 0.49,
      nearest_gene: genes[Math.floor(Math.random() * genes.length)],
    });
  }
  return variants.sort((a, b) => a.pval - b.pval);
}

function generateMockHeatmap(): PlotData {
  const keys = Object.keys(DISORDERS) as DisorderKey[];
  const names = keys.map(k => DISORDERS[k].name);
  const n = keys.length;
  const z: number[][] = [];
  for (let i = 0; i < n; i++) {
    const row: number[] = [];
    for (let j = 0; j < n; j++) {
      if (i === j) row.push(1);
      else if (j < i) row.push(z[j][i]);
      else row.push(-0.2 + Math.random() * 0.8);
    }
    z.push(row);
  }
  return {
    traces: [{
      type: 'heatmap', z, x: names, y: names,
      colorscale: [[0,'#1E293B'],[0.5,'#334155'],[1,'#3B82F6']],
      hovertemplate: '%{x} vs %{y}: r=%{z:.3f}<extra></extra>',
    }],
    layout: {
      xaxis: { tickangle: -45 },
      yaxis: { autorange: 'reversed' as any },
      plot_bgcolor: 'rgba(0,0,0,0)', paper_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#E2E8F0', size: 10 },
      margin: { l: 120, r: 20, t: 20, b: 120 },
    },
  };
}

// ── API client ──────────────────────────────────────────────────────────
export async function fetchDatasets() {
  if (USE_MOCK) return Object.values(DISORDERS);
  const res = await fetch(`${API_BASE}/api/datasets`);
  return res.json();
}

export async function fetchManhattan(disorder: DisorderKey): Promise<PlotData> {
  if (USE_MOCK) return generateMockManhattan(disorder);
  const res = await fetch(`${API_BASE}/api/plots/manhattan/${disorder}`);
  return res.json();
}

export async function fetchQQ(disorder: DisorderKey): Promise<PlotData & { lambda_gc?: number }> {
  if (USE_MOCK) return generateMockQQ(disorder);
  const res = await fetch(`${API_BASE}/api/plots/qq/${disorder}`);
  return res.json();
}

export async function fetchVariants(disorder: DisorderKey, n = 50): Promise<VariantRecord[]> {
  if (USE_MOCK) return generateMockVariants(disorder, n);
  const res = await fetch(`${API_BASE}/api/variants/search?disorder=${disorder}&limit=${n}`);
  const data = await res.json();
  return data.results || [];
}

export async function fetchHeatmap(): Promise<PlotData> {
  if (USE_MOCK) return generateMockHeatmap();
  const res = await fetch(`${API_BASE}/api/plots/heatmap`);
  return res.json();
}

export async function searchVariant(snp: string) {
  if (USE_MOCK) {
    const results: any[] = [];
    for (const d of Object.keys(DISORDERS) as DisorderKey[]) {
      if (Math.random() > 0.4) {
        const v = generateMockVariants(d, 1)[0];
        v.snp = snp;
        results.push({ ...v, disorder: d });
      }
    }
    return { query: snp, results, count: results.length };
  }
  const res = await fetch(`${API_BASE}/api/variants/search?snp=${snp}`);
  return res.json();
}
