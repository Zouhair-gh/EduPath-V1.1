import { api } from '@/services/api';

async function downloadBlob(url: string, filename: string) {
  const res = await api.get(url, { responseType: 'blob' });
  const blob = new Blob([res.data], { type: res.headers['content-type'] || 'text/csv' });
  const link = document.createElement('a');
  const href = URL.createObjectURL(blob);
  link.href = href;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(href);
}

export function useExports() {
  const exportStudents = async (courseId?: number) => {
    const qs = courseId ? `?courseId=${courseId}` : '';
    await downloadBlob(`/export/students${qs}`, `students${courseId ? `-course-${courseId}` : ''}.csv`);
  };
  const exportAlerts = async (courseId?: number) => {
    const qs = courseId ? `?courseId=${courseId}` : '';
    await downloadBlob(`/export/alerts${qs}`, `alerts${courseId ? `-course-${courseId}` : ''}.csv`);
  };
  return { exportStudents, exportAlerts };
}
