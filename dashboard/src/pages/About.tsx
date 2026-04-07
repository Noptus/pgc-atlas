export default function About() {
  return (
    <div className="max-w-3xl mx-auto space-y-8 py-4">
      <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
        About PGC GWAS Atlas
      </h1>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-slate-200">What is this?</h2>
        <p className="text-sm text-slate-400 leading-relaxed">
          PGC GWAS Atlas is an interactive visual platform for exploring genome-wide association study (GWAS) 
          summary statistics from the Psychiatric Genomics Consortium (PGC). The collection contains approximately 
          1 billion rows of data across 12 major psychiatric disorders, hosted on HuggingFace by OpenMed.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-slate-200">Visualizations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-slate-400">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="font-medium text-slate-200 mb-1">Manhattan Plot</h3>
            <p>Genome-wide view of association signals. Each point is a variant; y-axis shows -log10(p-value). Red dashed line = genome-wide significance (5x10^-8).</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="font-medium text-slate-200 mb-1">QQ Plot</h3>
            <p>Quantile-quantile plot comparing observed vs expected p-value distribution. Deviation from diagonal indicates true associations or systematic bias.</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="font-medium text-slate-200 mb-1">Miami Plot</h3>
            <p>Bidirectional Manhattan comparing two disorders. Top panel = disorder 1, bottom panel (inverted) = disorder 2. Shared loci appear at same x position.</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <h3 className="font-medium text-slate-200 mb-1">Cross-Trait Heatmap</h3>
            <p>Genetic correlation matrix showing effect-size concordance between all disorder pairs. Identifies shared genetic architecture.</p>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-slate-200">Data Source</h2>
        <p className="text-sm text-slate-400 leading-relaxed">
          All summary statistics come from the{' '}
          <a href="https://pgc.unc.edu" className="text-blue-400 hover:underline" target="_blank" rel="noreferrer">Psychiatric Genomics Consortium</a>,
          hosted on{' '}
          <a href="https://huggingface.co/collections/OpenMed/pgc-psychiatric-gwas-summary-statistics" className="text-blue-400 hover:underline" target="_blank" rel="noreferrer">HuggingFace by OpenMed</a>.
          Data is licensed under CC-BY-4.0.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-slate-200">Technology</h2>
        <div className="flex flex-wrap gap-2">
          {['React', 'TypeScript', 'Tailwind CSS', 'Plotly.js', 'FastAPI', 'HuggingFace Datasets', 'Python', 'Pandas'].map(t => (
            <span key={t} className="px-3 py-1 bg-slate-800 border border-slate-700 rounded-full text-xs text-slate-300">{t}</span>
          ))}
        </div>
      </section>
    </div>
  );
}
