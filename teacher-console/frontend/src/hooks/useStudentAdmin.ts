import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';

export function useStudentAdmin(courseId?: number) {
  const qc = useQueryClient();
  const invalidateNotes = (studentId: number | string) => qc.invalidateQueries({ queryKey: ['student-notes', studentId, courseId] });

  const addNote = useMutation({
    mutationFn: async ({ studentId, content }: { studentId: number | string; content: string }) => {
      const { data } = await api.post(`/students/${studentId}/notes`, { content, courseId });
      return data as { status: string };
    },
    onSuccess: (_d, vars) => invalidateNotes(vars.studentId),
  });

  const addTag = useMutation({
    mutationFn: async ({ studentId, tag }: { studentId: number | string; tag: string }) => {
      const { data } = await api.post(`/students/${studentId}/tags`, { tag, courseId });
      return data as { status: string };
    },
  });

  const removeTag = useMutation({
    mutationFn: async ({ studentId, tag }: { studentId: number | string; tag: string }) => {
      const { data } = await api.delete(`/students/${studentId}/tags/${encodeURIComponent(tag)}`, { params: { courseId } });
      return data as { status: string };
    },
  });

  return { addNote, addTag, removeTag };
}
