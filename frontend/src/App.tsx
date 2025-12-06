import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Catalog from './pages/Catalog';
import DatasetView from './pages/DatasetView';
import SQLRunner from './pages/SQLRunner';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="catalog" element={<Catalog />} />
          <Route path="catalog/:datasetId" element={<DatasetView />} />
          <Route path="sql" element={<SQLRunner />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
