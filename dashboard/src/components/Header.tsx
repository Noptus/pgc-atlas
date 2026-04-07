import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Header() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query.trim())}`);
  };

  return (
    <header className="h-14 bg-slate-900/80 backdrop-blur border-b border-slate-800 flex items-center px-6 gap-4">
      <form onSubmit={handleSearch} className="flex-1 max-w-xl">
        <input
          type="text"
          placeholder="Search variants (e.g. rs1234567, CACNA1C)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition"
        />
      </form>
      <a
        href="https://huggingface.co/collections/OpenMed/pgc-psychiatric-gwas-summary-statistics"
        target="_blank"
        rel="noreferrer"
        className="text-xs text-slate-500 hover:text-blue-400 transition"
      >
        HuggingFace ↗
      </a>
      <a
        href="https://github.com/Noptus/pgc-atlas"
        target="_blank"
        rel="noreferrer"
        className="text-xs text-slate-500 hover:text-blue-400 transition"
      >
        GitHub ↗
      </a>
    </header>
  );
}
