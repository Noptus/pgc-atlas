import Plot from 'react-plotly.js';
import { useManhattan } from '../hooks/usePlotData';
import { DisorderKey } from '../types';

interface Props {
  disorder: DisorderKey;
  height?: number;
}

export default function ManhattanPlot({ disorder, height = 350 }: Props) {
  const { data, isLoading, error } = useManhattan(disorder);

  if (isLoading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 animate-pulse" style={{ height }}>
        <div className="h-4 w-40 bg-slate-800 rounded mb-4" />
        <div className="h-full bg-slate-800/50 rounded" />
      </div>
    );
  }
  if (error || !data) return <div className="text-red-400 text-sm">Failed to load Manhattan plot</div>;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <h3 className="text-sm font-semibold">Manhattan Plot</h3>
        <span className="text-[10px] text-slate-500">Genome-wide significance: p &lt; 5×10⁻⁸</span>
      </div>
      <Plot
        data={data.traces as any}
        layout={{
          ...data.layout,
          height,
          autosize: true,
        } as any}
        config={{ responsive: true, displayModeBar: false }}
        className="w-full"
        useResizeHandler
        style={{ width: '100%' }}
      />
    </div>
  );
}
