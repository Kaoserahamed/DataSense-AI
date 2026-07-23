import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import ProjectsPage from './pages/ProjectsPage'
import DatasetsPage from './pages/DatasetsPage'
import DatasetDetailPage from './pages/DatasetDetailPage'
import DataChatPage from './pages/DataChatPage'
import VisualizationsPage from './pages/VisualizationsPage'
import Layout from './layouts/Layout'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/:projectId/datasets" element={<DatasetsPage />} />
        <Route path="/datasets/:datasetId" element={<DatasetDetailPage />} />
        <Route path="/datasets/:datasetId/chat" element={<DataChatPage />} />
        <Route path="/datasets/:datasetId/visualizations" element={<VisualizationsPage />} />
      </Route>
      
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  )
}

export default App
