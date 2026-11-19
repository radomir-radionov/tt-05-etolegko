import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { CreateCampaignPage } from './pages/CreateCampaignPage'
import { EditorPage } from './pages/EditorPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CreateCampaignPage />} />
        <Route path="/campaigns/:id/editor" element={<EditorPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}