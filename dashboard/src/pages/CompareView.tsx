import { useState } from 'react';
import Plot from 'react-plotly.js';
import { DISORDERS, fetchManhattan } from '../api/client';
import { DisorderKey, PlotData } from '../types';
import CrossTraitHeatmap from '../components/CrossTraitHeatmap';

const keys = Object.keys(DISORDERS) as DisorderKey[];

export default function CompareView() {
  const [d1, setD1] = useState<DisorderKey>('scz');
  const [d2, setD2] = useState<DisorderKey>('bipolar');
  const [miamiData, setMiamiData] = useState<PlotData | null>(null);
  const [loading, setLoading] = useState(false);

  const generateMiami = async () => {
    setLoading(true);
    try {
      const [m1, m2] = await Promise.all([fetchManhattan(d1), fetchManhattan(d2)]);
      // Simple Miami: flip the second dataset's y values
      const topTraces = m1.traces.map((t: any) => ({ ...t, name: DISORDERS[d1].name }));
      const bottomTraces = m2.traces.map((t: any) => ({
        ...t,
        y: (t.y as number[]).map((v: number) => -v),
        name: DISORDERS[d2].name,
        marker: { ...t.marker, color: typeof t.marker.color === 'string' ? DISORDERS[d2].color : (t.marker.color as string[]).map(() => DISORDERS[d2].color + '99') },
      }));
      const maxY = Math.max(...m1.traces.flatMap((t: any) => t.y as number[]), ...m2.traces.flatMap((t: any) => t.y as number[])) + 1;
      setMiamiData({
        traces: [...topTraces, ...bottomTraces],
        layout: {
          ...m1.layout,
          yaxis: {
            ...m1.layout.yaxis,
            title: `\u2191 ${DISORDERS[d1].name}  |  \u2193 ${DISORDERS[d2].name}`,
            range: [-maxY, maxY],
            zeroline: true,
            zerolinecolor: '#475569',
          },
          shapes: [
            { type: 'line' as any, x0: 0, x1: 3e9, y0: 7.3, y1: 7.3, line: { color: '#EF4444', width: 1, dash: 'dash' as any } },
            { type: 'line' as any, x0: 0, x1: 3e9, y0: -7.3, y1: -7.3, line: { color: '#EF4444', width: 1, dash: 'dash' as any } },
          ],
        },
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold">Compare Disorders</h1>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <div className="flex items-end gap-4 flex-wrap">
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Disorder 1</label>
            <select
              value={d1}
              onChange={(e) => setD1(e.target.value as DisorderKey)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500/50"
            >
              {keys.map(k => <option key={k} value={k}>{DISORDERS[k].name}</option>)}
            </select>
          </div>
          <span className="text-slate-600 text-xl pb-2">vs</span>
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Disorder 2</label>
            <select
              value={d2}
              onChange={(e) => setD2(e.target.value as DisorderKey)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500/50"
            >
              {keys.map(k => <option key={k} value={k}>{DISORDERS[k].name}</option>)}
            </select>
          </div>
          <button
            onClick={generateMiami}
            disabled={loading || d1 === d2}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white px-5 py-2 rounded-lg text-sm font-medium transition"
          >
            {loading ? 'Generating...' : 'Generate Miami Plot'}
          </button>
        </div>
      </div>

      {miamiData && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-800">
            <h3 className="text-sm font-semibold">
              Miami Plot: <span style={{ color: DISORDERS[d1].color }}>{DISORDERS[d1].name}</span> vs <span style={{ color: DISORDERS[d2].color }}>{DISORDERS[d2].name}</span>
            </h3>
          </div>
          <Plot
            data={miamiData.traces as any}
            layout={{ ...miamiData.layout, height: 450, autosize: true } as any}
            config={{ responsive: true, displayModeBar: false }}
            className="w-full"
            useResizeHandler
            style={{ width: '100%' }}
          />
        </div>
      )}

      <CrossTraitHeatmap height={450} />
    </div>
  );
}
