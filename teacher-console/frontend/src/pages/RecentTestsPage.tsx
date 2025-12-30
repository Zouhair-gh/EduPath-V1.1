
import React from 'react';
import RecentTests from '@/components/RecentTests';
import { Sidebar } from '@/components/Layout/Sidebar';

export default function RecentTestsPage() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 p-6">
        <RecentTests />
      </div>
    </div>
  );
}
