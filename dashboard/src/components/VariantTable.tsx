import { useState, useMemo } from 'react';
import { useVariants } from '../hooks/useDataset';
import { DisorderKey, VariantRecord } from '../types';
import { formatPValue } from '../utils/format';

interface Props {
  disorder: DisorderKey;
}

type SortKey = keyof VariantRecord;

export default function VariantTable({ disorder }: Props) {
  const { data: variants, isLoading } = useVariants(disorder, 100);
  const [sortKey, setSortKey] = useState<SortKey>('pval');
  const [sortAsc, setSortAsc] = useState(true);

  const sorted = useMemo(() => {
    if (!variants) return [];
    return [...variants].sort((a, b) => {
      const av = a[sortKey] ?? 0;
      const bv = b[sortKey] ?? 0;
      return sortAsc ? (av < bv ? -1 : 1) : (av > bv ? -1 : 1);
    });
  }, [variants, sortKey, sortAsc]);

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortAsc(!sortAsc);
    else { setSortKey(key); setSortAsc(true); }
  };

  const cols: { key: SortKey; label: string; fmt?: (v: any) => string }[] = [
    { key: 'snp', label: 'SNP' },
    { key: 'chr', label: 'Chr' },
    { key: 'bp', label: 'Position', fmt: (v: number) => v?.toLocaleString() },
    { key: 'a1', label: 'A1' },
    { key: 'a2', label: 'A2' },
    { key: 'effect', label: 'Effect', fmt: (v: number) => v?.toFixed(4) },
    { key: 'se', label: 'SE', fmt: (v: number) => v?.toFixed(4) },
    { key: 'pval', label: 'P-value', fmt: formatPValue },
    { key: 'maf', label: 'MAF', fmt: (v: number) => v?.toFixed(3) },
    { key: 'nearest_gene', label: 'Gene' },
  ];

  if (isLoading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 animate-pulse">
        <div className="h-4 w-32 bg-slate-800 rounded mb-4" />
        {[...Array(5)].map((_, i) => <div key={i} className="h-8 bg-slate-800/50 rounded mb-2" />)}
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <h3 className="text-sm font-semibold">Top Variants</h3>
        <span className="text-[10px] text-slate-500">{sorted.length} variants</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-slate-800">
              {cols.map(c => (
                <th
                  key={String(c.key)}
                  onClick={() => toggleSort(c.key)}
                  className="px-3 py-2.5 text-left font-medium text-slate-400 cursor-pointer hover:text-slate-200 transition whitespace-nowrap"
                >
                  {c.label} {sortKey === c.key ? (sortAsc ? '↑' : '↓') : ''}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.slice(0, 50).map((v, i) => (
              <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition">
                {cols.map(c => (
                  <td key={String(c.key)} className="px-3 py-2 whitespace-nowrap font-mono">
                    {c.fmt ? c.fmt(v[c.key]) : (v[c.key] ?? '-')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
