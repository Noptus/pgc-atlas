import { NavLink } from 'react-router-dom';
import { DISORDERS } from '../api/client';
import { DisorderKey } from '../types';
import { formatNumber } from '../utils/format';

const disorderKeys = Object.keys(DISORDERS) as DisorderKey[];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
      <NavLink to="/" className="px-5 py-5 border-b border-slate-800 hover:bg-slate-800/50 transition">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm font-bold">P</div>
          <div>
            <div className="font-bold text-sm tracking-wide">PGC Atlas</div>
            <div className="text-[10px] text-slate-500 tracking-widest uppercase">GWAS Explorer</div>
          </div>
        </div>
      </NavLink>

      <nav className="flex-1 overflow-y-auto py-2">
        <div className="px-4 py-2 text-[10px] font-semibold text-slate-500 uppercase tracking-widest">Disorders</div>
        {disorderKeys.map((key) => {
          const d = DISORDERS[key];
          return (
            <NavLink
              key={key}
              to={`/disorder/${key}`}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 text-sm transition-all hover:bg-slate-800/50 ${isActive ? 'bg-slate-800 border-r-2' : ''}`
              }
              style={({ isActive }) => isActive ? { borderRightColor: d.color } : {}}
            >
              <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: d.color }} />
              <span className="flex-1 truncate">{d.name}</span>
              <span className="text-[10px] text-slate-500">{formatNumber(d.variantCount)}</span>
            </NavLink>
          );
        })}

        <div className="px-4 pt-4 pb-2 text-[10px] font-semibold text-slate-500 uppercase tracking-widest">Tools</div>
        <NavLink to="/compare" className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 text-sm transition hover:bg-slate-800/50 ${isActive ? 'bg-slate-800' : ''}`}>
          <span className="text-slate-400">⇌</span> Compare Disorders
        </NavLink>
        <NavLink to="/about" className={({ isActive }) => `flex items-center gap-3 px-4 py-2.5 text-sm transition hover:bg-slate-800/50 ${isActive ? 'bg-slate-800' : ''}`}>
          <span className="text-slate-400">ℹ</span> About
        </NavLink>
      </nav>

      <div className="p-4 border-t border-slate-800 text-[10px] text-slate-600">
        Data: PGC via <a href="https://huggingface.co/collections/OpenMed/pgc-psychiatric-gwas-summary-statistics" className="text-blue-400 hover:underline" target="_blank" rel="noreferrer">OpenMed/HF</a>
      </div>
    </aside>
  );
}
