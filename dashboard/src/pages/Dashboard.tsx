import DisorderCard from '../components/DisorderCard';
import CrossTraitHeatmap from '../components/CrossTraitHeatmap';
import { DISORDERS } from '../api/client';
import { DisorderKey } from '../types';
import { formatNumber } from '../utils/format';

const keys = Object.keys(DISORDERS) as DisorderKey[];
const totalVariants = Object.values(DISORDERS).reduce((sum, d) => sum + d.variantCount, 0);

export default function Dashboard() {
  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero */}
      <section className="text-center py-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          PGC GWAS Atlas
        </h1>
        <p className="text-slate-400 mt-2 text-lg">
          Interactive explorer for Psychiatric Genomics Consortium summary statistics
        </p>
        <div className="flex items-center justify-center gap-8 mt-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400">{formatNumber(totalVariants)}</div>
            <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">Total Variants</div>
          </div>
          <div className="w-px h-10 bg-slate-700" />
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400">12</div>
            <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">Disorders</div>
          </div>
          <div className="w-px h-10 bg-slate-700" />
          <div className="text-center">
            <div className="text-3xl font-bold text-pink-400">{Object.values(DISORDERS).reduce((s, d) => s + d.significantLoci, 0)}</div>
            <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">GW-Sig Loci</div>
          </div>
        </div>
      </section>

      {/* Disorder grid */}
      <section>
        <h2 className="text-lg font-semibold mb-4 text-slate-300">Psychiatric Disorders</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {keys.map((key) => (
            <DisorderCard key={key} disorder={DISORDERS[key]} />
          ))}
        </div>
      </section>

      {/* Cross-trait heatmap */}
      <section>
        <CrossTraitHeatmap height={480} />
      </section>

      {/* Data source */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-sm font-semibold mb-2">Data Source</h2>
        <p className="text-xs text-slate-400 leading-relaxed">
          Summary statistics from the{' '}
          <a href="https://pgc.unc.edu" target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">
            Psychiatric Genomics Consortium (PGC)
          </a>
          , hosted on HuggingFace by{' '}
          <a href="https://huggingface.co/OpenMed" target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">
            OpenMed
          </a>
          . This collection contains approximately{' '}
          <span className="font-semibold text-slate-200">{formatNumber(totalVariants)}</span>{' '}
          genome-wide association study results across 12 psychiatric conditions.
          Licensed under CC-BY-4.0.
        </p>
      </section>
    </div>
  );
}
