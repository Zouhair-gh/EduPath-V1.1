import { createContext, useCallback, useContext, useMemo, useState } from 'react';

type Toast = { id: string; title?: string; message: string; type?: 'info' | 'success' | 'warning' | 'error'; timeout?: number };
type Ctx = { toasts: Toast[]; notify: (t: Omit<Toast, 'id'>) => void; remove: (id: string) => void };

const ToastCtx = createContext<Ctx | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const remove = useCallback((id: string) => setToasts((t) => t.filter((x) => x.id !== id)), []);
  const notify = useCallback((t: Omit<Toast, 'id'>) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const toast: Toast = { id, type: 'info', timeout: 4000, ...t };
    setToasts((arr) => [...arr, toast]);
    if (toast.timeout) setTimeout(() => remove(id), toast.timeout);
  }, [remove]);
  const value = useMemo(() => ({ toasts, notify, remove }), [toasts, notify, remove]);
  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((t) => (
          <div key={t.id} className={`rounded shadow px-4 py-3 text-sm text-white ${
            t.type === 'success' ? 'bg-green-600' : t.type === 'warning' ? 'bg-amber-600' : t.type === 'error' ? 'bg-red-600' : 'bg-gray-800'
          }`}>
            {t.title && <div className="font-semibold">{t.title}</div>}
            <div>{t.message}</div>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastCtx);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}