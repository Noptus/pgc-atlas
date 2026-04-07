import Plot from 'react-plotly.js';
import { useHeatmap } from '../hooks/usePlotData';

interface Props {
  height?: number;
}

export default function CrossTraitHeatmap({ height = 500 }: Props) {
  const { data, isLoading } = useHeatmap();

  if (isLoading || !data) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 animate-pulse" style={{ height }}>
        <div className="h-4 w-48 bg-slate-800 rounded mb-4" />
        <div className="h-full bg-slate-800/50 rounded" />
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800">
        <h3 className="text-sm font-semibold">Cross-Disorder Genetic Correlation</h3>
        <p className="text-[10px] text-slate-500 mt-0.5">Effect-size correlation between shared variants</p>
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
