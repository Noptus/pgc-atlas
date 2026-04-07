import { Link } from 'react-router-dom';
import { Disorder } from '../types';
import { formatNumber } from '../utils/format';

interface Props {
  disorder: Disorder;
}

export default function DisorderCard({ disorder }: Props) {
  return (
    <Link
      to={`/disorder/${disorder.id}`}
      className="group relative bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-600 transition-all hover:shadow-lg hover:shadow-black/20 overflow-hidden"
    >
      {/* Accent gradient */}
      <div
        className="absolute top-0 left-0 right-0 h-1 opacity-60 group-hover:opacity-100 transition"
        style={{ background: `linear-gradient(90deg, ${disorder.color}, transparent)` }}
      />

      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-base" style={{ color: disorder.color }}>
            {disorder.name}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">{disorder.fullName}</p>
        </div>
        <span
          className="w-3 h-3 rounded-full mt-1 flex-shrink-0"
          style={{ backgroundColor: disorder.color }}
        />
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <div className="text-lg font-bold">{formatNumber(disorder.variantCount)}</div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Variants</div>
        </div>
        <div>
          <div className="text-lg font-bold">{disorder.significantLoci}</div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">GW-Sig Loci</div>
        </div>
        <div>
          <div className="text-sm font-medium">{formatNumber(disorder.sampleSize)}</div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Samples</div>
        </div>
        <div>
          <div className="text-sm font-medium truncate">{disorder.latestStudy.split(' ')[0]}</div>
          <div className="text-[10px] text-slate-500 uppercase tracking-wider">Latest</div>
        </div>
      </div>

      <p className="text-xs text-slate-500 line-clamp-2">{disorder.description}</p>
    </Link>
  );
}
