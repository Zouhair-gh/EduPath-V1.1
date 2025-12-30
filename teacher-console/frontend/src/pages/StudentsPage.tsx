import { Navbar } from '@/components/Layout/Navbar';
import { Sidebar } from '@/components/Layout/Sidebar';
import { useStudents } from '@/hooks/useStudents';
import { StudentsTable } from '@/components/Student/StudentsTable';
import { useExports } from '@/hooks/useExports';

export default function StudentsPage() {
  const courseId = 1;
  const { data, isLoading, error } = useStudents(courseId);
  const { exportStudents } = useExports();
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-blue-700 flex items-center gap-2">
              <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
              Étudiants
            </h1>
            <button className="px-4 py-2 border rounded bg-blue-600 text-white hover:bg-blue-700 transition" onClick={() => exportStudents(courseId)}>Exporter CSV</button>
          </div>
          <section className="bg-white p-6 rounded shadow">
            <StudentsTable data={data} loading={isLoading} error={error ? (error as any).message : undefined} courseId={courseId} />
          </section>
        </main>
      </div>
    </div>
  );
}
