
import React, { useEffect, useState } from 'react';
import { fetchRecentTests } from '@/services/tests';
import { RecentTest } from '@/types';

export default function RecentTests() {
  const [tests, setTests] = useState<RecentTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRecentTests()
      .then((data) => {
        setTests(data);
        setLoading(false);
      })
      .catch((err) => {
        setError('Failed to load recent tests');
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4 text-blue-700 flex items-center gap-2">
        <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 17v-2a4 4 0 014-4h4m0 0V7a4 4 0 00-4-4H7a4 4 0 00-4 4v10a4 4 0 004 4h4a4 4 0 004-4z" /></svg>
        Recent Tests
      </h2>
      {loading && <div className="text-gray-500">Loading...</div>}
      {error && <div className="text-red-500">{error}</div>}
      {!loading && !error && tests.length === 0 && (
        <div className="text-gray-500">No recent tests to display.</div>
      )}
      {!loading && !error && tests.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border rounded shadow">
            <thead>
              <tr className="bg-blue-50">
                <th className="py-2 px-4 text-left">Student</th>
                <th className="py-2 px-4 text-left">Email</th>
                <th className="py-2 px-4 text-left">Course</th>
                <th className="py-2 px-4 text-left">Author</th>
                <th className="py-2 px-4 text-left">Content</th>
                <th className="py-2 px-4 text-left">Date</th>
              </tr>
            </thead>
            <tbody>
              {tests.map((test) => (
                <tr key={test.id} className="border-b hover:bg-blue-50 transition">
                  <td className="py-2 px-4 font-semibold text-blue-800">{test.name || test.student_id}</td>
                  <td className="py-2 px-4 text-blue-600">{test.email || test.student_id}</td>
                  <td className="py-2 px-4">{test.course_id}</td>
                  <td className="py-2 px-4">{test.author}</td>
                  <td className="py-2 px-4 max-w-xs truncate" title={test.content}>{test.content}</td>
                  <td className="py-2 px-4 text-xs text-gray-500">{new Date(test.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
