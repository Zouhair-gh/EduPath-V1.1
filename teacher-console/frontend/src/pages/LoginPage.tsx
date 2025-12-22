import { useState } from 'react';
import { api } from '@/services/api';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const login = async () => {
    try {
      setLoading(true);
      setError(null);
      const { data } = await api.post('/auth/login', { user: { id: 1, role: 'teacher', courses: [1] } });
      localStorage.setItem('token', data.token);
      navigate('/');
    } catch (e: any) {
      setError('Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-6 rounded shadow w-full max-w-sm">
        <h1 className="text-xl font-semibold mb-4">Connexion</h1>
        <button onClick={login} disabled={loading} className="w-full bg-blue-600 text-white py-2 rounded">
          {loading ? 'Connexion...' : 'Se connecter (dev)'}
        </button>
        {error && <div className="text-red-600 mt-3">{error}</div>}
      </div>
    </div>
  );
}
