import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:4000/api',
  timeout: 8000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  (config as any).metadata = { start: Date.now() };
  return config;
});

api.interceptors.response.use(
  (res) => {
    const ms = Date.now() - ((res.config as any).metadata?.start || Date.now());
    console.log(`[API] ${res.config.method?.toUpperCase()} ${res.config.url} -> ${res.status} (${ms}ms)`);
    return res;
  },
  (err) => {
    const cfg: any = err.config || {};
    const ms = Date.now() - (cfg.metadata?.start || Date.now());
    const status = err.response?.status;
    console.warn(`[API ERR] ${cfg.method?.toUpperCase()} ${cfg.url} -> ${status || 'network'} (${ms}ms): ${err.message}`);
    if (status === 401 || status === 403) {
      // Optionally redirect to login
      // window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);