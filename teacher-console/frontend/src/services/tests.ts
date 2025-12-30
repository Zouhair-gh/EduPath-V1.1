import { api } from '@/services/api';

export async function fetchRecentTests(limit = 10) {
  // This endpoint does not exist yet, will need to be implemented in backend
  const res = await api.get(`/tests/recent?limit=${limit}`);
  return res.data;
}
