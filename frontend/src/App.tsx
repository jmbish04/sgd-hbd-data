import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Catalog from './pages/Catalog';
import DatasetView from './pages/DatasetView';
import SQLRunner from './pages/SQLRunner';
import RagChat from './pages/RagChat';
import HealthPage from './pages/Health';
import DatasetFlow from './pages/DatasetFlow';
import { useDarkMode } from '@/hooks/use-dark-mode';

function App() {
  // Enable dark mode by default
  useDarkMode({ defaultValue: true });

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="catalog" element={<Catalog />} />
          <Route path="catalog/:datasetId" element={<DatasetView />} />
          <Route path="sql" element={<SQLRunner />} />
          <Route path="chat" element={<RagChat />} />
          <Route path="health" element={<HealthPage />} />
          <Route path="flow" element={<DatasetFlow />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
