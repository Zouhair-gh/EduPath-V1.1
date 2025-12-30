
import { Link } from 'react-router-dom';
// Import RecentTests for sidebar preview or later use
// import RecentTests from '../RecentTests';

export function Sidebar() {
  return (
    <div className="bg-gray-100 w-64 p-4 space-y-2">
      <Link to="/" className="block p-2 rounded hover:bg-gray-200">Dashboard</Link>
      <Link to="/students" className="block p-2 rounded hover:bg-gray-200">Étudiants</Link>
      <Link to="/alerts" className="block p-2 rounded hover:bg-gray-200">Alertes</Link>
      <Link to="/recent-tests" className="block p-2 rounded hover:bg-gray-200">Recent tests</Link>
    </div>
  );
}