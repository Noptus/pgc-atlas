import { useSearchParams, Link } from 'react-router-dom';
import { useSearch } from '../hooks/useDataset';
import { DISORDERS } from '../api/client';
import { DisorderKey } from '../types';
import { formatPValue } from '../utils/format';

export default function SearchResults() {
  const [params] = useSearchParams();
  const query = params.get('q') || '';
  const { data, isLoading } = useSearch(query);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold">
        Search: <span className="text-blue-400 font-mono">{query}</span>
      </h1>

      {isLoading && (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => <div key={i} className="h-16 bg-slate-900 rounded-xl animate-pulse" />)}
        </div>
      )}

      {data && data.count === 0 && (
        <div className="text-center py-16 text-slate-500">No variants found matching "{query}"</div>
      )}

      {data && data.results && data.results.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-800 text-sm text-slate-400">
            {data.count} result{data.count > 1 ? 's' : ''} across disorders
          </div>
          <div className="divide-y divide-slate-800/50">
            {data.results.map((r: any, i: number) => {
              const disorder = DISORDERS[r.disorder as DisorderKey];
              return (
                <Link
                  key={i}
                  to={`/disorder/${r.disorder}`}
                  className="flex items-center gap-4 px-4 py-3 hover:bg-slate-800/30 transition"
                >
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: disorder?.color || '#6B7280' }} />
                  <div className="flex-1">
                    <span className="font-mono text-sm">{r.snp}</span>
                    <span className="text-slate-500 text-xs ml-3">Chr{r.chr}:{r.bp?.toLocaleString()}</span>
                  </div>
                  <span className="text-xs" style={{ color: disorder?.color }}>{disorder?.name}</span>
                  <span className="text-xs text-slate-500 font-mono">{formatPValue(r.pval)}</span>
                  <span className="text-xs text-slate-500">β={r.effect?.toFixed(3)}</span>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
