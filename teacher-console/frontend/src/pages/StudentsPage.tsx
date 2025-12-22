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
        <div className="flex-1 p-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold">Étudiants</h1>
            <button className="px-3 py-1 border rounded" onClick={() => exportStudents(courseId)}>Exporter CSV</button>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <StudentsTable data={data} loading={isLoading} error={error ? (error as any).message : undefined} courseId={courseId} />
          </div>
        </div>
      </div>
    </div>
  );
}
