import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DisorderView from './pages/DisorderView';
import CompareView from './pages/CompareView';
import SearchResults from './pages/SearchResults';
import About from './pages/About';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="disorder/:disorderId" element={<DisorderView />} />
        <Route path="compare" element={<CompareView />} />
        <Route path="search" element={<SearchResults />} />
        <Route path="about" element={<About />} />
      </Route>
    </Routes>
  );
}
