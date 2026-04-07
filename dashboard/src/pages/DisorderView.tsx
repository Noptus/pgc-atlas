import { useParams } from 'react-router-dom';
import ManhattanPlot from '../components/ManhattanPlot';
import QQPlot from '../components/QQPlot';
import VariantTable from '../components/VariantTable';
import StatsPanel from '../components/StatsPanel';
import { DISORDERS } from '../api/client';
import { DisorderKey } from '../types';

export default function DisorderView() {
  const { disorderId } = useParams<{ disorderId: string }>();
  const key = disorderId as DisorderKey;
  const disorder = DISORDERS[key];

  if (!disorder) {
    return <div className="text-center py-20 text-slate-400">Disorder not found</div>;
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <span className="w-4 h-4 rounded-full" style={{ backgroundColor: disorder.color }} />
        <div>
          <h1 className="text-2xl font-bold" style={{ color: disorder.color }}>{disorder.name}</h1>
          <p className="text-sm text-slate-400">{disorder.fullName}</p>
        </div>
      </div>

      {/* Plots row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ManhattanPlot disorder={key} height={340} />
        </div>
        <div>
          <QQPlot disorder={key} height={340} />
        </div>
      </div>

      {/* Stats + Table */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <StatsPanel disorder={disorder} />
        </div>
        <div className="lg:col-span-3">
          <VariantTable disorder={key} />
        </div>
      </div>
    </div>
  );
}
