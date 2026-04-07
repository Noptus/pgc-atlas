import { Disorder } from '../types';
import { formatNumber } from '../utils/format';

interface Props {
  disorder: Disorder;
}

export default function StatsPanel({ disorder }: Props) {
  const stats = [
    { label: 'Total Variants', value: formatNumber(disorder.variantCount) },
    { label: 'GW-Significant Loci', value: disorder.significantLoci.toString() },
    { label: 'Sample Size', value: formatNumber(disorder.sampleSize) },
    { label: 'Latest Study', value: disorder.latestStudy },
    { label: 'PMID', value: disorder.pmid || 'N/A' },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800">
        <h3 className="text-sm font-semibold" style={{ color: disorder.color }}>{disorder.name}</h3>
        <p className="text-[10px] text-slate-500 mt-0.5">{disorder.fullName}</p>
      </div>
      <div className="divide-y divide-slate-800/50">
        {stats.map(s => (
          <div key={s.label} className="px-4 py-3 flex justify-between items-center">
            <span className="text-xs text-slate-400">{s.label}</span>
            <span className="text-sm font-medium">{s.value}</span>
          </div>
        ))}
      </div>
      <div className="px-4 py-3 border-t border-slate-800">
        <p className="text-xs text-slate-500">{disorder.description}</p>
      </div>
    </div>
  );
}
