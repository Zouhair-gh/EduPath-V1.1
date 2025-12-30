import { BrowserRouter, Routes, Route } from 'react-router-dom';

import DashboardPage from '@/pages/DashboardPage';
import StudentsPage from '@/pages/StudentsPage';
import AlertsPage from '@/pages/AlertsPage';
import LoginPage from '@/pages/LoginPage';
import RecentTestsPage from '@/pages/RecentTestsPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/students" element={<StudentsPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/recent-tests" element={<RecentTestsPage />} />
      </Routes>
    </BrowserRouter>
  );
}