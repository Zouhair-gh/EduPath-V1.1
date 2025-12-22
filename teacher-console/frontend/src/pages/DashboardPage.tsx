import { Navbar } from '@/components/Layout/Navbar';
import { Sidebar } from '@/components/Layout/Sidebar';
import { ClassOverview } from '@/components/Dashboard/ClassOverview';
import { useClassDetails } from '@/hooks/useClassDetails';
import { StatsCards } from '@/components/Dashboard/StatsCards';
import { SeveritySummary } from '@/components/Dashboard/SeveritySummary';
import { TopStudents } from '@/components/Dashboard/TopStudents';
import { Trends } from '@/components/Dashboard/Trends';
import { RecentAlerts } from '@/components/Dashboard/RecentAlerts';
import { ProfileDistribution } from '@/components/Dashboard/ProfileDistribution';
import { CourseSelector } from '@/components/Dashboard/CourseSelector';
import { ClassesGrid } from '@/components/Dashboard/ClassesGrid';
import { useEffect, useState } from 'react';

export default function DashboardPage() {
  const [courseId, setCourseId] = useState<number>(() => {
    const saved = localStorage.getItem('courseId');
    return saved ? Number(saved) : 1;
  });
  useEffect(() => { localStorage.setItem('courseId', String(courseId)); }, [courseId]);
  const { data: details, isLoading } = useClassDetails(courseId);
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <div className="flex-1 p-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold">Vue d'ensemble de la classe</h1>
            <CourseSelector value={courseId} onChange={setCourseId} />
          </div>
          <div className="mb-6">
            <ClassesGrid onSelect={setCourseId} />
          </div>
          <ClassOverview courseId={courseId} />

          <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2 space-y-4">
              {isLoading || !details ? (
                <div className="bg-white p-4 rounded shadow">Chargement…</div>
              ) : (
                <>
                  <StatsCards students={details.totals.students} avgEng={details.totals.averageEngagement} avgSuc={details.totals.averageSuccessRate} />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <TopStudents items={details.topStudents} />
                    <Trends ma7={details.trends.engagementMA7} ma30={details.trends.engagementMA30} />
                  </div>
                  <RecentAlerts alerts={details.recentAlerts} />
                </>
              )}
            </div>
            <div className="space-y-4">
              {details && <SeveritySummary counts={details.totals.alerts} />}
              {details && <ProfileDistribution items={details.profiles.distribution} />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}