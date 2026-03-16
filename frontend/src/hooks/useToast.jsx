import { createContext, useContext, useState, useCallback } from "react";
import { CheckCircle, AlertTriangle, XCircle, Info, X } from "lucide-react";

const ToastContext = createContext(null);

const ICONS = {
  success: CheckCircle,
  error:   XCircle,
  warning: AlertTriangle,
  info:    Info,
};

const COLORS = {
  success: { border: "var(--accent-border)", icon: "var(--accent)",  bg: "var(--accent-dim)"  },
  error:   { border: "rgba(248,113,113,0.25)", icon: "var(--danger)", bg: "var(--danger-dim)"  },
  warning: { border: "rgba(251,191,36,0.25)",  icon: "var(--warning)",bg: "var(--warning-dim)" },
  info:    { border: "rgba(96,165,250,0.25)",  icon: "var(--info)",   bg: "var(--info-dim)"    },
};

function ToastItem({ toast, onRemove }) {
  const Icon = ICONS[toast.type] || Info;
  const colors = COLORS[toast.type] || COLORS.info;

  return (
    <div
      className="toast flex items-start gap-3 px-4 py-3 rounded-lg border shadow-xl"
      style={{
        background: "var(--surface-2)",
        borderColor: colors.border,
        minWidth: 280,
        maxWidth: 380,
      }}
    >
      <Icon size={15} style={{ color: colors.icon, marginTop: 1, flexShrink: 0 }} />
      <span className="text-sm flex-1" style={{ color: "var(--text)" }}>
        {toast.message}
      </span>
      <button
        onClick={() => onRemove(toast.id)}
        className="text-faint hover:text-primary transition-colors"
        style={{ marginTop: 1, flexShrink: 0 }}
      >
        <X size={13} />
      </button>
    </div>
  );
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const remove = useCallback((id) => {
    setToasts((p) => p.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback((message, type = "info", duration = 4000) => {
    const id = Date.now() + Math.random();
    setToasts((p) => [...p, { id, message, type }]);
    if (duration > 0) {
      setTimeout(() => remove(id), duration);
    }
    return id;
  }, [remove]);

  return (
    <ToastContext.Provider value={toast}>
      {children}
      {/* Toast container */}
      <div
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          zIndex: 9999,
          display: "flex",
          flexDirection: "column",
          gap: 8,
          pointerEvents: "none",
        }}
      >
        {toasts.map((t) => (
          <div key={t.id} style={{ pointerEvents: "auto" }}>
            <ToastItem toast={t} onRemove={remove} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used inside ToastProvider");
  return ctx;
};
